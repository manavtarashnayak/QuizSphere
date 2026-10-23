"""Quiz assessment management, retrieval, update, and deletion routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Quiz, Question, User
from backend.schemas import (
    QuizCreate,
    QuizUpdateRequest,
    QuizListItemResponse,
    QuizQuestionsResponse,
    QuestionAttemptResponse,
)
from backend.services.auth import get_current_user

router = APIRouter()


@router.get("", response_model=List[QuizListItemResponse])
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


@router.get("/{quiz_id}", response_model=QuizListItemResponse)
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


@router.post("", status_code=status.HTTP_201_CREATED)
def create_quiz(
    payload: QuizCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new quiz with questions (Instructor action)."""
    instructor_id = current_user.id if current_user else "u_instructor_1"

    # Ensure instructor exists
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

    # Insert Questions
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


@router.put("/{quiz_id}")
def update_quiz(
    quiz_id: str,
    payload: QuizUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing quiz assessment details and optional replacement of question list.
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found.",
        )

    # Update basic metadata fields if provided
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

    # Replace questions if new question set is provided
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


@router.get("/{quiz_id}/questions", response_model=QuizQuestionsResponse)
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


@router.delete("/{quiz_id}")
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
