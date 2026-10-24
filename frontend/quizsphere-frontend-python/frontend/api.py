"""
Bridge connecting the Python Tkinter frontend directly to the FastAPI/PostgreSQL backend API.
Falls back safely to local quizsphere_data.json if backend server is not running.
"""

import json
import urllib.request
import urllib.error
import uuid
from typing import Optional, Dict, Any, List

API_BASE_URL = "http://127.0.0.1:8000/api"
_AUTH_TOKEN: Optional[str] = None


def is_backend_online() -> bool:
    """Check if the FastAPI backend server is alive."""
    try:
        req = urllib.request.Request(f"{API_BASE_URL}/health", headers={"User-Agent": "QuizSphere-Tkinter"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("status") == "ok"
    except Exception:
        pass
    return False


def login(email: str, password: str, role: str) -> Optional[Dict[str, Any]]:
    """Log in against the backend API, storing the JWT bearer token."""
    global _AUTH_TOKEN
    try:
        payload = json.dumps({"email": email, "password": password, "role": role}).encode("utf-8")
        req = urllib.request.Request(
            f"{API_BASE_URL}/auth/login",
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "QuizSphere-Tkinter"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            if resp.status == 200:
                res_data = json.loads(resp.read().decode("utf-8"))
                _AUTH_TOKEN = res_data.get("access_token")
                user = res_data.get("user", {})
                return {
                    "id": user.get("id"),
                    "email": user.get("email"),
                    "name": user.get("full_name"),
                    "role": user.get("role")
                }
    except Exception as e:
        print("[Backend API] Login fallback to offline:", e)
    return None


def register(name: str, email: str, password: str, role: str) -> Optional[Dict[str, Any]]:
    """Register a new student or instructor against the backend."""
    global _AUTH_TOKEN
    try:
        payload = json.dumps({
            "full_name": name,
            "email": email,
            "password": password,
            "role": role
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{API_BASE_URL}/auth/register",
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "QuizSphere-Tkinter"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            if resp.status in (200, 201):
                res_data = json.loads(resp.read().decode("utf-8"))
                _AUTH_TOKEN = res_data.get("access_token")
                user = res_data.get("user", {})
                return {
                    "id": user.get("id"),
                    "email": user.get("email"),
                    "name": user.get("full_name"),
                    "role": user.get("role")
                }
    except Exception as e:
        print("[Backend API] Register fallback to offline:", e)
    return None


def fetch_quizzes() -> Optional[List[Dict[str, Any]]]:
    """Fetch all published assessments from PostgreSQL."""
    try:
        req = urllib.request.Request(f"{API_BASE_URL}/quizzes", headers={"User-Agent": "QuizSphere-Tkinter"})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            if resp.status == 200:
                quizzes = json.loads(resp.read().decode("utf-8"))
                return quizzes
    except Exception as e:
        print("[Backend API] Fetch quizzes fallback to offline:", e)
    return None


def start_quiz(quiz_id: str) -> Optional[Dict[str, Any]]:
    """Start an exam session on the backend and get an attempt_id."""
    try:
        headers = {"User-Agent": "QuizSphere-Tkinter"}
        if _AUTH_TOKEN:
            headers["Authorization"] = f"Bearer {_AUTH_TOKEN}"
        req = urllib.request.Request(f"{API_BASE_URL}/quizzes/{quiz_id}/start", headers=headers, data=b"", method="POST")
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print("[Backend API] Start quiz fallback to offline:", e)
    return None


def fetch_quiz_questions(quiz_id: str) -> Optional[List[Dict[str, Any]]]:
    """Fetch sanitized questions for taking an exam."""
    try:
        req = urllib.request.Request(f"{API_BASE_URL}/quizzes/{quiz_id}/questions", headers={"User-Agent": "QuizSphere-Tkinter"})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("questions", [])
    except Exception as e:
        print("[Backend API] Fetch questions fallback to offline:", e)
    return None


def submit_attempt(quiz_id: str, answers: Dict[str, int], time_taken_seconds: int, attempt_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Submit exam answers to the backend for authoritative server-side grading."""
    try:
        headers = {"Content-Type": "application/json", "User-Agent": "QuizSphere-Tkinter"}
        if _AUTH_TOKEN:
            headers["Authorization"] = f"Bearer {_AUTH_TOKEN}"

        att_id = attempt_id or f"att_{uuid.uuid4().hex[:12]}"
        payload = json.dumps({
            "quiz_id": quiz_id,
            "answers": answers,
            "time_taken_seconds": max(0, int(time_taken_seconds))
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{API_BASE_URL}/attempts/{att_id}/submit",
            data=payload,
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print("[Backend API] Submit attempt fallback to offline:", e)
    return None


def create_quiz(title: str, description: str, category: str, minutes: int, questions: List[Dict[str, Any]]) -> bool:
    """Create a new quiz in PostgreSQL as an instructor."""
    try:
        headers = {"Content-Type": "application/json", "User-Agent": "QuizSphere-Tkinter"}
        if _AUTH_TOKEN:
            headers["Authorization"] = f"Bearer {_AUTH_TOKEN}"

        backend_questions = [
            {
                "text": q["text"],
                "options": q["options"],
                "correct_option": q["answer"],
                "explanation": q.get("explanation", "")
            }
            for q in questions
        ]

        payload = json.dumps({
            "title": title,
            "description": description,
            "category": category,
            "difficulty": "Intermediate",
            "duration_minutes": minutes,
            "passing_score_percentage": 50,
            "questions": backend_questions
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{API_BASE_URL}/quizzes",
            data=payload,
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=4.0) as resp:
            return resp.status in (200, 201)
    except Exception as e:
        print("[Backend API] Create quiz fallback to offline:", e)
    return False


def fetch_leaderboard() -> Optional[List[Dict[str, Any]]]:
    """Fetch live student leaderboard from PostgreSQL."""
    try:
        req = urllib.request.Request(f"{API_BASE_URL}/leaderboard", headers={"User-Agent": "QuizSphere-Tkinter"})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print("[Backend API] Fetch leaderboard fallback to offline:", e)
    return None


def fetch_attempt_history() -> Optional[List[Dict[str, Any]]]:
    """Fetch all completed attempts for the authenticated student."""
    try:
        headers = {"User-Agent": "QuizSphere-Tkinter"}
        if _AUTH_TOKEN:
            headers["Authorization"] = f"Bearer {_AUTH_TOKEN}"
        req = urllib.request.Request(f"{API_BASE_URL}/attempts/history", headers=headers)
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print("[Backend API] Fetch attempt history fallback to offline:", e)
    return None
