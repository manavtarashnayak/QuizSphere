"""Attempt history (history.html): every past attempt, filtered by subject."""

import tkinter as tk

import data
import theme
from pages.common import topic_tag

FILTERS = [("all", "All"), ("math", "Maths"), ("gk", "General Knowledge"), ("web", "Web & Code"), ("mix", "Mixed")]


def build(app, page):
    body = page.body
    learner = data.get_current_user()

    # Newest first, and remember each attempt's subject
    attempts = []
    for a in reversed(data.get_attempts(learner["email"])):
        quiz = data.get_quiz(a["quizId"])
        attempts.append({"data": a, "topic": data.theme_of(quiz) if quiz else "mix"})

    theme.eyebrow(body, "Student").pack(fill="x", pady=(30, 0))
    theme.heading(body, "Attempt history", size=28).pack(fill="x")

    chips_row = tk.Frame(body, bg=theme.BG)
    chips_row.pack(fill="x", pady=(16, 6))
    count = theme.text(body, "", size=10, fg=theme.MUTED)
    count.pack(fill="x")
    listing = tk.Frame(body, bg=theme.BG)
    listing.pack(fill="x", pady=(8, 30))
    chips = {}

    def render(topic):
        page.background.set_theme("mix" if topic == "all" else topic)
        for key, chip in chips.items():
            if key == topic:
                chip.set_colors(theme.TOPIC_COLORS.get(key, theme.GOLD), theme.BG)
            else:
                chip.set_colors(theme.CARD, theme.TEXT_SOFT, theme.BORDER)
        for w in listing.winfo_children():
            w.destroy()
        shown = [e for e in attempts if topic == "all" or e["topic"] == topic]
        count.config(text=f"Showing {len(shown)} of {len(attempts)} attempt(s)")
        if not shown:
            theme.text(listing, "No attempts for this subject yet.", fg=theme.MUTED).pack(fill="x", pady=10)
            return
        for entry in shown:
            a = entry["data"]
            passed = a["percent"] >= data.PASS_MARK
            item = theme.card(listing, padx=20, pady=14)
            item.pack(fill="x", pady=5)
            info = tk.Frame(item, bg=theme.CARD)
            info.pack(side="left", fill="x", expand=True)
            topic_tag(info, entry["topic"]).pack(anchor="w")
            theme.text(info, a["quizTitle"], size=13, bg=theme.CARD, fg=theme.WHITE, weight="bold").pack(fill="x", pady=(6, 0))
            theme.text(info, f"{data.nice_date(a['date'], with_time=True)} · {a['correct']}/{a['total']} correct",
                       size=9, bg=theme.CARD, fg=theme.MUTED).pack(fill="x")
            theme.Button(item, "View result", lambda x=a: app.show("results", attempt_id=x["id"]),
                         kind="ghost", size=10, pady=6).pack(side="right", padx=(16, 0))
            score = tk.Frame(item, bg=theme.CARD)
            score.pack(side="right")
            tk.Label(score, text=f"{a['percent']}%", font=theme.head_font(20), bg=theme.CARD, fg=theme.GOLD).pack()
            tk.Label(score, text="Passed" if passed else "Not passed", font=theme.font(9, "bold"), bg=theme.CARD,
                     fg=theme.SUCCESS if passed else theme.DANGER).pack()

    for key, label in FILTERS:
        chip = theme.Button(chips_row, label, lambda k=key: render(k), kind="ghost", size=10, padx=14, pady=5)
        chip.pack(side="left", padx=(0, 8))
        chips[key] = chip

    render("all")
