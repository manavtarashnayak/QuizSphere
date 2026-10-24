"""
QuizSphere data (OFFLINE DEMO MODE)

This file does the same job as js/data.js on the website.
The website saved everything in the browser (localStorage).
This app saves everything in one file instead: quizsphere_data.json,
which sits next to this file. Delete that file to start fresh.

Nothing is sent to a server. Real API calls can be added later,
once the backend teammate shares the endpoints.
"""

import json
import math
import time
from datetime import datetime
from pathlib import Path

SAVE_FILE = Path(__file__).parent / "quizsphere_data.json"

PASS_MARK = 50  # percent needed to pass a quiz

DEMO_USERS = [
    {"email": "student@college.edu", "password": "student123", "role": "student", "name": "Demo Student"},
    {"email": "instructor@college.edu", "password": "instructor123", "role": "instructor", "name": "Demo Instructor"},
]

DEMO_QUIZZES = [
    {
        "id": "gk-101",
        "theme": "gk",
        "title": "General Knowledge",
        "description": "Warm up with questions about the world around you.",
        "minutes": 10,
        "questions": [
            {"text": "What is the capital city of Japan?", "options": ["Seoul", "Tokyo", "Beijing", "Bangkok"], "answer": 1},
            {"text": "Which planet is known as the Red Planet?", "options": ["Venus", "Jupiter", "Mars", "Saturn"], "answer": 2},
            {"text": "How many continents are there on Earth?", "options": ["5", "6", "7", "8"], "answer": 2},
            {"text": "Which is the largest ocean?", "options": ["Atlantic", "Indian", "Arctic", "Pacific"], "answer": 3},
            {"text": "Who painted the Mona Lisa?", "options": ["Leonardo da Vinci", "Pablo Picasso", "Vincent van Gogh", "Claude Monet"], "answer": 0},
        ],
    },
    {
        "id": "math-101",
        "theme": "math",
        "title": "Basic Maths",
        "description": "Quick arithmetic and number sense questions.",
        "minutes": 10,
        "questions": [
            {"text": "What is 12 × 8?", "options": ["86", "96", "108", "92"], "answer": 1},
            {"text": "What is 15% of 200?", "options": ["15", "20", "30", "35"], "answer": 2},
            {"text": "What is the square root of 144?", "options": ["12", "14", "11", "16"], "answer": 0},
            {"text": "Which number is a prime number?", "options": ["21", "27", "29", "33"], "answer": 2},
            {"text": "What is 3/4 written as a decimal?", "options": ["0.34", "0.75", "0.43", "0.70"], "answer": 1},
        ],
    },
    {
        "id": "web-101",
        "theme": "web",
        "title": "Web Basics",
        "description": "HTML, CSS and JavaScript fundamentals for beginners.",
        "minutes": 8,
        "questions": [
            {"text": "What does HTML stand for?", "options": ["HyperText Markup Language", "High Tech Modern Language", "Home Tool Markup Language", "Hyperlink Text Mode Language"], "answer": 0},
            {"text": "Which language is used to style web pages?", "options": ["HTML", "Python", "CSS", "SQL"], "answer": 2},
            {"text": "Which HTML tag makes a link?", "options": ["<link>", "<a>", "<href>", "<url>"], "answer": 1},
            {"text": "Which keyword declares a variable that cannot be reassigned in JavaScript?", "options": ["var", "let", "const", "static"], "answer": 2},
            {"text": "Which CSS property changes text colour?", "options": ["font-color", "text-color", "color", "foreground"], "answer": 2},
        ],
    },
]

# SAMPLE classmates so the leaderboard is not empty in Offline Demo Mode
SAMPLE_CLASSMATES = [
    {"name": "Aarav Mehta", "average": 92, "quizzes": 7},
    {"name": "Sara Khan", "average": 88, "quizzes": 6},
    {"name": "Liam Chen", "average": 81, "quizzes": 5},
    {"name": "Diya Patel", "average": 76, "quizzes": 8},
    {"name": "Noah Fernandes", "average": 69, "quizzes": 4},
    {"name": "Ishita Rao", "average": 63, "quizzes": 5},
    {"name": "Kabir Singh", "average": 55, "quizzes": 3},
]

# Subject names used for tags and filters
TOPIC_NAMES = {"mix": "Mixed", "math": "Maths", "gk": "General Knowledge", "web": "Web & Code"}


def theme_of(quiz):
    """Which subject a quiz belongs to (math, gk, web or mix)."""
    return quiz.get("theme") or {"gk-101": "gk", "math-101": "math", "web-101": "web"}.get(quiz.get("id"), "mix")


# ---------- Reading and writing the save file ----------

def _read_all():
    try:
        return json.loads(SAVE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}  # no file yet, or it was broken: start empty


def load(key, fallback):
    return _read_all().get(key, fallback)


def save(key, value):
    everything = _read_all()
    everything[key] = value
    SAVE_FILE.write_text(json.dumps(everything, indent=2, ensure_ascii=False), encoding="utf-8")


def remove(key):
    everything = _read_all()
    everything.pop(key, None)
    SAVE_FILE.write_text(json.dumps(everything, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------- Quizzes ----------

def get_quizzes():
    return load("quizzes", DEMO_QUIZZES)


def get_quiz(quiz_id):
    return next((q for q in get_quizzes() if q["id"] == quiz_id), None)


def save_quiz(quiz):
    all_quizzes = get_quizzes()
    all_quizzes.append(quiz)
    save("quizzes", all_quizzes)


# ---------- Accounts ----------

def get_users():
    """Demo accounts + accounts made on the Register screen.
    Names changed on the Profile screen are kept in "names" and win over the saved name."""
    names = load("names", {})
    users = []
    for u in DEMO_USERS + load("users", []):
        u = dict(u)
        if u["email"] in names:
            u["name"] = names[u["email"]]
        users.append(u)
    return users


def update_user_name(email, name):
    names = load("names", {})
    names[email] = name
    save("names", names)


def register_user(name, email, password, role):
    email = email.strip().lower()
    if any(u["email"] == email for u in get_users()):
        return False  # email already used
    saved = load("users", [])
    saved.append({"email": email, "password": password, "role": role, "name": name})
    save("users", saved)
    return True


def login(email, password, role):
    email = email.strip().lower()
    user = next((u for u in get_users()
                 if u["email"] == email and u["password"] == password and u["role"] == role), None)
    if user:
        save("current_user", {"email": user["email"], "role": user["role"], "name": user["name"]})
    return user


def logout():
    remove("current_user")


def get_current_user():
    user = load("current_user", None)
    if not user:
        return None
    # Always use the latest account name (e.g. after a name change on Profile)
    account = next((u for u in get_users() if u["email"] == user["email"]), None)
    if account:
        user["name"] = account["name"]
    return user


# ---------- Attempts (one per finished quiz) ----------

def get_all_attempts():
    return load("attempts", [])


def get_attempts(email):
    return [a for a in get_all_attempts() if a["email"] == email]


def save_attempt(attempt):
    all_attempts = get_all_attempts()
    all_attempts.append(attempt)
    save("attempts", all_attempts)


def new_id():
    return str(int(time.time() * 1000))


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def nice_date(iso_text, with_time=False):
    try:
        d = datetime.fromisoformat(iso_text.replace("Z", ""))
    except ValueError:
        return iso_text
    return d.strftime("%d/%m/%Y, %I:%M %p") if with_time else d.strftime("%d/%m/%Y")


def initials(name):
    return "".join(w[0] for w in name.split() if w)[:2].upper() or "?"


# ---------- Achievement badges (worked out from saved attempts) ----------

def _topic_of_attempt(a):
    quiz = get_quiz(a["quizId"])
    return theme_of(quiz) if quiz else "mix"


def best_streak(attempts):
    """Longest run of passed quizzes in a row (oldest to newest)."""
    best = run = 0
    for a in attempts:
        run = run + 1 if a["percent"] >= PASS_MARK else 0
        best = max(best, run)
    return best


def js_round(x):
    """Round like the website did (2.5 -> 3). Python's round() would give 2."""
    return int(math.floor(x + 0.5))


def _average(attempts):
    return sum(a["percent"] for a in attempts) / len(attempts)


BADGES = [
    {"id": "first", "icon": "1st", "name": "First Steps", "desc": "Finish your first quiz.",
     "test": lambda lst: len(lst) >= 1},
    {"id": "perfect", "icon": "100", "name": "Perfectionist", "desc": "Score 100% on any quiz.",
     "test": lambda lst: any(a["percent"] == 100 for a in lst)},
    {"id": "streak", "icon": "×3", "name": "Hat Trick", "desc": "Pass 3 quizzes in a row.",
     "test": lambda lst: best_streak(lst) >= 3},
    {"id": "explorer", "icon": "◎", "name": "Explorer", "desc": "Try Maths, General Knowledge and Web & Code.",
     "test": lambda lst: all(any(_topic_of_attempt(a) == t for a in lst) for t in ("math", "gk", "web"))},
    {"id": "flyer", "icon": "★", "name": "High Flyer", "desc": "Average 80% or more over 3+ quizzes.",
     "test": lambda lst: len(lst) >= 3 and _average(lst) >= 80},
    {"id": "master", "icon": "10", "name": "Quiz Master", "desc": "Complete 10 quizzes.",
     "test": lambda lst: len(lst) >= 10},
]


def unlocked_ids(attempts):
    return [b["id"] for b in BADGES if b["test"](attempts)]


def summarise(attempts):
    """Average score and pass rate for a list of attempts (used by the instructor)."""
    if not attempts:
        return {"average": "–", "passRate": "–"}
    passed = sum(1 for a in attempts if a["percent"] >= PASS_MARK)
    return {"average": f"{js_round(_average(attempts))}%",
            "passRate": f"{js_round(passed / len(attempts) * 100)}%"}
