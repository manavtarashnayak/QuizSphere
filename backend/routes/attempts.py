"""Attempt sessions, answer submissions, grading, history, and leaderboard/analytics routes."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models import Quiz, Question, QuizAttempt, User
from backend.schemas import (
    AttemptStartResponse,
    AttemptSubmitRequest,
    AttemptResultResponse,
    DetailedReviewItem,
    LeaderboardEntry,
    QuizAnalyticsResponse,
)
from backend.services.auth import get_current_user

router = APIRouter()


@router.post("/quizzes/{quiz_id}/start", response_model=AttemptStartResponse)
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

    # Ensure student exists in database
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


@router.post("/attempts/{attempt_id}/submit", response_model=AttemptResultResponse)
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
        # Create attempt record if not pre-started
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

    # Server-side timer validation (duration_minutes + 60s grace period for network latency)
    allowed_max_seconds = (quiz.duration_minutes * 60) + 60
    if payload.time_taken_seconds > allowed_max_seconds:
        # If client reports time far exceeding allowed limit, reject submission
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Time limit expired. The maximum allowed time for this assessment was {quiz.duration_minutes} minutes.",
        )

    # Grade submitted answers
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

    # Update attempt
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


@router.get("/attempts/{attempt_id}/result", response_model=AttemptResultResponse)
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


@router.get("/attempts/history", response_model=List[AttemptResultResponse])
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


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
def get_leaderboard(db: Session = Depends(get_db)):
    """
    Compute and return student rankings based on average percentage score and completed assessments.
    """
    # Group completed attempts by user_id
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


@router.get("/quizzes/{quiz_id}/analytics", response_model=QuizAnalyticsResponse)
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


@router.get("/quizzes/{quiz_id}/results")
def get_quiz_results_for_instructor(quiz_id: str, db: Session = Depends(get_db)):
    """Retrieve all student submissions for a specific quiz (Instructor view)."""
    attempts = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.quiz_id == quiz_id)
        .order_by(QuizAttempt.completed_at.desc())
        .all()
    )
    return attempts
