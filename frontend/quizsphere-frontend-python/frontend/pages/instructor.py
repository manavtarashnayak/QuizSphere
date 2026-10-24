"""Instructor dashboard (instructor-dashboard.html): totals and a table of every quiz."""

import tkinter as tk

import data
import theme
from pages.common import stat_card

COLUMNS = ["Quiz", "Subject", "Questions", "Time", "Attempts", "Average", "Pass rate"]


def build(app, page):
    body = page.body
    teacher = data.get_current_user()
    quizzes = data.get_quizzes()
    attempts = data.get_all_attempts()
    overall = data.summarise(attempts)

    head = tk.Frame(body, bg=theme.BG)
    head.pack(fill="x", pady=(30, 10))
    left = tk.Frame(head, bg=theme.BG)
    left.pack(side="left", fill="x", expand=True)
    theme.eyebrow(left, "Instructor dashboard").pack(fill="x")
    theme.heading(left, f"Welcome, {teacher['name']}", size=28).pack(fill="x")
    theme.Button(head, "+ Create quiz", lambda: app.show("create-quiz")).pack(side="right")

    stats = tk.Frame(body, bg=theme.BG)
    stats.pack(fill="x")
    theme.grid_columns(stats, 4)
    stat_card(stats, "Total quizzes", str(len(quizzes)), 0)
    stat_card(stats, "Total attempts", str(len(attempts)), 1)
    stat_card(stats, "Average score", overall["average"], 2)
    stat_card(stats, "Pass rate", overall["passRate"], 3)

    theme.heading(body, "Quizzes and participation", size=18).pack(fill="x", pady=(30, 0))
    theme.text(body, "Each quiz with number of attempts, average score and pass rate",
               size=10, fg=theme.MUTED).pack(fill="x", pady=(0, 10))

    # The table: one header row, then one row per quiz
    table = theme.card(body, padx=0, pady=0)
    table.pack(fill="x", pady=(0, 30))
    table.grid_columnconfigure(0, weight=3)
    for c in range(1, len(COLUMNS)):
        table.grid_columnconfigure(c, weight=1)
    for c, name in enumerate(COLUMNS):
        tk.Label(table, text=name.upper(), font=theme.font(9, "bold"), bg=theme.BG_2, fg=theme.GOLD,
                 anchor="w", padx=14, pady=10).grid(row=0, column=c, sticky="nsew")

    for r, quiz in enumerate(quizzes, start=1):
        mine = [a for a in attempts if a["quizId"] == quiz["id"]]
        s = data.summarise(mine)
        topic = data.theme_of(quiz)
        values = [quiz["title"], data.TOPIC_NAMES[topic], len(quiz["questions"]), f"{quiz['minutes']} min",
                  len(mine), s["average"], s["passRate"]]
        cells = []
        for c, value in enumerate(values):
            cell = tk.Label(table, text=str(value), font=theme.font(11, "bold" if c == 0 else "normal"),
                            bg=theme.CARD, fg=theme.TOPIC_COLORS[topic] if c == 1 else theme.WHITE,
                            anchor="w", padx=14, pady=10)
            cell.grid(row=r, column=c, sticky="nsew")
            cells.append(cell)

        def hover(on, row_cells=cells, t=topic):   # light up the whole row under the mouse
            for cell in row_cells:
                cell.config(bg=theme.CARD_HOVER if on else theme.CARD)
            page.background.set_theme(t if on else "mix")
        for cell in cells:
            cell.bind("<Enter>", lambda e, h=hover: h(True))
            cell.bind("<Leave>", lambda e, h=hover: h(False))
