"""Student dashboard (student-dashboard.html)."""

import tkinter as tk

import data
import theme
from pages.common import badge_grid, card_hover, section, stat_card, topic_tag


def build(app, page):
    body = page.body
    user = data.get_current_user()
    quizzes = data.get_quizzes()
    attempts = data.get_attempts(user["email"])

    head = tk.Frame(body, bg=theme.BG)
    head.pack(fill="x", pady=(30, 10))
    left = tk.Frame(head, bg=theme.BG)
    left.pack(side="left", fill="x", expand=True)
    theme.eyebrow(left, "Student dashboard").pack(fill="x")
    theme.heading(left, f"Welcome, {user['name']}", size=28).pack(fill="x")
    theme.pill(head, "Offline Demo Mode").pack(side="right")

    # Summary cards
    stats = tk.Frame(body, bg=theme.BG)
    stats.pack(fill="x")
    theme.grid_columns(stats, 3)
    average = f"{data.js_round(sum(a['percent'] for a in attempts) / len(attempts))}%" if attempts else "–"
    stat_card(stats, "Quizzes available", str(len(quizzes)), 0)
    stat_card(stats, "Quizzes taken", str(len(attempts)), 1)
    stat_card(stats, "Average score", average, 2)

    # Achievement badges
    section(body, "Achievement badges")
    count = theme.text(body, "", size=10, fg=theme.MUTED)
    count.pack(fill="x")
    earned = badge_grid(body, attempts)
    count.config(text=f"{earned} of {len(data.BADGES)} unlocked · click a badge to flip it")

    # One card per quiz
    section(body, "Available quizzes")
    grid = tk.Frame(body, bg=theme.BG)
    grid.pack(fill="x")
    theme.grid_columns(grid, 3)
    for i, quiz in enumerate(quizzes):
        topic = data.theme_of(quiz)
        box = theme.card(grid, padx=22, pady=20)
        box.grid(row=i // 3, column=i % 3, sticky="nsew", padx=8, pady=8)
        topic_tag(box, topic).pack(anchor="w")
        title = theme.heading(box, quiz["title"], size=15, bg=theme.CARD)
        title.pack(fill="x", pady=(12, 4))
        desc = theme.text(box, quiz["description"], size=10, bg=theme.CARD, wrap=280)
        desc.pack(fill="x")
        meta = tk.Frame(box, bg=theme.CARD)
        meta.pack(fill="x", pady=(12, 14))
        theme.pill(meta, f"{len(quiz['questions'])} questions", bg=theme.CARD).pack(side="left")
        theme.pill(meta, f"{quiz['minutes']} min", bg=theme.CARD).pack(side="left", padx=6)
        theme.Button(box, "Start quiz", lambda q=quiz: app.show("take-quiz", quiz_id=q["id"])).pack(anchor="w", side="bottom")
        card_hover(box, theme.TOPIC_COLORS[topic], (title, desc, meta),
                   on_enter=lambda t=topic: page.background.set_theme(t),
                   on_leave=lambda: page.background.set_theme("mix"))

    # The 5 most recent attempts
    section(body, "Recent attempts")
    theme.Button(body, "See all attempts in History →", lambda: app.show("history"),
                 kind="link", size=10, padx=0, pady=0).pack(anchor="w")
    if not attempts:
        theme.text(body, "No attempts yet. Pick a quiz above to begin.", fg=theme.MUTED).pack(fill="x", pady=12)
    for a in reversed(attempts[-5:]):
        row = theme.card(body, padx=18, pady=12)
        row.pack(fill="x", pady=5)
        theme.text(row, a["quizTitle"], size=12, bg=theme.CARD, fg=theme.WHITE, weight="bold").pack(side="left")
        theme.text(row, f"   {a['percent']}% · {data.nice_date(a['date'])}", bg=theme.CARD).pack(side="left")
        theme.Button(row, "View result", lambda x=a: app.show("results", attempt_id=x["id"]),
                     kind="ghost", size=10, pady=6).pack(side="right")
    tk.Frame(body, bg=theme.BG, height=30).pack()
