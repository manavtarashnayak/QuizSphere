"""Home screen: big welcome, a turning flower and the feature list."""

import tkinter as tk

import data
import effects
import theme
from pages.common import card_hover

FEATURES = [
    ("01", "Timed quizzes", "A countdown clock and a shrinking time bar keep every attempt fair and focused."),
    ("02", "Instant results", "See your score straight away and review every answer, with confetti for great scores."),
    ("03", "Achievement badges", "Unlock badges for your first quiz, perfect scores, streaks and trying every subject."),
    ("04", "Leaderboard", "See where you rank in your class, with gold, silver and bronze for the top three."),
    ("05", "Attempt history", "Look back at every quiz you have taken and filter by subject."),
    ("06", "Easy for instructors", "Create quizzes in minutes and track attempts, average scores and pass rates."),
]


def build(app, page):
    body = page.body
    user = data.get_current_user()

    # Hero: text on the left, turning flower on the right
    hero = tk.Frame(body, bg=theme.BG)
    hero.pack(fill="x", pady=(40, 30))
    left = tk.Frame(hero, bg=theme.BG)
    left.pack(side="left", fill="both", expand=True)
    theme.eyebrow(left, "Quiz Assessment Platform").pack(fill="x")
    theme.heading(left, "Assess smarter.", size=40).pack(fill="x", pady=(8, 0))
    theme.heading(left, "Learn better.", size=40, fg=theme.GOLD).pack(fill="x")
    theme.text(left, "Students take timed quizzes and see instant results. Instructors create quizzes "
                     "in minutes. All in one calm, simple place.", size=13, wrap=520).pack(fill="x", pady=(18, 0))

    actions = tk.Frame(left, bg=theme.BG)
    actions.pack(fill="x", pady=(24, 0))
    start_target = app.dashboard_for(user) if user else "login"
    theme.Button(actions, "Get started", lambda: app.show(start_target)).pack(side="left")
    theme.Button(actions, "See features", lambda: page.canvas.yview_moveto(0.45),
                 kind="ghost").pack(side="left", padx=12)

    effects.FlowerBloom(hero, size=330).pack(side="right", padx=(20, 0))

    # Feature cards, 3 per row
    theme.eyebrow(body, "Features").pack(fill="x", pady=(30, 0))
    theme.heading(body, "Everything you need for a quiz day", size=24).pack(fill="x", pady=(6, 14))
    grid = tk.Frame(body, bg=theme.BG)
    grid.pack(fill="x", pady=(0, 30))
    theme.grid_columns(grid, 3)
    for i, (num, title, desc) in enumerate(FEATURES):
        box = theme.card(grid, padx=22, pady=22)
        box.grid(row=i // 3, column=i % 3, sticky="nsew", padx=8, pady=8)
        n = tk.Label(box, text=num, font=theme.head_font(14), bg="#2a2016", fg=theme.GOLD, padx=10, pady=6)
        n.pack(anchor="w")
        t = theme.heading(box, title, size=14, bg=theme.CARD)
        t.pack(fill="x", pady=(14, 6))
        d = theme.text(box, desc, size=10, bg=theme.CARD, wrap=280)
        d.pack(fill="x")
        card_hover(box, theme.GOLD, (n, t, d))
