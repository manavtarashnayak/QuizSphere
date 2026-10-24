"""
QuizSphere data (OFFLINE DEMO MODE)

This file does the same job as js/data.js on the website.
The website saved everything in the browser (localStorage).
This app saves everything in one file instead: quizsphere_data.json,
which sits next to this file. Delete that file to start fresh.

Synchronizes seamlessly with FastAPI/PostgreSQL backend when online.
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
        "id": "cbse-phys-11-12",
        "theme": "phys",
        "category": "Physics",
        "title": "CBSE Physics (Classes 11 & 12)",
        "description": "Fundamental concepts from CBSE Class 11 & 12 Physics: Mechanics, Thermodynamics, Electrostatics, and Optics.",
        "minutes": 20,
        "questions": [
            {"id": "phys_1", "text": "What is the dimensional formula of Universal Gravitational Constant (G)?", "options": ["[M⁻¹ L³ T⁻²]", "[M¹ L² T⁻²]", "[M⁻¹ L² T⁻¹]", "[M⁰ L³ T⁻²]"], "answer": 0, "explanation": "From F = G*m1*m2/r², G = F*r²/(m1*m2) -> [M⁻¹ L³ T⁻²]."},
            {"id": "phys_2", "text": "In projectile motion under gravity (ignoring air resistance), which component of velocity remains constant?", "options": ["Vertical component", "Horizontal component", "Both vertical and horizontal", "Neither"], "answer": 1, "explanation": "No external force acts along horizontal axis, so horizontal velocity is constant."},
            {"id": "phys_3", "text": "According to the First Law of Thermodynamics, ΔQ is equal to:", "options": ["ΔU - W", "ΔU + W", "W - ΔU", "ΔU * W"], "answer": 1, "explanation": "ΔQ = ΔU + ΔW (heat supplied = increase in internal energy + work done)."},
            {"id": "phys_4", "text": "What is the electric field inside a charged thin spherical conducting shell of radius R?", "options": ["Zero", "q / (4πε₀ R²)", "q / (4πε₀ r)", "Infinite"], "answer": 0, "explanation": "By Gauss's Law, enclosed charge inside a hollow conducting shell is zero, so E = 0."},
            {"id": "phys_5", "text": "Which phenomenon demonstrates the transverse wave nature of light?", "options": ["Interference", "Diffraction", "Polarization", "Refraction"], "answer": 2, "explanation": "Polarization can only occur in transverse waves."},
            {"id": "phys_6", "text": "The SI unit of magnetic flux is:", "options": ["Tesla", "Weber", "Henry", "Gauss"], "answer": 1, "explanation": "Magnetic flux is measured in Weber (Wb); flux density (B) is in Tesla (T)."},
            {"id": "phys_7", "text": "In Young's Double Slit Experiment, what happens to fringe width if distance between slits is halved?", "options": ["Halved", "Doubled", "Remains unchanged", "Quadrupled"], "answer": 1, "explanation": "Fringe width β = λD/d. If slit separation d is halved, β doubles."},
            {"id": "phys_8", "text": "What is the de Broglie wavelength of an electron accelerated through potential difference V?", "options": ["12.27 / √V Å", "1.227 / √V Å", "122.7 / √V Å", "0.1227 / √V Å"], "answer": 0, "explanation": "For an electron, λ = h/√(2meV) ≈ 12.27 / √V Å."}
        ],
    },
    {
        "id": "cbse-chem-11-12",
        "theme": "chem",
        "category": "Chemistry",
        "title": "CBSE Chemistry (Classes 11 & 12)",
        "description": "Essential questions covering Physical, Organic, and Inorganic Chemistry from CBSE 11th & 12th curriculum.",
        "minutes": 20,
        "questions": [
            {"id": "chem_1", "text": "Which orbital has zero angular nodes?", "options": ["p orbital", "s orbital", "d orbital", "f orbital"], "answer": 1, "explanation": "Angular nodes = azimuthal quantum number l. For s orbital l = 0, so 0 angular nodes."},
            {"id": "chem_2", "text": "What is the shape of Xenon tetrafluoride (XeF4) molecule according to VSEPR theory?", "options": ["Tetrahedral", "Square Planar", "See-saw", "Octahedral"], "answer": 1, "explanation": "Xe has 8 valence electrons, 4 bond pairs and 2 lone pairs -> sp3d2 geometry, square planar shape."},
            {"id": "chem_3", "text": "The unit of rate constant for a first-order chemical reaction is:", "options": ["mol L⁻¹ s⁻¹", "L mol⁻¹ s⁻¹", "s⁻¹", "mol² L⁻² s⁻¹"], "answer": 2, "explanation": "For nth order: (mol/L)^(1-n) * s⁻¹. When n=1, unit is s⁻¹."},
            {"id": "chem_4", "text": "Which element exhibits highest oxidation state in 3d transition metal series?", "options": ["Chromium", "Manganese", "Iron", "Titanium"], "answer": 1, "explanation": "Manganese (Mn) exhibits +7 oxidation state in KMnO4 due to 3d5 4s2 electrons."},
            {"id": "chem_5", "text": "Which reagent is used in Lucas Test to distinguish primary, secondary, and tertiary alcohols?", "options": ["Anhydrous ZnCl2 + conc. HCl", "Dilute H2SO4", "Bromine water", "Alkaline KMnO4"], "answer": 0, "explanation": "Lucas reagent is an equimolar mixture of anhydrous ZnCl2 and concentrated HCl."},
            {"id": "chem_6", "text": "The monomer units of Nylon-6,6 are:", "options": ["Adipic acid and Hexamethylenediamine", "Terephthalic acid and Ethylene glycol", "Caprolactam", "Phenol and Formaldehyde"], "answer": 0, "explanation": "Nylon-6,6 is synthesized by condensation polymerization of adipic acid and hexamethylenediamine."},
            {"id": "chem_7", "text": "In Cannizzaro reaction, aldehydes that undergo self oxidation and reduction must have:", "options": ["At least one α-hydrogen", "No α-hydrogen atoms", "At least two α-hydrogens", "An acidic hydroxyl group"], "answer": 1, "explanation": "Only aldehydes without α-hydrogens (e.g. formaldehyde, benzaldehyde) undergo Cannizzaro reaction."}
        ],
    },
    {
        "id": "cbse-math-11-12",
        "theme": "math",
        "category": "Mathematics",
        "title": "CBSE Mathematics (Classes 11 & 12)",
        "description": "Calculus, Linear Algebra, Probability, and Coordinate Geometry for 11th & 12th standards.",
        "minutes": 20,
        "questions": [
            {"id": "math_1", "text": "What is the derivative of e^(sin x) with respect to x?", "options": ["cos(x) * e^(sin x)", "-cos(x) * e^(sin x)", "sin(x) * e^(cos x)", "e^(cos x)"], "answer": 0, "explanation": "By chain rule: d/dx[e^(sin x)] = e^(sin x) * d/dx(sin x) = cos(x) * e^(sin x)."},
            {"id": "math_2", "text": "What is the value of ∫₀^(π/2) sin(x) dx?", "options": ["0", "1", "-1", "π/2"], "answer": 1, "explanation": "[-cos(x)] from 0 to π/2 = -cos(π/2) - (-cos(0)) = 0 - (-1) = 1."},
            {"id": "math_3", "text": "If A is a square matrix of order 3 and |A| = 4, then |adj(A)| is equal to:", "options": ["4", "16", "64", "12"], "answer": 1, "explanation": "For an n×n matrix, |adj(A)| = |A|^(n-1). Here 4^(3-1) = 4^2 = 16."},
            {"id": "math_4", "text": "Two events A and B are independent. If P(A) = 0.3 and P(B) = 0.4, find P(A ∪ B):", "options": ["0.70", "0.58", "0.12", "0.82"], "answer": 1, "explanation": "P(A ∪ B) = P(A) + P(B) - P(A∩B) = 0.3 + 0.4 - (0.3*0.4) = 0.7 - 0.12 = 0.58."},
            {"id": "math_5", "text": "What is the direction cosines of the vector r = 2i + 3j - 6k?", "options": ["2/7, 3/7, -6/7", "2/49, 3/49, -6/49", "2, 3, -6", "1/7, 2/7, -3/7"], "answer": 0, "explanation": "|r| = √(4 + 9 + 36) = √49 = 7. Direction cosines = (2/7, 3/7, -6/7)."},
            {"id": "math_6", "text": "The domain of function f(x) = sin⁻¹(2x - 1) is:", "options": ["[0, 1]", "[-1, 1]", "[0, 2]", "(-1, 1)"], "answer": 0, "explanation": "-1 ≤ 2x - 1 ≤ 1 => 0 ≤ 2x ≤ 2 => 0 ≤ x ≤ 1. Domain is [0, 1]."},
            {"id": "math_7", "text": "What is the order and degree of differential equation (d²y/dx²)³ + (dy/dx)² + sin(y) = 0?", "options": ["Order 2, Degree 3", "Order 3, Degree 2", "Order 2, Degree not defined", "Order 1, Degree 2"], "answer": 0, "explanation": "Highest derivative is d²y/dx² (order 2), raised to power 3 (degree 3)."}
        ],
    },
    {
        "id": "cbse-cs-prog-11-12",
        "theme": "prog",
        "category": "Computer Science",
        "title": "Computer Science & Python",
        "description": "Python, Data Structures, OOP, and Relational Databases (SQL).",
        "minutes": 20,
        "questions": [
            {"id": "cs_1", "text": "Which of the following data types is IMMUTABLE in Python?", "options": ["List", "Dictionary", "Set", "Tuple"], "answer": 3, "explanation": "Tuples, integers, floats, strings, and frozensets are immutable in Python."},
            {"id": "cs_2", "text": "What is the output of print([1, 2, 3] * 2)?", "options": ["[2, 4, 6]", "[1, 2, 3, 1, 2, 3]", "[[1, 2, 3], [1, 2, 3]]", "Error"], "answer": 1, "explanation": "Multiplying a list by an integer n repeats the list n times."},
            {"id": "cs_3", "text": "What is the worst-case time complexity of QuickSort on an already sorted array with last element pivot?", "options": ["O(N log N)", "O(N²)", "O(N)", "O(log N)"], "answer": 1, "explanation": "QuickSort degrades to O(N²) when partition is unbalanced (e.g. sorted array with last element pivot)."},
            {"id": "cs_4", "text": "Which data structure operates on LIFO (Last In First Out) principle?", "options": ["Queue", "Stack", "Binary Tree", "Linked List"], "answer": 1, "explanation": "A Stack operates on LIFO; Queue operates on FIFO."},
            {"id": "cs_5", "text": "Which SQL clause is used to filter groups created by GROUP BY?", "options": ["WHERE", "HAVING", "ORDER BY", "FILTER"], "answer": 1, "explanation": "HAVING filters aggregated groups; WHERE filters individual table rows prior to aggregation."}
        ],
    },
    {
        "id": "gk-101",
        "theme": "gk",
        "category": "General Knowledge",
        "title": "General Knowledge",
        "description": "Warm up with questions about the world around you.",
        "minutes": 10,
        "questions": [
            {"id": "gk_1", "text": "What is the capital city of Japan?", "options": ["Seoul", "Tokyo", "Beijing", "Bangkok"], "answer": 1},
            {"id": "gk_2", "text": "Which planet is known as the Red Planet?", "options": ["Venus", "Jupiter", "Mars", "Saturn"], "answer": 2},
            {"id": "gk_3", "text": "How many continents are there on Earth?", "options": ["5", "6", "7", "8"], "answer": 2},
            {"id": "gk_4", "text": "Which is the largest ocean?", "options": ["Atlantic", "Indian", "Arctic", "Pacific"], "answer": 3},
            {"id": "gk_5", "text": "Who painted the Mona Lisa?", "options": ["Leonardo da Vinci", "Pablo Picasso", "Vincent van Gogh", "Claude Monet"], "answer": 0},
        ],
    },
    {
        "id": "web-101",
        "theme": "web",
        "category": "Web Development",
        "title": "Web Basics",
        "description": "HTML, CSS and JavaScript fundamentals for beginners.",
        "minutes": 8,
        "questions": [
            {"id": "web_1", "text": "What does HTML stand for?", "options": ["HyperText Markup Language", "High Tech Modern Language", "Home Tool Markup Language", "Hyperlink Text Mode Language"], "answer": 0},
            {"id": "web_2", "text": "Which language is used to style web pages?", "options": ["HTML", "Python", "CSS", "SQL"], "answer": 2},
            {"id": "web_3", "text": "Which HTML tag makes a link?", "options": ["<link>", "<a>", "<href>", "<url>"], "answer": 1},
            {"id": "web_4", "text": "Which keyword declares a variable that cannot be reassigned in JavaScript?", "options": ["var", "let", "const", "static"], "answer": 2},
            {"id": "web_5", "text": "Which CSS property changes text colour?", "options": ["font-color", "text-color", "color", "foreground"], "answer": 2},
        ],
    },
]

SAMPLE_CLASSMATES = [
    {"name": "Aarav Mehta", "average": 92, "quizzes": 7},
    {"name": "Sara Khan", "average": 88, "quizzes": 6},
    {"name": "Liam Chen", "average": 81, "quizzes": 5},
    {"name": "Diya Patel", "average": 76, "quizzes": 8},
    {"name": "Noah Fernandes", "average": 69, "quizzes": 4},
    {"name": "Ishita Rao", "average": 63, "quizzes": 5},
    {"name": "Kabir Singh", "average": 55, "quizzes": 3},
]

class SafeTopicDict(dict):
    def __getitem__(self, key):
        return self.get(key, str(key).capitalize() if key else "Mixed")

TOPIC_NAMES = SafeTopicDict({
    "mix": "Mixed",
    "math": "Maths",
    "gk": "General Knowledge",
    "web": "Web & Code",
    "phys": "Physics",
    "chem": "Chemistry",
    "prog": "Computer Science",
    "dsa": "Data Structures",
    "sql": "SQL Databases",
})


def theme_of(quiz):
    """Which subject a quiz belongs to."""
    if not quiz:
        return "mix"
    if quiz.get("theme"):
        return quiz["theme"]
    cat = (quiz.get("category") or quiz.get("title") or "").lower()
    if "phys" in cat:
        return "phys"
    if "chem" in cat:
        return "chem"
    if "math" in cat:
        return "math"
    if "comp" in cat or "prog" in cat or "python" in cat or "code" in cat:
        return "prog"
    if "gk" in cat or "general" in cat:
        return "gk"
    if "web" in cat:
        return "web"
    id_map = {
        "cbse-phys-11-12": "phys",
        "cbse-chem-11-12": "chem",
        "cbse-math-11-12": "math",
        "cbse-cs-prog-11-12": "prog",
        "cbse-cs-py-11-12": "prog",
        "gk-101": "gk",
        "math-101": "math",
        "web-101": "web"
    }
    return id_map.get(quiz.get("id"), "mix")


# ---------- Reading and writing the save file ----------

def _read_all():
    try:
        return json.loads(SAVE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


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
    idx = next((i for i, q in enumerate(all_quizzes) if q["id"] == quiz["id"]), -1)
    if idx >= 0:
        all_quizzes[idx] = quiz
    else:
        all_quizzes.append(quiz)
    save("quizzes", all_quizzes)


# ---------- Accounts ----------

def get_users():
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
        return False
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


def set_current_user(user):
    """Store active user profile from API or local login."""
    if not user:
        remove("current_user")
        return
    save("current_user", {
        "id": user.get("id"),
        "email": user["email"],
        "role": user["role"],
        "name": user.get("name") or user.get("full_name") or "User"
    })


def logout():
    remove("current_user")


def get_current_user():
    user = load("current_user", None)
    if not user:
        return None
    account = next((u for u in get_users() if u["email"] == user["email"]), None)
    if account:
        user["name"] = account["name"]
    return user


# ---------- Attempts (one per finished quiz) ----------

def get_all_attempts():
    return load("attempts", [])


def get_attempts(email):
    return [a for a in get_all_attempts() if a.get("email") == email]


def save_attempt(attempt):
    all_attempts = get_all_attempts()
    idx = next((i for i, a in enumerate(all_attempts) if a["id"] == attempt["id"]), -1)
    if idx >= 0:
        all_attempts[idx] = attempt
    else:
        all_attempts.append(attempt)
    save("attempts", all_attempts)


def new_id():
    return str(int(time.time() * 1000))


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def nice_date(iso_text, with_time=False):
    if not iso_text:
        return "Recent"
    try:
        d = datetime.fromisoformat(str(iso_text).replace("Z", ""))
    except (ValueError, TypeError):
        return str(iso_text)
    return d.strftime("%d/%m/%Y, %I:%M %p") if with_time else d.strftime("%d/%m/%Y")


def initials(name):
    return "".join(w[0] for w in name.split() if w)[:2].upper() or "?"


# ---------- Achievement badges (worked out from saved attempts) ----------

def _topic_of_attempt(a):
    quiz = get_quiz(a.get("quizId"))
    return theme_of(quiz) if quiz else "mix"


def best_streak(attempts):
    """Longest run of passed quizzes in a row (oldest to newest)."""
    best = run = 0
    for a in attempts:
        run = run + 1 if a["percent"] >= PASS_MARK else 0
        best = max(best, run)
    return best


def js_round(x):
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
    if not attempts:
        return {"average": "–", "passRate": "–"}
    passed = sum(1 for a in attempts if a["percent"] >= PASS_MARK)
    return {"average": f"{js_round(_average(attempts))}%",
            "passRate": f"{js_round(passed / len(attempts) * 100)}%"}
