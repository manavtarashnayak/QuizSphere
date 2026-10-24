# QuizSphere — Frontend (Python Tkinter)

The QuizSphere frontend, made only with **Python** and its built-in **Tkinter** library.
No HTML, CSS or JavaScript. It opens as a desktop window.

**Front-end developer:** Sumedha Sil · SRM KTR · CSE Core · RA2611003011378

## Run it

You need Python 3.8 or newer. Tkinter comes with Python on Windows and Mac.

In VS Code: open the `frontend` folder, open `main.py`, and click the ▶ **Run Python File**
button at the top right. Or type this in the terminal:

```
cd frontend
python main.py
```

On Windows you can also double-click `main.py`.

| Role       | Email                    | Password        |
|------------|--------------------------|-----------------|
| Student    | `student@college.edu`    | `student123`    |
| Instructor | `instructor@college.edu` | `instructor123` |

## Where your data goes

The app runs in **Offline Demo Mode**. It does not talk to the backend yet.
Accounts, quizzes and scores are saved in `quizsphere_data.json` next to `main.py`.
That file is the desktop version of the browser's localStorage.
Delete it to start fresh. `.gitignore` stops it from being uploaded to GitHub.

## Which file does what

| Python file               | What it does (and the old web file it replaced) |
|---------------------------|----------------------------------------|
| `main.py`                 | the links between pages + `logout`     |
| `data.py`                 | `js/data.js`, `js/badges.js`           |
| `theme.py`                | `css/site.css`                         |
| `background.py`           | `js/background.js` (3D shapes, switched off: see `main.py`) |
| `border.py`               | flower border: vines and floating flowers beside the page |
| `effects.py`              | `js/confetti.js`, `js/trophy.js`, the Home screen flower and badge flips |
| `pages/home.py`           | `index.html`                           |
| `pages/login.py`          | `login.html` + `js/login.js`           |
| `pages/register.py`       | `register.html` + `js/register.js`     |
| `pages/student.py`        | `student-dashboard.html` + `js/dashboard.js` |
| `pages/take_quiz.py`      | `take-quiz.html` + `js/quiz.js`        |
| `pages/results.py`        | `results.html` + `js/results.js`       |
| `pages/history.py`        | `history.html` + `js/history.js`       |
| `pages/leaderboard.py`    | `leaderboard.html` + `js/leaderboard.js` |
| `pages/profile.py`        | `profile.html` + `js/profile.js`       |
| `pages/instructor.py`     | `instructor-dashboard.html` + `js/instructor.js` |
| `pages/create_quiz.py`    | `create-quiz.html` + `js/create-quiz.js` |

The space beside the page is decorated with a flower border (`border.py`).
