# 🎓 Quiz Assessment Platform

A modern, responsive, dashboard-style web platform for conducting academic quizzes, timed assessments, and automated evaluation.

- **Frontend**: Pure HTML5, CSS3, and vanilla JavaScript (no complex framework, beginner-friendly).
- **Backend**: Python 3.11+, FastAPI, and SQLAlchemy.
- **Database**: PostgreSQL (with automated schema creation and default seed data).

---

## 👩‍💻 Guide for Frontend Developer (Quick Start in 2 Minutes)

If you are working on the **Frontend (Design, HTML, CSS, JavaScript)**, you **do NOT need to install or configure PostgreSQL**. 

The frontend has a built-in **Offline Demo Mode** with pre-loaded mock quizzes and automatic 1-click login buttons!

### Step 1: Open the Project in VS Code
1. Open **Visual Studio Code**.
2. Click **File ➔ Open Folder...** and select the `quiz-assessment-platform` directory.

### Step 2: Start the Frontend
Open the terminal in VS Code (`Ctrl + ~` or Terminal ➔ New Terminal) and run:

```powershell
npm start
```
*(Or if you prefer Python: `python -m http.server 5500 --directory frontend`)*

### Step 3: View in Browser
Open your browser and visit:
👉 **[http://localhost:5500](http://localhost:5500)**

### Step 4: Login with 1 Click
On the [Login Page](http://localhost:5500/login.html), simply click:
- **"Demo Student"** ➔ Click "Sign In" to test the Student Dashboard and take quizzes.
- **"Demo Instructor"** ➔ Click "Sign In" to test creating quizzes and reviewing results.

---

## 🎨 Where Can the Frontend Developer Make Changes?

| If you want to change... | Open this file | What to look for |
|---|---|---|
| **Theme Colors & Fonts** | `frontend/css/style.css` | Look at `:root` at the top: `--color-indigo-600` (primary button/accent color) |
| **Home Page Titles & Text** | `frontend/index.html` | Look for `hero-title` and `<section id="features">` |
| **Student Dashboard Look** | `frontend/student-dashboard.html` | Summary metric cards and sidebar navigation |
| **Quiz Taking Screen** | `frontend/take-quiz.html` & `frontend/css/quiz.css` | Timer widget, question buttons, and question navigator palette |
| **Quiz Creation Form** | `frontend/create-quiz.html` | Add/remove question fields and preview modal |
| **Results & Score Gauge** | `frontend/results.html` | Circular SVG score ring and pass/fail indicators |

---

## 👨‍💻 Guide for Backend Developer (FastAPI + PostgreSQL)

If you are working on the **Backend & Database**:

### Step 1: Set Up Python Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Step 2: Configure `.env`
Ensure your `.env` file in the root folder contains your PostgreSQL credentials:
```env
DATABASE_URL=postgresql+psycopg://postgres:admin123@localhost:5432/quiz%20assessment
SECRET_KEY=super_secure_random_key_of_at_least_32_characters_12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

### Step 3: Start the Backend Server
```powershell
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Step 4: Verify the API
Open your browser to:
- **Health Check**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health) (Returns `{"status": "ok", "database": "connected"}`)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (Test every endpoint directly in the browser!)

---

## 🌿 Team Collaboration (Git Workflow)

To avoid overwriting each other's work:

### 1. Work on Separate Branches
- **Frontend Teammate:**
  ```powershell
  git checkout -b frontend-design
  ```
- **Backend Teammate:**
  ```powershell
  git checkout -b backend-features
  ```

### 2. Pushing Your Changes
When you make changes and want to share them:
```powershell
git add .
git commit -m "Describe what you changed"
git push origin <your-branch-name>
```

### 3. Merging on GitHub
Go to GitHub ➔ Open a **Pull Request** ➔ Review the changes ➔ Click **Merge Pull Request**.

---

## 📁 Repository Structure

```text
frontend/
├── index.html                  # Landing page (hero, features, CSS mockup, workflow)
├── login.html                  # Sign-in with role toggle and demo autofill
├── register.html               # Registration with password strength meter
├── student-dashboard.html      # Student stats, active quizzes, recent attempts
├── instructor-dashboard.html   # Instructor dashboard, metrics, quiz management
├── quiz-list.html              # Assessment catalog with search and filters
├── take-quiz.html              # Distraction-free quiz engine, timer, and palette
├── create-quiz.html            # Dynamic question builder with option configurator
├── results.html                # Score gauge, accuracy stats, and question review
├── history.html                # Attempt history table and status filters
├── css/                        # Design tokens, typography, layouts, and quiz styles
│   ├── style.css               # Core colors (:root), buttons, cards, modals
│   ├── auth.css                # Login/Register styling
│   ├── dashboard.css           # Sidebar and stats layout
│   └── quiz.css                # Timer widget, question palette, score ring
├── js/                         # API client, auth, and page controllers
└── assets/images/              # Vector logos and illustrations

backend/
├── main.py                     # FastAPI entry point, CORS, and auto-seeding
├── config.py                   # Environment settings
├── database.py                 # SQLAlchemy engine and session dependency
├── models.py                   # Database tables: User, Quiz, Question, QuizAttempt
├── schemas.py                  # Pydantic validation schemas
├── routes/                     # Modular API endpoints
│   ├── auth.py                 # /api/auth (register, login, me)
│   ├── quizzes.py              # /api/quizzes (list, create, sanitized questions, delete)
│   └── attempts.py             # /api/attempts (start, submit, grade, history)
└── services/
    └── auth.py                 # Password hashing (Argon2) and JWT generation
```

---

## 🔑 Default Test Accounts

| Role | Email | Password | What You Can Do |
|---|---|---|---|
| **Student** | `student@college.edu` | `student123` | Browse quizzes, attempt timed assessments, view scores |
| **Instructor** | `instructor@college.edu` | `instructor123` | Create assessments, view class submissions, manage quizzes |
