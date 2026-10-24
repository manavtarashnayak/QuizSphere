# 🎓 Quiz Assessment Platform (QuizSphere)

A modern, responsive full-stack assessment platform designed for conducting timed exams, subject-wise quizzes, authoritative server-side evaluations, and tracking student performance metrics.

---

## 👥 Authors & Team Contributions

- **Frontend Developer**: **Sumedha Sil** (*SRM KTR · CSE Core · RA2611003011378*)
  - Desktop GUI frontend, dark glassmorphism styling, interactive hover effects, procedural background & vine canvas animations, question palette navigation, achievement badges showcase, and interactive podium leaderboard.
- **Backend Developer**: **Manav Tarash Nayak**
  - FastAPI consolidated REST API endpoints, PostgreSQL schema design and SQLAlchemy ORM models, Argon2 password hashing, PyJWT bearer token authentication, authoritative server-side exam grading, timer validation, and CBSE question bank seeding.

---

## 📸 Platform Screenshots

### 🖥️ Student Dashboard & Assessment Catalog
![Student Dashboard](docs/screenshots/student_dashboard.png)

### 📊 Performance Analytics, Curriculum & Achievements
![Assessment Platform Overview](docs/screenshots/assessment_platform.png)

---

## 🏗️ Architecture & Technology Stack

- **Frontend**: **Python Tkinter Desktop Application** (`frontend/quizsphere-frontend-python/frontend/`)
  - Smooth multi-screen router architecture (`main.py`)
  - Custom dark glassmorphism theme (`theme.py`) with per-subject dynamic color palettes
  - Particle & flower vine canvas animations (`background.py`, `border.py`, `effects.py`)
  - **Zero extra pip dependencies**: API communication built entirely using Python's standard library (`urllib.request`, `json`, `uuid`)
- **Backend**: **FastAPI** (`backend/main.py`)
  - 15 consolidated, production-ready REST API endpoints
  - JWT Bearer authentication with Argon2 password encryption
  - Server-side authoritative grading and strict time limit enforcement
- **Database**: **PostgreSQL** with SQLAlchemy ORM
  - 4 core relational tables: `users`, `quizzes`, `questions`, and `quiz_attempts`
  - Automated database seeding with Class 11th & 12th CBSE questions
- **Dual Execution Modes**:
  - 🌐 **Live Server Mode**: Connects directly to FastAPI and PostgreSQL with real-time score calculation and live podium rankings.
  - 💾 **Offline Demo Mode**: Automatic graceful fallback to local storage (`quizsphere_data.json`) if the backend server is offline or unreachable.

---

## 🌟 Key Platform Features

### 1. 📚 Comprehensive Curriculum & Question Banks
Pre-seeded in both the **PostgreSQL Database** and the **Offline Demo Bank**:
- ⚛️ **CBSE Physics (Classes 11 & 12)**: Gravitational constants, projectile motion, first law of thermodynamics, electrostatic fields in conducting shells, wave optics, polarization, and de Broglie wavelengths.
- 🧪 **CBSE Chemistry (Classes 11 & 12)**: Quantum orbital nodes, VSEPR molecular geometry (XeF₄), reaction kinetics, transition metal oxidation states, Lucas test, and polymer monomer units.
- 📐 **CBSE Mathematics (Classes 11 & 12)**: Chain rule calculus derivatives, definite integrals, adjoint matrices, probability, vector direction cosines, and differential equations.
- 💻 **Computer Science & Python Programming**: Data types, mutability (tuples vs lists), list operations, OOP concepts, and SQL (`HAVING` vs `WHERE`).
- 🌲 **Core Computer Science**: Data Structures & Algorithms (Stacks, Queues, QuickSort complexity, Binary Trees).
- 🗄️ **Database Systems**: Relational database schema, primary keys, and query optimization.
- 🌍 **General Knowledge & Web Basics**: Fundamentals of HTML5, CSS3, JavaScript ES6, and general science trivia.

---

### 2. 🎯 Student Assessment Engine
- **Live Database Streaming**: Available quizzes are streamed directly from PostgreSQL.
- **Timed Exam Session**: Live countdown clock, progress bar, and question palette with answered status indicators.
- **Cheat-Proof Architecture**: Correct answers and explanations are securely withheld by the backend during active assessments (`GET /api/quizzes/{id}/questions`).
- **Authoritative Server Grading**: Exam answers are submitted to the server (`POST /api/attempts/{id}/submit`), which validates timer constraints and grades each question accurately.
- **Detailed Results Breakdown**: Visual score percentage ring, celebratory confetti for scores ≥ 80%, golden trophy for 100% scores, and per-question explanation reviews.
- **Achievement Badges System**: Unlockable reward badges for consistency, high accuracy, and exam streaks (*First Steps, Perfectionist, Hat Trick, Explorer, High Flyer, Quiz Master*).
- **Interactive Leaderboard**: Live student rankings calculated by average percentage scores and completed assessments, featuring a 1st/2nd/3rd place medal podium.
- **Attempt History**: Full history of past assessments with subject filter chips (*Physics, Chemistry, Maths, Programming, GK, Web*).

---

### 3. 👨‍🏫 Instructor Management Tools
- **Quiz Creator**: Interface to create custom quizzes with titles, descriptions, subject categories, time limits, and multiple-choice questions.
- **Dual Persistence**: Newly created quizzes are saved immediately to PostgreSQL and mirrored locally for offline availability.
- **Analytics & Participation Table**: Overview of total quizzes, student participation count, average scores, and pass rates.

---

## 🚀 Setup & Execution Guide

### 1. Prerequisites
- **Python 3.11+**
- **PostgreSQL 14+** (e.g. pgAdmin 4 or `psql`)

---

### 2. Configure PostgreSQL Database
Create a database named `quiz assessment` in PostgreSQL:
```sql
CREATE DATABASE "quiz assessment";
```

Create a `.env` file in the project root directory:
```env
DATABASE_URL=postgresql+psycopg://postgres:admin123@localhost:5432/quiz%20assessment
SECRET_KEY=super_secure_random_key_of_at_least_32_characters_12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```
*(Adjust the username and password in `DATABASE_URL` to match your local PostgreSQL configuration).*

---

### 3. Install Python Dependencies
In the project root folder:
```powershell
# Create virtual environment (optional but recommended)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r requirements.txt
```

---

### 4. Start the FastAPI Backend Server
```powershell
uvicorn backend.main:app --port 8000
```
*On initial startup, the backend automatically seeds all PostgreSQL tables with default accounts, CBSE questions, and quizzes.*

- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Database Health Check**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

### 5. Start the Python Tkinter Desktop Frontend
In a new terminal window:
```powershell
cd frontend\quizsphere-frontend-python\frontend
python main.py
```

---

## 👥 Default Demo Credentials

| Role | Email | Password | Permissions |
|---|---|---|---|
| **Student** | `student@college.edu` | `student123` | Take CBSE & CS assessments, review detailed answers, view badges and class leaderboard |
| **Instructor** | `instructor@college.edu` | `instructor123` | Create new assessments, view participation statistics and quiz table |

*(You can also use the 1-click **"Demo Student"** and **"Demo Instructor"** buttons on the login screen).*

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| **GET** | `/api/health` | Health check verifying PostgreSQL database connectivity |
| **POST** | `/api/auth/register` | Register a new student or instructor |
| **POST** | `/api/auth/login` | Authenticate credentials and return JWT bearer token |
| **GET** | `/api/auth/me` | Fetch authenticated user profile |
| **GET** | `/api/quizzes` | Fetch all published assessments from PostgreSQL |
| **POST** | `/api/quizzes` | Create a new assessment with questions |
| **GET** | `/api/quizzes/{quiz_id}` | Fetch metadata of a single quiz |
| **PUT** | `/api/quizzes/{quiz_id}` | Update quiz parameters or questions |
| **DELETE** | `/api/quizzes/{quiz_id}` | Delete a quiz and all associated questions |
| **GET** | `/api/quizzes/{quiz_id}/questions` | Sanitized question payload for students (*answers hidden*) |
| **POST** | `/api/quizzes/{quiz_id}/start` | Initialize exam session & start timer |
| **POST** | `/api/attempts/{attempt_id}/submit` | Authoritative server-side grading & time validation |
| **GET** | `/api/attempts/{attempt_id}/result` | Fetch detailed score breakdown & explanation review |
| **GET** | `/api/attempts/history` | Retrieve past attempt records for logged-in user |
| **GET** | `/api/leaderboard` | Top student rankings computed from PostgreSQL database |
| **GET** | `/api/quizzes/{quiz_id}/analytics` | Overall performance analytics for an assessment |
| **GET** | `/api/quizzes/{quiz_id}/results` | Instructor overview of all student submissions |

---

## 📁 Repository Structure

```text
quiz-assessment-platform/
├── backend/
│   ├── main.py                     # Consolidated FastAPI application (All 15 API routes, CORS, init)
│   ├── config.py                   # Pydantic Settings & environment variables
│   ├── database.py                 # SQLAlchemy engine, connection check, and DB session
│   ├── models.py                   # PostgreSQL ORM models: User, Quiz, Question, QuizAttempt
│   ├── schemas.py                  # Pydantic validation schemas (Auth, Quizzes, Attempts, Leaderboard)
│   ├── services/
│   │   └── auth.py                 # Argon2 password hashing and PyJWT security utilities
│   └── seed/
│       └── cbse_questions.py       # Comprehensive CBSE 11/12th & Python question bank
│
├── frontend/
│   └── quizsphere-frontend-python/
│       └── frontend/
│           ├── main.py             # Desktop Tkinter application entry point & router
│           ├── api.py              # Zero-dependency HTTP client connecting to FastAPI/PostgreSQL
│           ├── data.py             # Data manager, local persistence, CBSE questions bank
│           ├── theme.py            # Dark glassmorphism styling, safe color palettes, fonts
│           ├── background.py       # Animated canvas background with interactive shapes
│           ├── border.py           # Procedural flower vine border animation
│           ├── effects.py          # Confetti particle engine and 3D spinning trophy
│           └── pages/
│               ├── home.py         # Welcome landing screen
│               ├── login.py        # Authentication with role toggle & 1-click demo buttons
│               ├── register.py     # Account creation with live password strength meter
│               ├── student.py      # Student dashboard with live database quiz streaming
│               ├── instructor.py   # Instructor portal with participation table
│               ├── take_quiz.py    # Timed exam engine with question palette
│               ├── results.py      # Score arc ring, trophy, badges, and explanation review
│               ├── leaderboard.py  # Medal podium (1st, 2nd, 3rd) and student rankings
│               ├── history.py      # Attempt records with subject filter chips
│               ├── create_quiz.py  # Multi-question creator with options and explanations
│               ├── profile.py      # Student/Instructor profile and display name editor
│               └── common.py       # Reusable UI widgets (stat cards, badges, topic tags)
│
├── docs/
│   └── screenshots/                # UI screenshots for README
│       ├── student_dashboard.png
│       └── assessment_platform.png
│
├── .env.example                    # Template environment variables
├── requirements.txt                # Python backend dependencies
└── README.md                       # Complete platform documentation
```

---

## 📄 License
This project is developed for academic assessment and learning purposes. © 2026 QuizSphere.
