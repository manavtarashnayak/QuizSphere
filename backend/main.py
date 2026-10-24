"""
FastAPI application entry point connecting database, auth, assessments, and analytics routes.
All endpoints are consolidated directly in this file for clear visibility and easy teammate reference.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.config import get_settings
from backend.database import check_database_connection, engine, SessionLocal, Base, get_db
import backend.models
from backend.models import User, Quiz, Question, QuizAttempt
from backend.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
    QuizCreate,
    QuizUpdateRequest,
    QuizListItemResponse,
    QuizQuestionsResponse,
    QuestionAttemptResponse,
    AttemptStartResponse,
    AttemptSubmitRequest,
    AttemptResultResponse,
    DetailedReviewItem,
    LeaderboardEntry,
    QuizAnalyticsResponse,
)
from backend.services.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)
from backend.seed.cbse_questions import SEED_QUIZZES

settings = get_settings()

app = FastAPI(
    title="Quiz Assessment Platform API",
    version="1.2.0",
    description="Consolidated Backend API for Quiz Assessment Platform connecting PostgreSQL and Frontend.",
)

# -----------------------------------------------------------------------------
# CORS Configuration
# -----------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# Database Startup & Seeding
# -----------------------------------------------------------------------------
def init_db_and_seed_defaults():
    """Create all tables and seed sample data + CBSE and Programming questions if not present."""
    try:
        Base.metadata.create_all(bind=engine)
        db: Session = SessionLocal()
        try:
            # 1. Seed demo users
            if not db.query(User).first():
                student = User(
                    id="u_student_1",
                    full_name="Alex Johnson",
                    email="student@college.edu",
                    hashed_password=hash_password("student123"),
                    role="student",
                )
                instructor = User(
                    id="u_instructor_1",
                    full_name="Prof. Sarah Miller",
                    email="instructor@college.edu",
                    hashed_password=hash_password("instructor123"),
                    role="instructor",
                )
                db.add_all([student, instructor])
                db.commit()

            # 2. Seed DSA assessment
            if not db.query(Quiz).filter(Quiz.id == "q_1").first():
                quiz1 = Quiz(
                    id="q_1",
                    instructor_id="u_instructor_1",
                    title="Data Structures & Algorithms Assessment",
                    description="Test your fundamental knowledge of trees, graphs, sorting algorithms, and complexity analysis.",
                    category="Computer Science",
                    difficulty="Intermediate",
                    duration_minutes=15,
                    passing_score_percentage=60,
                )
                db.add(quiz1)
                db.commit()

                db.add_all([
                    Question(
                        id="q1_1",
                        quiz_id="q_1",
                        question_text="What is the worst-case time complexity of QuickSort?",
                        options=["O(n log n)", "O(n²)", "O(log n)", "O(n)"],
                        correct_option=1,
                        explanation="In the worst case when the pivot is always the extreme element, QuickSort degrades to O(n²).",
                        order_index=1,
                    ),
                    Question(
                        id="q1_2",
                        quiz_id="q_1",
                        question_text="Which data structure follows the LIFO (Last In, First Out) principle?",
                        options=["Queue", "Priority Queue", "Stack", "Binary Search Tree"],
                        correct_option=2,
                        explanation="A Stack follows the Last In First Out order for insertions and deletions.",
                        order_index=2,
                    ),
                    Question(
                        id="q1_3",
                        quiz_id="q_1",
                        question_text="What is the average search complexity in a balanced Binary Search Tree?",
                        options=["O(1)", "O(log n)", "O(n)", "O(n log n)"],
                        correct_option=1,
                        explanation="In a balanced BST, tree height is log(n), making search operations O(log n).",
                        order_index=3,
                    ),
                    Question(
                        id="q1_4",
                        quiz_id="q_1",
                        question_text="Which algorithm finds the shortest path in a graph with non-negative edge weights?",
                        options=["Dijkstra's Algorithm", "Kruskal's Algorithm", "Prim's Algorithm", "DFS"],
                        correct_option=0,
                        explanation="Dijkstra's algorithm efficiently computes single-source shortest paths with non-negative weights.",
                        order_index=4,
                    ),
                ])
                db.commit()

            # 3. Seed CBSE & Programming question banks
            instructor_id = "u_instructor_1"
            for q_data in SEED_QUIZZES:
                existing_quiz = db.query(Quiz).filter(Quiz.id == q_data["id"]).first()
                if not existing_quiz:
                    new_quiz = Quiz(
                        id=q_data["id"],
                        instructor_id=instructor_id,
                        title=q_data["title"],
                        description=q_data["description"],
                        category=q_data["category"],
                        difficulty=q_data["difficulty"],
                        duration_minutes=q_data["duration_minutes"],
                        passing_score_percentage=q_data["passing_score_percentage"],
                    )
                    db.add(new_quiz)
                    db.commit()

                    for idx, question_item in enumerate(q_data["questions"], start=1):
                        new_question = Question(
                            id=question_item["id"],
                            quiz_id=new_quiz.id,
                            question_text=question_item["text"],
                            options=question_item["options"],
                            correct_option=question_item["correct_option"],
                            explanation=question_item.get("explanation"),
                            order_index=idx,
                        )
                        db.add(new_question)
                    db.commit()

        finally:
            db.close()
    except Exception as e:
        print("Note: Database init warning:", e)


# Run startup database init
init_db_and_seed_defaults()


# =============================================================================
# 1. HEALTH CHECK ENDPOINT
# =============================================================================
@app.get("/api/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Confirm that the API and its configured database are available."""
    try:
        check_database_connection()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is unavailable.",
        ) from error
    return {"status": "ok", "database": "connected"}


# =============================================================================
# 2. AUTHENTICATION ENDPOINTS (/api/auth)
# =============================================================================
@app.post("/api/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, tags=["Auth"])
def register(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    """Register a new student or instructor account."""
    existing_user = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    user = User(
        full_name=payload.full_name,
        email=payload.email.lower(),
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": user.id, "email": user.email, "role": user.role})
    return TokenResponse(access_token=token, token_type="bearer", user=UserResponse.model_validate(user))


@app.post("/api/auth/login", response_model=TokenResponse, tags=["Auth"])
def login(payload: UserLoginRequest, db: Session = Depends(get_db)):
    """Authenticate user credentials and issue a JWT token."""
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = create_access_token(data={"sub": user.id, "email": user.email, "role": user.role})
    return TokenResponse(access_token=token, token_type="bearer", user=UserResponse.model_validate(user))


@app.get("/api/auth/me", response_model=UserResponse, tags=["Auth"])
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Fetch profile data for the authenticated user session."""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return current_user


# =============================================================================
# 3. QUIZZES MANAGEMENT ENDPOINTS (/api/quizzes)
# =============================================================================
@app.get("/api/quizzes", response_model=List[QuizListItemResponse], tags=["Quizzes"])
def get_all_quizzes(db: Session = Depends(get_db)):
    """Fetch all published assessments for catalog and dashboard."""
    quizzes = db.query(Quiz).filter(Quiz.is_published == True).order_by(Quiz.created_at.desc()).all()
    results = []
    for q in quizzes:
        results.append(
            QuizListItemResponse(
                id=q.id,
                title=q.title,
                description=q.description,
                category=q.category,
                difficulty=q.difficulty,
                duration_minutes=q.duration_minutes,
                question_count=len(q.questions),
                passing_score_percentage=q.passing_score_percentage,
                instructor_name=q.instructor.full_name if q.instructor else "Instructor",
                created_at=q.created_at,
            )
        )
    return results


@app.get("/api/quizzes/{quiz_id}", response_model=QuizListItemResponse, tags=["Quizzes"])
def get_quiz_by_id(quiz_id: str, db: Session = Depends(get_db)):
    """Fetch metadata of a single quiz by ID."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found.",
        )
    return QuizListItemResponse(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        category=quiz.category,
        difficulty=quiz.difficulty,
        duration_minutes=quiz.duration_minutes,
        question_count=len(quiz.questions),
        passing_score_percentage=quiz.passing_score_percentage,
        instructor_name=quiz.instructor.full_name if quiz.instructor else "Instructor",
        created_at=quiz.created_at,
    )


@app.post("/api/quizzes", status_code=status.HTTP_201_CREATED, tags=["Quizzes"])
def create_quiz(
    payload: QuizCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new quiz with questions (Instructor action)."""
    instructor_id = current_user.id if current_user else "u_instructor_1"

    inst = db.query(User).filter(User.id == instructor_id).first()
    if not inst:
        inst = User(
            id=instructor_id,
            full_name="Prof. Sarah Miller",
            email="instructor@college.edu",
            hashed_password="demo",
            role="instructor",
        )
        db.add(inst)
        db.commit()

    quiz = Quiz(
        title=payload.title,
        description=payload.description,
        category=payload.category,
        difficulty=payload.difficulty,
        duration_minutes=payload.duration_minutes,
        passing_score_percentage=payload.passing_score_percentage,
        instructor_id=instructor_id,
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    for idx, q_data in enumerate(payload.questions):
        q = Question(
            quiz_id=quiz.id,
            question_text=q_data.text,
            options=q_data.options,
            correct_option=q_data.correct_option,
            explanation=q_data.explanation,
            order_index=idx,
        )
        db.add(q)

    db.commit()
    db.refresh(quiz)

    return {
        "id": quiz.id,
        "title": quiz.title,
        "question_count": len(quiz.questions),
        "duration_minutes": quiz.duration_minutes,
        "message": "Quiz created successfully",
    }


@app.put("/api/quizzes/{quiz_id}", tags=["Quizzes"])
def update_quiz(
    quiz_id: str,
    payload: QuizUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update quiz metadata or replace questions."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found.",
        )

    if payload.title is not None:
        quiz.title = payload.title
    if payload.description is not None:
        quiz.description = payload.description
    if payload.category is not None:
        quiz.category = payload.category
    if payload.difficulty is not None:
        quiz.difficulty = payload.difficulty
    if payload.duration_minutes is not None:
        quiz.duration_minutes = payload.duration_minutes
    if payload.passing_score_percentage is not None:
        quiz.passing_score_percentage = payload.passing_score_percentage
    if payload.is_published is not None:
        quiz.is_published = payload.is_published

    if payload.questions is not None:
        db.query(Question).filter(Question.quiz_id == quiz.id).delete()
        for idx, q_data in enumerate(payload.questions):
            q = Question(
                quiz_id=quiz.id,
                question_text=q_data.text,
                options=q_data.options,
                correct_option=q_data.correct_option,
                explanation=q_data.explanation,
                order_index=idx,
            )
            db.add(q)

    db.commit()
    db.refresh(quiz)

    return {
        "id": quiz.id,
        "title": quiz.title,
        "question_count": len(quiz.questions),
        "duration_minutes": quiz.duration_minutes,
        "message": "Quiz updated successfully",
    }


@app.get("/api/quizzes/{quiz_id}/questions", response_model=QuizQuestionsResponse, tags=["Quizzes"])
def get_quiz_questions_for_attempt(quiz_id: str, db: Session = Depends(get_db)):
    """
    Retrieve sanitized question set for student taking the exam.
    SECURITY: Correct answers and explanations are never sent in this payload!
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz assessment not found.",
        )

    sanitized_questions = [
        QuestionAttemptResponse(
            id=q.id,
            text=q.question_text,
            options=q.options,
        )
        for q in quiz.questions
    ]

    return QuizQuestionsResponse(
        quiz_id=quiz.id,
        title=quiz.title,
        duration_minutes=quiz.duration_minutes,
        total_questions=len(sanitized_questions),
        questions=sanitized_questions,
    )


@app.delete("/api/quizzes/{quiz_id}", tags=["Quizzes"])
def delete_quiz(quiz_id: str, db: Session = Depends(get_db)):
    """Delete a quiz assessment and all related records."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz assessment not found.",
        )

    db.delete(quiz)
    db.commit()
    return {"success": True, "message": "Quiz deleted successfully."}


# =============================================================================
# 4. EXAM ATTEMPTS, GRADING & SESSIONS ENDPOINTS
# =============================================================================
@app.post("/api/quizzes/{quiz_id}/start", response_model=AttemptStartResponse, tags=["Attempts"])
def start_quiz_attempt(
    quiz_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start a new exam session and initialize the attempt record."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")

    user_id = current_user.id if current_user else "u_student_1"

    student = db.query(User).filter(User.id == user_id).first()
    if not student:
        student = User(
            id=user_id,
            full_name="Alex Johnson",
            email="student@college.edu",
            hashed_password="demo",
            role="student",
        )
        db.add(student)
        db.commit()

    started_at = datetime.now(timezone.utc)
    expires_at = started_at + timedelta(minutes=quiz.duration_minutes)

    attempt = QuizAttempt(
        id=f"att_{uuid.uuid4().hex[:12]}",
        user_id=user_id,
        quiz_id=quiz.id,
        quiz_title=quiz.title,
        started_at=started_at,
        total_questions=len(quiz.questions),
    )
    db.add(attempt)
    db.commit()

    return AttemptStartResponse(
        attempt_id=attempt.id,
        quiz_id=quiz.id,
        quiz_title=quiz.title,
        duration_minutes=quiz.duration_minutes,
        started_at=started_at,
        expires_at=expires_at,
    )


@app.post("/api/attempts/{attempt_id}/submit", response_model=AttemptResultResponse, tags=["Attempts"])
def submit_quiz_attempt(
    attempt_id: str,
    payload: AttemptSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Authoritative Server-side Grading:
    Evaluates answers against database, validates time-limit grace period, records score, and returns review breakdown.
    """
    quiz = db.query(Quiz).filter(Quiz.id == payload.quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")

    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    now_utc = datetime.now(timezone.utc)

    if not attempt:
        user_id = current_user.id if current_user else "u_student_1"
        attempt = QuizAttempt(
            id=attempt_id,
            user_id=user_id,
            quiz_id=quiz.id,
            quiz_title=quiz.title,
            started_at=now_utc - timedelta(seconds=payload.time_taken_seconds),
            total_questions=len(quiz.questions),
        )
        db.add(attempt)

    # Server-side timer validation (duration_minutes + 60s grace period for latency)
    allowed_max_seconds = (quiz.duration_minutes * 60) + 60
    if payload.time_taken_seconds > allowed_max_seconds:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Time limit expired. The maximum allowed time for this assessment was {quiz.duration_minutes} minutes.",
        )

    correct_count = 0
    incorrect_count = 0
    unanswered_count = 0
    detailed_review = []

    for q in quiz.questions:
        user_choice = payload.answers.get(q.id)
        is_answered = user_choice is not None
        is_correct = is_answered and user_choice == q.correct_option

        if not is_answered:
            unanswered_count += 1
        elif is_correct:
            correct_count += 1
        else:
            incorrect_count += 1

        detailed_review.append(
            DetailedReviewItem(
                id=q.id,
                text=q.question_text,
                options=q.options,
                user_choice=user_choice if is_answered else None,
                correct_choice=q.correct_option,
                is_correct=is_correct,
                explanation=q.explanation,
            )
        )

    total_questions = len(quiz.questions) or 1
    percentage = round((correct_count / total_questions) * 100)
    passed = percentage >= quiz.passing_score_percentage

    attempt.completed_at = now_utc
    attempt.time_taken_seconds = payload.time_taken_seconds
    attempt.total_questions = total_questions
    attempt.correct_answers = correct_count
    attempt.incorrect_answers = incorrect_count
    attempt.unanswered = unanswered_count
    attempt.score = correct_count
    attempt.percentage = percentage
    attempt.passed = passed
    attempt.submitted_answers = payload.answers

    db.commit()
    db.refresh(attempt)

    return AttemptResultResponse(
        id=attempt.id,
        user_id=attempt.user_id,
        quiz_id=attempt.quiz_id,
        quiz_title=attempt.quiz_title,
        started_at=attempt.started_at,
        completed_at=attempt.completed_at,
        time_taken_seconds=attempt.time_taken_seconds,
        total_questions=attempt.total_questions,
        correct_answers=attempt.correct_answers,
        incorrect_answers=attempt.incorrect_answers,
        unanswered=attempt.unanswered,
        score=attempt.score,
        percentage=attempt.percentage,
        passed=attempt.passed,
        detailed_review=detailed_review,
    )


@app.get("/api/attempts/{attempt_id}/result", response_model=AttemptResultResponse, tags=["Attempts"])
def get_attempt_result(attempt_id: str, db: Session = Depends(get_db)):
    """Fetch evaluated attempt result and detailed question review."""
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt result not found.")

    quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
    detailed_review = []
    if quiz:
        user_answers = attempt.submitted_answers or {}
        for q in quiz.questions:
            user_choice = user_answers.get(q.id)
            is_answered = user_choice is not None
            is_correct = is_answered and user_choice == q.correct_option

            detailed_review.append(
                DetailedReviewItem(
                    id=q.id,
                    text=q.question_text,
                    options=q.options,
                    user_choice=user_choice if is_answered else None,
                    correct_choice=q.correct_option,
                    is_correct=is_correct,
                    explanation=q.explanation,
                )
            )

    return AttemptResultResponse(
        id=attempt.id,
        user_id=attempt.user_id,
        quiz_id=attempt.quiz_id,
        quiz_title=attempt.quiz_title,
        started_at=attempt.started_at,
        completed_at=attempt.completed_at,
        time_taken_seconds=attempt.time_taken_seconds,
        total_questions=attempt.total_questions,
        correct_answers=attempt.correct_answers,
        incorrect_answers=attempt.incorrect_answers,
        unanswered=attempt.unanswered,
        score=attempt.score,
        percentage=attempt.percentage,
        passed=attempt.passed,
        detailed_review=detailed_review,
    )


@app.get("/api/attempts/history", response_model=List[AttemptResultResponse], tags=["Attempts"])
def get_attempt_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all past attempts for the current logged-in student."""
    user_id = current_user.id if current_user else "u_student_1"
    attempts = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.user_id == user_id)
        .order_by(QuizAttempt.started_at.desc())
        .all()
    )
    return attempts


# =============================================================================
# 5. LEADERBOARD & QUIZ ANALYTICS ENDPOINTS
# =============================================================================
@app.get("/api/leaderboard", response_model=List[LeaderboardEntry], tags=["Leaderboard & Analytics"])
def get_leaderboard(db: Session = Depends(get_db)):
    """Compute and return student rankings based on average percentage score and completed assessments."""
    stats = (
        db.query(
            QuizAttempt.user_id,
            func.count(QuizAttempt.id).label("quizzes_taken"),
            func.avg(QuizAttempt.percentage).label("avg_score"),
            func.sum(QuizAttempt.score).label("total_score"),
        )
        .filter(QuizAttempt.completed_at != None)
        .group_by(QuizAttempt.user_id)
        .order_by(func.avg(QuizAttempt.percentage).desc())
        .limit(20)
        .all()
    )

    results = []
    for rank, item in enumerate(stats, start=1):
        user = db.query(User).filter(User.id == item.user_id).first()
        results.append(
            LeaderboardEntry(
                rank=rank,
                user_id=item.user_id,
                student_name=user.full_name if user else f"Student ({item.user_id[:6]})",
                average_score=round(float(item.avg_score or 0), 1),
                quizzes_taken=item.quizzes_taken,
                total_score=int(item.total_score or 0),
            )
        )
    return results


@app.get("/api/quizzes/{quiz_id}/analytics", response_model=QuizAnalyticsResponse, tags=["Leaderboard & Analytics"])
def get_quiz_analytics(quiz_id: str, db: Session = Depends(get_db)):
    """Compute aggregate analytics for a given assessment."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")

    completed_attempts = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.quiz_id == quiz_id, QuizAttempt.completed_at != None)
        .all()
    )

    total_attempts = len(completed_attempts)
    if total_attempts == 0:
        return QuizAnalyticsResponse(
            quiz_id=quiz.id,
            quiz_title=quiz.title,
            total_attempts=0,
            average_score=0.0,
            average_percentage=0.0,
            pass_count=0,
            fail_count=0,
            pass_rate_percentage=0.0,
        )

    pass_count = sum(1 for a in completed_attempts if a.passed)
    fail_count = total_attempts - pass_count
    avg_score = sum(a.score for a in completed_attempts) / total_attempts
    avg_percentage = sum(a.percentage for a in completed_attempts) / total_attempts
    pass_rate = (pass_count / total_attempts) * 100

    return QuizAnalyticsResponse(
        quiz_id=quiz.id,
        quiz_title=quiz.title,
        total_attempts=total_attempts,
        average_score=round(avg_score, 1),
        average_percentage=round(avg_percentage, 1),
        pass_count=pass_count,
        fail_count=fail_count,
        pass_rate_percentage=round(pass_rate, 1),
    )


@app.get("/api/quizzes/{quiz_id}/results", tags=["Leaderboard & Analytics"])
def get_quiz_results_for_instructor(quiz_id: str, db: Session = Depends(get_db)):
    """Retrieve all student submissions for a specific quiz (Instructor view)."""
    attempts = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.quiz_id == quiz_id)
        .order_by(QuizAttempt.completed_at.desc())
        .all()
    )
    return attempts
