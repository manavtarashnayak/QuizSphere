"""FastAPI application entry point connecting database, auth, assessments, and analytics routes."""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.database import check_database_connection, engine, SessionLocal, Base
import backend.models
from backend.models import User, Quiz, Question
from backend.services.auth import hash_password
from backend.routes.auth import router as auth_router
from backend.routes.quizzes import router as quizzes_router
from backend.routes.attempts import router as attempts_router
from backend.seed.cbse_questions import SEED_QUIZZES

settings = get_settings()

app = FastAPI(
    title="Quiz Assessment Platform API",
    version="1.1.0",
    description="Backend API for the Quiz Assessment Platform connecting PostgreSQL and HTML/JS frontend.",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def init_db_and_seed_defaults():
    """Create all tables and seed sample data and CBSE + Programming quizzes if not already present."""
    try:
        Base.metadata.create_all(bind=engine)
        db: Session = SessionLocal()
        try:
            # Seed demo users if empty
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

            # Seed demo core quizzes if empty
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

            # Seed CBSE 11th/12th and Basic Programming Quizzes
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

# Register API Routers
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(quizzes_router, prefix="/api/quizzes", tags=["Quizzes"])
app.include_router(attempts_router, prefix="/api", tags=["Attempts & Analytics"])


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
