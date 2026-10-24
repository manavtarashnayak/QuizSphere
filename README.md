# 🎓 Quiz Assessment Platform (QuizSphere)

A modern, responsive, full-stack assessment platform designed for conducting timed exams, subject-wise quizzes, automated evaluations, and tracking student performance metrics.

- **Frontend**: Pure HTML5, Modern CSS3 (Dark glassmorphism theme, dynamic 3D background canvas, interactive tilt effects), and Vanilla JavaScript (No heavy frameworks, fast and beginner-friendly).
- **Backend**: Python 3.11+, FastAPI (with fully consolidated, production-ready REST API endpoints).
- **Database**: PostgreSQL with SQLAlchemy ORM (automatic schema migrations and comprehensive starter seed data).
- **Dual Execution Modes**: 
  - 🌐 **Full-Stack Mode**: Connected to PostgreSQL and FastAPI with secure JWT authentication and authoritative server-side grading.
  - 💾 **Offline Demo Mode**: Zero-backend setup required! Pure in-browser localStorage simulation with mock users, custom test configurator, and instant grading.

---

## 🌟 Key Platform Features

### 1. 📚 Rich Curriculum & Question Banks
Pre-seeded in both **Live PostgreSQL Database** and **Frontend Demo Mode**:
- ⚛️ **CBSE Physics (Classes 11 & 12)**: Mechanics, Gravitation, Thermodynamics, Electrostatics, Gauss's Law, Wave Optics, and de Broglie wavelengths.
- 🧪 **CBSE Chemistry (Classes 11 & 12)**: Carbon Hybridization, Chemical Equilibrium, Redox, Lucas Test, Reaction Kinetics, and Lanthanoids.
- 📐 **CBSE Mathematics (Classes 11 & 12)**: Calculus derivatives, Definite integrals, Adjoint matrices, Probability, Vectors, and Set theory.
- 💻 **Computer Science & Python Programming**: Data types, mutability, string operations, operator precedence, functions (`def`), loops (`range`), and SQL queries (`HAVING` vs `WHERE`).
- 🌲 **Core Computer Science**: Data Structures & Algorithms (Trees, Graphs, QuickSort complexity, Dijkstra's algorithm).
- 🗄️ **Database Systems**: Normal forms (1NF, 2NF, 3NF), and ACID transactions.
- 🌍 **General Knowledge & Web Basics**: Fundamentals of HTML, CSS, JavaScript, and world trivia.

---

### 2. 🎯 Student Assessment Engine
- **Custom Test Builder**: Students can configure assessments on-the-fly by choosing specific subjects (Physics, Chemistry, Maths, Programming, etc.) and selecting custom question counts (5, 10, 15, 20, or All).
- **Distraction-Free Exam Interface**: Live countdown timer with auto-submit on expiry, question palette with status indicators (answered, unanswered, marked for review).
- **Immediate Results & Performance Review**: Question-by-question explanations, percentage accuracy breakdown, time-taken metrics, and pass/fail badges.
- **Student History & Records**: Chronological log of past tests, scores, and dates.
- **Gamified Achievement Badges**: Unlockable reward badges for consistency, high accuracy, and streaks.
- **Top Classmate Leaderboard**: Live ranking based on average scores and quizzes completed.

---

### 3. 👨‍🏫 Instructor Management Tools
- **Assessment Creator**: Intuitive interface to create custom assessments with questions, 4 options, designated correct answers, explanations, and custom passing criteria.
- **Quiz Management & Editing**: Real-time ability to update durations, modify passing scores, or delete outdated quizzes (`PUT` and `DELETE` endpoints).
- **Submissions & Analytics Dashboard**: Overview of student submissions, pass/fail percentages, and average scores per quiz.

---

### 4. 🔒 Security & Architecture Design
- **Cheat-Proof Questions Endpoint**: Correct answers and explanations are stripped when fetching questions for an active test (`GET /api/quizzes/{id}/questions`).
- **Authoritative Server-Side Grading**: All scoring happens on the server (`POST /api/attempts/{id}/submit`).
- **Strict Timer Enforcement**: Late submissions exceeding allowed duration plus network grace period are automatically rejected by the server.
- **JWT Authentication & Password Hashing**: Passwords encrypted via modern Argon2 hashing; sessions verified via PyJWT Bearer tokens.

---

## 🚀 Setup & Execution Guide

### Option A: Frontend Quick Start (Zero Database / Teammate Guide)
If you are working on the **Frontend (UI, CSS, JavaScript)**, you **do NOT need to install PostgreSQL or Python**:

1. **Open the repository in VS Code**:
   ```powershell
   cd quiz-assessment-platform
   ```
2. **Start the Frontend Server**:
   ```powershell
   npm start
   ```
   *(Alternative using Python built-in server: `python -m http.server 5500 --directory frontend`)*
   *(Alternative: Right-click `frontend/index.html` and choose **"Open with Live Server"** in VS Code).*

3. **Open in Browser**:
   Visit 👉 **[http://localhost:5500](http://localhost:5500)** (or `http://localhost:5500/student-dashboard.html`)

4. **1-Click Demo Logins**:
   - On `login.html`, click **"Demo Student"** to explore the student dashboard, take CBSE/Programming quizzes, and view badges.
   - Click **"Demo Instructor"** to test creating quizzes.

---

### Option B: Backend Setup (FastAPI + PostgreSQL)

#### 1. Prerequisites
- **Python 3.11+**
- **PostgreSQL 14+** (e.g., pgAdmin 4)

#### 2. Configure PostgreSQL Database
In pgAdmin or SQL Shell (`psql`), create a database named `quiz assessment` (or any database name you prefer):
```sql
CREATE DATABASE "quiz assessment";
```

#### 3. Setup Virtual Environment & Dependencies
In the project root folder:
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Install required Python packages
pip install -r requirements.txt
```

#### 4. Environment Variables (`.env`)
Create or edit your `.env` file in the root directory:
```env
# PostgreSQL connection string (URL encode any space in database name as %20)
DATABASE_URL=postgresql+psycopg://postgres:admin123@localhost:5432/quiz%20assessment
SECRET_KEY=super_secure_random_key_of_at_least_32_characters_12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=http://localhost:5500,http://127.0.0.1:5500,http://localhost:3000
```

#### 5. Start the Backend Server
```powershell
npm run backend
# OR directly with uvicorn:
.venv\Scripts\uvicorn.exe backend.main:app --reload --port 8000
```
*Note: On first startup, the server automatically creates all PostgreSQL tables and populates the default users and CBSE + Programming quizzes!*

#### 6. Test Backend Endpoints
- **Database Health Check**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)
- **Interactive Swagger Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### Option C: Run Full-Stack Simultaneously
If you want both frontend and backend running with one command:
```powershell
npm run dev
```

---

## 📡 Complete REST API Reference (All in `backend/main.py`)

| Method | Endpoint | Description |
|---|---|---|
| **GET** | `/api/health` | Health check verifying PostgreSQL database connectivity |
| **POST** | `/api/auth/register` | Register a new student or instructor |
| **POST** | `/api/auth/login` | Authenticate credentials and return JWT bearer token |
| **GET** | `/api/auth/me` | Fetch authenticated user profile |
| **GET** | `/api/quizzes` | Fetch all published assessments |
| **POST** | `/api/quizzes` | Create a new assessment with questions |
| **GET** | `/api/quizzes/{quiz_id}` | Fetch metadata of a single quiz |
| **PUT** | `/api/quizzes/{quiz_id}` | Update quiz parameters or questions |
| **DELETE** | `/api/quizzes/{quiz_id}` | Delete a quiz and all associated questions |
| **GET** | `/api/quizzes/{quiz_id}/questions` | Sanitized question payload for students (*answers hidden*) |
| **POST** | `/api/quizzes/{quiz_id}/start` | Initialize exam session & start timer |
| **POST** | `/api/attempts/{attempt_id}/submit` | Submit answers for server-side grading and time validation |
| **GET** | `/api/attempts/{attempt_id}/result` | Fetch detailed score breakdown & explanation review |
| **GET** | `/api/attempts/history` | Retrieve past attempt records for logged-in user |
| **GET** | `/api/leaderboard` | Top student ranking computed by average scores & tests completed |
| **GET** | `/api/quizzes/{quiz_id}/analytics` | Overall performance analytics for an assessment |
| **GET** | `/api/quizzes/{quiz_id}/results` | Instructor overview of all student submissions |

---

## 📁 Repository Structure

```text
quiz-assessment-platform/
├── backend/
│   ├── main.py                     # Consolidated FastAPI entry point (All 15 API routes, CORS, init)
│   ├── config.py                   # Pydantic Settings & environment variables
│   ├── database.py                 # SQLAlchemy engine, connection check, and DB session
│   ├── models.py                   # Database models: User, Quiz, Question, QuizAttempt
│   ├── schemas.py                  # Pydantic validation schemas (Auth, Quizzes, Attempts, Leaderboard)
│   ├── routes/                     # Modular route components
│   │   ├── auth.py                 # Authentication routes
│   │   ├── quizzes.py              # Quiz management routes
│   │   └── attempts.py             # Attempt, grading, and leaderboard routes
│   ├── services/
│   │   └── auth.py                 # Argon2 password hashing and PyJWT security utilities
│   └── seed/
│       └── cbse_questions.py       # Comprehensive CBSE 11/12th & Python question bank
│
├── frontend/
│   ├── index.html                  # Landing page with animated hero, features, and 3D background
│   ├── login.html                  # Login page with role toggle and 1-click demo buttons
│   ├── register.html               # Registration page with strength indicators
│   ├── student-dashboard.html      # Main student dashboard with custom test builder & subjects
│   ├── instructor-dashboard.html   # Instructor dashboard for quiz management
│   ├── quiz-list.html              # Catalog of assessments
│   ├── take-quiz.html              # Full-screen timed exam engine with question palette
│   ├── results.html                # Score breakdown, radial gauge, and question review
│   ├── history.html                # Past test attempts table with filters
│   ├── leaderboard.html            # Top student rankings and statistics
│   ├── profile.html                # User profile and custom settings
│   ├── css/
│   │   ├── site.css                # Global glassmorphism design system & variables
│   │   ├── style.css               # Core styling tokens
│   │   ├── auth.css                # Authentication styling
│   │   ├── dashboard.css           # Dashboard metrics & layout
│   │   └── quiz.css                # Exam interface & timer widgets
│   └── js/
│       ├── data.js                 # Local mock database for Offline Demo Mode & CBSE questions
│       ├── dashboard.js            # Student dashboard controller & test generator
│       ├── quiz.js                 # Live exam timer, option selection, and submission logic
│       ├── results.js              # Score gauge & review renderer
│       ├── history.js              # Attempt history controller
│       ├── badges.js               # Achievement badges system
│       ├── background.js           # Interactive 3D wireframe canvas background
│       └── effects.js              # Glassmorphism tilt and card hover effects
│
├── .env.example                    # Template environment variables
├── package.json                    # npm lifecycle scripts (`npm start`, `npm run backend`, `npm run dev`)
├── requirements.txt                # Python backend dependencies
└── README.md                       # Complete project and onboarding documentation
```

---

## 👥 Default Demo Credentials

| Role | Email | Password | Permissions |
|---|---|---|---|
| **Student** | `student@college.edu` | `student123` | Take CBSE & CS assessments, customize test length, review scores, view leaderboard |
| **Instructor** | `instructor@college.edu` | `instructor123` | Create new assessments, edit quiz parameters, view student submissions |

---

## 🌿 Git Team Workflow

When working together on features:
1. **Pull latest changes:**
   ```powershell
   git checkout main
   git pull origin main
   ```
2. **Create your feature branch:**
   ```powershell
   git checkout -b feature/your-feature-name
   ```
3. **Commit & Push:**
   ```powershell
   git add .
   git commit -m "feat: description of work"
   git push origin feature/your-feature-name
   ```
4. **Open a Pull Request on GitHub** to merge cleanly into `main`.
