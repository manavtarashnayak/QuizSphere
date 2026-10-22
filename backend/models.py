"""Database models for Quiz Assessment Platform."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship

from backend.database import Base


def generate_uuid() -> str:
    """Generate a 36-character UUID string."""
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """Return timezone-aware current UTC datetime."""
    return datetime.now(timezone.utc)


class User(Base):
    """User account model for students and instructors."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    full_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="student")  # 'student' or 'instructor'
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    quizzes = relationship("Quiz", back_populates="instructor", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="student", cascade="all, delete-orphan")


class Quiz(Base):
    """Quiz assessment metadata."""
    __tablename__ = "quizzes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    instructor_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), default="General", index=True, nullable=False)
    difficulty = Column(String(20), default="Intermediate", nullable=False)  # Beginner, Intermediate, Advanced
    duration_minutes = Column(Integer, default=15, nullable=False)
    passing_score_percentage = Column(Integer, default=60, nullable=False)
    is_published = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    instructor = relationship("User", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan", order_by="Question.order_index")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")


class Question(Base):
    """Multiple choice question belonging to a quiz."""
    __tablename__ = "questions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    quiz_id = Column(String(36), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # List of 4 strings: ["A", "B", "C", "D"]
    correct_option = Column(Integer, nullable=False)  # 0-indexed: 0, 1, 2, or 3
    explanation = Column(Text, nullable=True)
    order_index = Column(Integer, default=0, nullable=False)

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")


class QuizAttempt(Base):
    """Student's live assessment attempt and recorded score."""
    __tablename__ = "quiz_attempts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    quiz_id = Column(String(36), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    quiz_title = Column(String(200), nullable=False)
    started_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    time_taken_seconds = Column(Integer, default=0, nullable=False)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, default=0, nullable=False)
    incorrect_answers = Column(Integer, default=0, nullable=False)
    unanswered = Column(Integer, default=0, nullable=False)
    score = Column(Integer, default=0, nullable=False)
    percentage = Column(Integer, default=0, nullable=False)
    passed = Column(Boolean, default=False, nullable=False)
    submitted_answers = Column(JSON, nullable=True)  # {"q_id_1": 2, "q_id_2": 0}

    # Relationships
    student = relationship("User", back_populates="attempts")
    quiz = relationship("Quiz", back_populates="attempts")