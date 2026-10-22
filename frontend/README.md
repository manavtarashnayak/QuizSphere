# Quiz Assessment Platform — Frontend

A modern, responsive, dashboard-style web frontend for the **Quiz Assessment Platform**, built strictly with HTML5, CSS3, and vanilla JavaScript (no frontend frameworks).

Designed for college and academic assessment workflows, supporting students and instructors.

---

## 🚀 Quick Start (Running the Frontend)

You can serve the frontend with any standard static HTTP file server:

### Option 1: Python HTTP Server (Recommended)
```bash
# From the repository root
python -m http.server 3000 --directory frontend
```
Then open your browser at:
👉 **[http://localhost:3000](http://localhost:3000)**

### Option 2: Node / npx serve
```bash
npx serve frontend -l 3000
```

### Option 3: VS Code Live Server
Right-click `frontend/index.html` and choose **"Open with Live Server"**.

---

## 🔑 Demo Credentials (Offline / Standalone Testing)

The frontend features automatic backend detection. If the FastAPI backend is not running, the application gracefully activates **Demo Mode**, backed by a full client-side mock store in `localStorage`.

Quick-login autofill buttons are available on the login page:

| Role | Email | Password |
|---|---|---|
| **Student** | `student@college.edu` | `student123` |
| **Instructor** | `instructor@college.edu` | `instructor123` |

---

## 📁 Architecture & Folder Structure

```
frontend/
├── index.html                  # Landing page with hero, mockup, features, workflows
├── login.html                  # Login page with role toggle and demo autofill
├── register.html               # Registration with password strength indicator
├── student-dashboard.html      # Student summary cards, active quizzes, recent attempts
├── instructor-dashboard.html   # Instructor quiz management table, metric cards, deletion
├── quiz-list.html              # Quiz catalog with search, category & difficulty filters
├── take-quiz.html              # Distraction-free quiz interface, countdown timer, palette
├── create-quiz.html            # Dynamic question builder with 4 options and preview
├── results.html                # Radial score gauge, statistics, and detailed review
├── history.html                # Student past attempt history and filtering
├── css/
│   ├── style.css               # Design system tokens, buttons, cards, modals, toasts
│   ├── auth.css                # Authentication cards, role pills, strength meters
│   ├── dashboard.css           # Sidebar layout, metrics grid, tables, responsive offcanvas
│   └── quiz.css                # Timer widget, question palette, question builder, score gauge
├── js/
│   ├── config.js               # API URL, endpoints, timeouts, and storage keys
│   ├── api.js                  # Fetch client, JWT Bearer handling, mock database simulator
│   ├── auth.js                 # Authentication logic, form validation, password visibility
│   ├── student-dashboard.js    # Student analytics, recent quizzes, attempts
│   ├── instructor-dashboard.js # Instructor dashboard, table actions, quiz deletion modal
│   ├── quiz-list.js            # Catalog search and filter engine
│   ├── take-quiz.js            # Live quiz engine: timer, state persistence, question palette
│   ├── create-quiz.js          # Dynamic question builder, form validation, preview modal
│   ├── results.js              # Score gauge calculation, pass/fail status, review breakdown
│   └── history.js              # Historical attempts table, search, and status filtering
└── assets/
    └── images/
        └── logo.svg            # Platform vector logo
```

---

## 🔌 FastAPI & PostgreSQL Backend Integration

The frontend connects to the backend via `js/api.js` using configuration in `js/config.js`:

```javascript
const CONFIG = {
  API_BASE_URL: 'http://127.0.0.1:8000',
  ...
};
```

### Expected REST API Endpoints

- `GET  /health` - Backend health check
- `POST /api/auth/login` - Authenticate user `{ email, password, role }` -> `{ access_token, user }`
- `POST /api/auth/register` - Create account `{ full_name, email, password, role }`
- `GET  /api/auth/me` - Current authenticated user
- `GET  /api/quizzes` - List available quizzes
- `POST /api/quizzes` - Create new quiz with questions (Instructor)
- `DELETE /api/quizzes/{id}` - Delete quiz (Instructor)
- `GET  /api/quizzes/{id}/questions` - Sanitized questions for active quiz (no correct answers)
- `POST /api/quizzes/{id}/start` - Begin a new attempt session
- `POST /api/attempts/{id}/submit` - Submit answers `{ quiz_id, answers, time_taken_seconds }`
- `GET  /api/attempts/{id}/result` - Retrieve evaluated score and review
- `GET  /api/attempts/history` - Retrieve student's attempt history

### Security Design
- **Zero Answer Leakage**: Correct answers are **never** delivered in the question payload before submission.
- **Authoritative Grading**: Scores are evaluated on the server side upon final submission.
- **Session Preservation**: State is preserved during the test in `sessionStorage` in case of accidental browser refresh.
- **Accidental Navigation Guard**: `beforeunload` warning triggers if the user attempts to close the tab during an active test.
