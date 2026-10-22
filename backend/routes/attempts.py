"""Attempt sessions, answer submissions, grading, and history routes."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Quiz, Question, QuizAttempt, User
from backend.schemas import (
    AttemptStartResponse,
    AttemptSubmitRequest,
    AttemptResultResponse,
    DetailedReviewItem,
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
    Evaluates answers against database, records score, and returns review breakdown.
    """
    quiz = db.query(Quiz).filter(Quiz.id == payload.quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")

    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        # Create attempt record if not pre-started
        user_id = current_user.id if current_user else "u_student_1"
        attempt = QuizAttempt(
            id=attempt_id,
            user_id=user_id,
            quiz_id=quiz.id,
            quiz_title=quiz.title,
            started_at=datetime.now(timezone.utc) - timedelta(seconds=payload.time_taken_seconds),
            total_questions=len(quiz.questions),
        )
        db.add(attempt)

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
    attempt.completed_at = datetime.now(timezone.utc)
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
