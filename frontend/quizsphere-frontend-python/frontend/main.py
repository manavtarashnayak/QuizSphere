"""
QuizSphere — desktop version made with Python Tkinter.

HOW TO RUN (from this folder):
    python main.py

Demo accounts:
    Student     student@college.edu     / student123
    Instructor  instructor@college.edu  / instructor123

How it works:
  On the website every page was its own HTML file, and links moved you between them.
  Here there is ONE window. app.show("page-name") clears the window and builds the
  page you asked for. Each page lives in its own file inside the pages/ folder.
"""

import math
import tkinter as tk
from tkinter import messagebox

import data
import theme
from background import Background
from border import Border
from pages import (create_quiz, history, home, instructor, leaderboard, login, profile,
                   register, results, student, take_quiz)

# page name -> (file that builds it, who may see it)
#   None = anyone, "user" = anyone logged in, "student" / "instructor" = only that role
PAGES = {
    "home": (home, None),
    "login": (login, None),
    "register": (register, None),
    "student-dashboard": (student, "student"),
    "instructor-dashboard": (instructor, "instructor"),
    "take-quiz": (take_quiz, "user"),
    "results": (results, "user"),
    "leaderboard": (leaderboard, "user"),
    "history": (history, "student"),
    "profile": (profile, "user"),
    "create-quiz": (create_quiz, "instructor"),
}


class App:
    def __init__(self):
        self.root = tk.Tk()
        theme.init_fonts(self.root)
        self.root.title("QuizSphere — Quiz Assessment Platform")
        self.root.geometry("1180x780")
        self.root.minsize(900, 620)
        self.root.configure(bg=theme.BG)
        try:
            self.root.state("zoomed")              # start full-screen on Windows
        except tk.TclError:
            try:
                self.root.attributes("-zoomed", True)   # Linux
            except tk.TclError:
                pass
        # One click listener for the whole app: clicks make nearby background shapes spin
        self.root.bind_all("<Button-1>", lambda e: self.page and self.page.background.poke(e), add="+")
        self.page = None
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

        self.frame = None          # the page currently on screen
        self.leave_check = None    # a page can set this to ask "are you sure?" before leaving
        self.current = None

        user = data.get_current_user()
        self.show(self.dashboard_for(user) if user else "home")

    # ------------------------------------------------------------- navigation

    @staticmethod
    def dashboard_for(user):
        return "instructor-dashboard" if user and user["role"] == "instructor" else "student-dashboard"

    def show(self, name, **options):
        """Clear the window and build page `name`. `options` are passed to the page
        (like ?id=... in the website's address bar)."""
        if self.leave_check and not self.leave_check():
            return  # the page said "stay here"
        self.leave_check = None

        module, guard = PAGES[name]
        user = data.get_current_user()
        if guard and not user:                       # must log in first
            module, name = login, "login"
        elif guard in ("student", "instructor") and user["role"] != guard:
            name = self.dashboard_for(user)          # wrong role: go to own dashboard
            module = PAGES[name][0]

        if self.frame is not None:
            self.frame.destroy()
        self.current = name
        self.frame = tk.Frame(self.root, bg=theme.BG)
        self.frame.pack(fill="both", expand=True)

        self._navbar(name, user)
        self._footer()

        page = theme.ScrollPage(self.frame)
        page.pack(fill="both", expand=True)
        # Floating 3D shapes behind the page (slower and calmer on the quiz screen)
        # shapes=False: the old 3D wireframe shapes are switched off, only the flower border shows.
        # Change it to True to bring them back.
        page.background = Background(page.canvas, calm=(name == "take-quiz"), shapes=False)
        # Flower vines + gently floating flowers in the space beside the page
        page.border = Border(page.canvas, lambda: (page.body.winfo_x(), page.body.winfo_x() + page.body.winfo_width()),
                             calm=(name == "take-quiz"))
        self.page = page
        module.build(self, page, **options)

    def _footer(self):
        foot = tk.Frame(self.frame, bg=theme.BG_2, pady=8)
        foot.pack(side="bottom", fill="x")
        tk.Label(foot, text="Front-end developer:  Sumedha Sil  ·  SRM KTR  ·  CSE Core  ·  RA2611003011378",
                 font=theme.font(10, "bold"), bg=theme.BG_2, fg=theme.GOLD).pack()
        tk.Label(foot, text="© 2026 QuizSphere · Offline Demo Mode", font=theme.font(9),
                 bg=theme.BG_2, fg=theme.MUTED).pack()

    def _navbar(self, current, user):
        bar = tk.Frame(self.frame, bg=theme.BG_2, padx=24, pady=10)
        bar.pack(side="top", fill="x")

        logo = tk.Frame(bar, bg=theme.BG_2, cursor="hand2")
        logo.pack(side="left")
        # Logo: a small gold flower with a pink centre
        mark = tk.Canvas(logo, width=28, height=28, bg=theme.BG_2, highlightthickness=0)
        for i in range(6):
            a = i * math.tau / 6
            x, y = 14 + 7 * math.cos(a), 14 + 7 * math.sin(a)
            mark.create_oval(x - 5.5, y - 5.5, x + 5.5, y + 5.5, fill=theme.GOLD, outline=theme.GOLD_DARK)
        mark.create_oval(9, 9, 19, 19, fill="#f472b6", outline="")
        mark.pack(side="left", padx=(0, 8))
        name = tk.Label(logo, text="QuizSphere", font=theme.head_font(15), bg=theme.BG_2, fg=theme.WHITE)
        name.pack(side="left")
        for w in (logo, mark, name):
            w.bind("<Button-1>", lambda e: self.show("home"))

        if not user:
            links = [("Home", "home"), ("Log in", "login"), ("Register", "register")]
        elif user["role"] == "instructor":
            links = [("Dashboard", "instructor-dashboard"), ("Create quiz", "create-quiz"),
                     ("Leaderboard", "leaderboard"), ("Profile", "profile")]
        else:
            links = [("Dashboard", "student-dashboard"), ("History", "history"),
                     ("Leaderboard", "leaderboard"), ("Profile", "profile")]

        right = tk.Frame(bar, bg=theme.BG_2)
        right.pack(side="right")
        for label, target in links:
            kind = "nav-active" if target == current else "nav"
            theme.Button(right, label, lambda t=target: self.show(t), kind=kind, size=10,
                         padx=12, pady=6).pack(side="left", padx=2)
        if user:
            theme.Button(right, "Log out", self.logout, kind="ghost", size=10,
                         padx=12, pady=6).pack(side="left", padx=(10, 0))

    def logout(self):
        if self.leave_check and not self.leave_check():
            return
        self.leave_check = None
        data.logout()
        self.show("login")

    def quit(self):
        if self.leave_check and not messagebox.askyesno(
                "Quit QuizSphere?", "You are in the middle of a quiz. Quit anyway? This attempt will not be saved."):
            return
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    App().run()
