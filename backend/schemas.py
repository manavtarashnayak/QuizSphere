"""Pydantic schemas for request validation and response serialization."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ---------------------------------------------------------
# User & Auth Schemas
# ---------------------------------------------------------
class UserRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=6)
    role: str = Field(default="student", pattern="^(student|instructor)$")


class UserLoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str
    role: Optional[str] = "student"


class UserResponse(BaseModel):
    id: str
    full_name: str
    email: str
    role: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ---------------------------------------------------------
# Question Schemas
# ---------------------------------------------------------
class QuestionCreate(BaseModel):
    text: str = Field(..., min_length=3)
    options: List[str] = Field(..., min_length=4, max_length=4)
    correct_option: int = Field(..., ge=0, le=3)
    explanation: Optional[str] = None


class QuestionAttemptResponse(BaseModel):
    """Sanitized question for test-taker (NO correct answers)."""
    id: str
    text: str
    options: List[str]


# ---------------------------------------------------------
# Quiz Schemas
# ---------------------------------------------------------
class QuizCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    category: str = "General"
    difficulty: str = "Intermediate"
    duration_minutes: int = Field(default=15, ge=1, le=180)
    passing_score_percentage: int = Field(default=60, ge=0, le=100)
    questions: List[QuestionCreate] = Field(..., min_length=1)


class QuizUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=1, le=180)
    passing_score_percentage: Optional[int] = Field(None, ge=0, le=100)
    is_published: Optional[bool] = None
    questions: Optional[List[QuestionCreate]] = None


class QuizListItemResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    category: str
    difficulty: str
    duration_minutes: int
    question_count: int
    passing_score_percentage: int
    instructor_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class QuizQuestionsResponse(BaseModel):
    quiz_id: str
    title: str
    duration_minutes: int
    total_questions: int
    questions: List[QuestionAttemptResponse]


# ---------------------------------------------------------
# Attempt & Results Schemas
# ---------------------------------------------------------
class AttemptStartResponse(BaseModel):
    attempt_id: str
    quiz_id: str
    quiz_title: str
    duration_minutes: int
    started_at: datetime
    expires_at: datetime


class AttemptSubmitRequest(BaseModel):
    quiz_id: str
    answers: Dict[str, int]  # {question_id: selected_option_index}
    time_taken_seconds: int = 0


class DetailedReviewItem(BaseModel):
    id: str
    text: str
    options: List[str]
    user_choice: Optional[int]
    correct_choice: int
    is_correct: bool
    explanation: Optional[str] = None


class AttemptResultResponse(BaseModel):
    id: str
    user_id: str
    quiz_id: str
    quiz_title: str
    started_at: datetime
    completed_at: Optional[datetime]
    time_taken_seconds: int
    total_questions: int
    correct_answers: int
    incorrect_answers: int
    unanswered: int
    score: int
    percentage: int
    passed: bool
    detailed_review: Optional[List[DetailedReviewItem]] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------
# Leaderboard & Analytics Schemas
# ---------------------------------------------------------
class LeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    student_name: str
    average_score: float
    quizzes_taken: int
    total_score: int


class QuizAnalyticsResponse(BaseModel):
    quiz_id: str
    quiz_title: str
    total_attempts: int
    average_score: float
    average_percentage: float
    pass_count: int
    fail_count: int
    pass_rate_percentage: float
