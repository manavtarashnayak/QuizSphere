"""Instructor dashboard (instructor-dashboard.html): totals and a table of every quiz."""

import tkinter as tk

import api
import data
import theme
from pages.common import stat_card

COLUMNS = ["Quiz", "Subject", "Questions", "Time", "Attempts", "Average", "Pass rate"]


def build(app, page):
    body = page.body
    teacher = data.get_current_user()
    if not teacher:
        page.after(1, lambda: app.show("login"))
        return

    is_online = api.is_backend_online()

    quizzes_map = {q["id"]: q for q in data.get_quizzes()}
    if is_online:
        live_quizzes = api.fetch_quizzes()
        if live_quizzes:
            for lq in live_quizzes:
                qid = lq["id"]
                q_count = lq.get("question_count", 0)
                local_q = quizzes_map.get(qid, {})
                local_questions = local_q.get("questions", [])
                if len(local_questions) < q_count:
                    placeholder_questions = local_questions + [
                        {"id": f"{qid}_q{k+1}", "text": f"Question {k+1}", "options": ["A", "B"], "answer": 0}
                        for k in range(len(local_questions), q_count)
                    ]
                else:
                    placeholder_questions = local_questions

                quizzes_map[qid] = {
                    "id": qid,
                    "title": lq["title"],
                    "description": lq.get("description", ""),
                    "theme": data.theme_of(lq),
                    "category": lq.get("category", "General"),
                    "minutes": lq.get("duration_minutes", 10),
                    "questions": placeholder_questions,
                    "live": True,
                }

    quizzes = list(quizzes_map.values())
    attempts = data.get_all_attempts()
    overall = data.summarise(attempts)

    head = tk.Frame(body, bg=theme.BG)
    head.pack(fill="x", pady=(30, 10))
    left = tk.Frame(head, bg=theme.BG)
    left.pack(side="left", fill="x", expand=True)
    theme.eyebrow(left, "Instructor dashboard").pack(fill="x")
    theme.heading(left, f"Welcome, {teacher['name']}", size=28).pack(fill="x")

    badge_text = "● Live Server" if is_online else "○ Offline Mode"
    badge_color = theme.SUCCESS if is_online else theme.MUTED
    theme.pill(left, badge_text, color=badge_color, bg=theme.CARD).pack(anchor="w", pady=(4, 0))

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
        mine = [a for a in attempts if a.get("quizId") == quiz["id"]]
        s = data.summarise(mine)
        topic = data.theme_of(quiz)
        topic_name = data.TOPIC_NAMES.get(topic, quiz.get("category", "General"))
        values = [quiz["title"], topic_name, len(quiz.get("questions", [])), f"{quiz.get('minutes', 10)} min",
                  len(mine), s["average"], s["passRate"]]
        cells = []
        for c, value in enumerate(values):
            cell = tk.Label(table, text=str(value), font=theme.font(11, "bold" if c == 0 else "normal"),
                            bg=theme.CARD, fg=theme.TOPIC_COLORS.get(topic, theme.CYAN) if c == 1 else theme.WHITE,
                            anchor="w", padx=14, pady=10)
            cell.grid(row=r, column=c, sticky="nsew")
            cells.append(cell)

        def hover(on, row_cells=cells, t=topic):
            for cell in row_cells:
                cell.config(bg=theme.CARD_HOVER if on else theme.CARD)
            page.background.set_theme(t if on else "mix")
        for cell in cells:
            cell.bind("<Enter>", lambda e, h=hover: h(True))
            cell.bind("<Leave>", lambda e, h=hover: h(False))
