"""Results screen (results.html): score ring, confetti, trophy, badges and answer review."""

import tkinter as tk

import data
import effects
import theme
from pages.common import badge_grid


def build(app, page, attempt_id=None, new=False):
    viewer = data.get_current_user()
    mine = data.get_attempts(viewer["email"])
    attempt = next((a for a in mine if a["id"] == attempt_id), None)
    quiz = attempt and data.get_quiz(attempt["quizId"])
    if not attempt or not quiz:
        page.after(1, lambda: app.show(app.dashboard_for(viewer)))
        return

    body = page.body
    passed = attempt["percent"] >= data.PASS_MARK
    page.background.set_theme(data.theme_of(quiz))

    # ---- Banner: a canvas so the confetti can fly over it
    banner = tk.Canvas(body, height=240, bg=theme.CARD, highlightthickness=1, highlightbackground=theme.BORDER)
    banner.pack(fill="x", pady=(28, 0))
    ring_color = theme.GOLD if passed else theme.DANGER
    cx, cy, r = 130, 120, 76
    banner.create_oval(cx - r, cy - r, cx + r, cy + r, outline=theme.BORDER, width=14)
    arc = banner.create_arc(cx - r, cy - r, cx + r, cy + r, start=90, extent=0, style="arc",
                            outline=ring_color, width=14)
    number = banner.create_text(cx, cy, text="0%", fill=theme.WHITE, font=theme.head_font(28))

    x = 250
    label = "Passed" if passed else "Not passed"
    banner.create_text(x, 46, text="RESULT", fill=theme.GOLD, font=theme.font(9, "bold"), anchor="w")
    banner.create_text(x + 70, 46, text=label, fill=theme.SUCCESS if passed else theme.DANGER,
                       font=theme.font(10, "bold"), anchor="w")
    banner.create_text(x, 82, text=quiz["title"], fill=theme.WHITE, font=theme.head_font(24), anchor="w")
    banner.create_text(x, 124, anchor="w", width=560, fill=theme.TEXT_SOFT, font=theme.font(12),
                       text=f"You answered {attempt['correct']} out of {attempt['total']} questions correctly. "
                            f"Pass mark is {data.PASS_MARK}%.")
    buttons = tk.Frame(banner, bg=theme.CARD)
    theme.Button(buttons, "Back to dashboard", lambda: app.show(app.dashboard_for(viewer)), kind="ghost").pack(side="left")
    theme.Button(buttons, "Try again", lambda: app.show("take-quiz", quiz_id=quiz["id"])).pack(side="left", padx=10)
    banner.create_window(x, 182, window=buttons, anchor="w")

    # Fill the ring and count the number up from 0
    def count_up(shown=0):
        if not banner.winfo_exists():
            return
        shown = min(shown + 2, attempt["percent"])
        banner.itemconfigure(arc, extent=-3.6 * shown if shown < 100 else -359.9)
        banner.itemconfigure(number, text=f"{shown}%")
        if shown < attempt["percent"]:
            banner.after(25, count_up, shown)

    banner.after(200, count_up)
    if attempt["percent"] >= 80:          # celebrate great scores with confetti
        banner.after(900, lambda: effects.confetti(banner))

    # ---- Perfect score: spinning trophy
    if attempt["percent"] == 100:
        box = theme.card(body, padx=24, pady=16)
        box.pack(fill="x", pady=(18, 0))
        effects.Trophy(box, size=150).pack(side="left")
        words = tk.Frame(box, bg=theme.CARD)
        words.pack(side="left", padx=20)
        theme.eyebrow(words, "Perfect score", bg=theme.CARD).pack(fill="x")
        theme.heading(words, "You earned the gold trophy!", size=20, bg=theme.CARD).pack(fill="x", pady=4)
        theme.text(words, "Every single answer was correct. Brilliant work.", bg=theme.CARD, size=12).pack(fill="x")

    # ---- Badge showcase (badges this attempt just unlocked spin in)
    fresh = []
    if new and mine and mine[-1]["id"] == attempt["id"]:   # only right after submitting
        before = data.unlocked_ids(mine[:-1])
        fresh = [b for b in data.unlocked_ids(mine) if b not in before]
    eyebrow = "New achievement" if fresh else "Badge showcase"
    title = ("Badge unlocked!" if len(fresh) == 1 else f"{len(fresh)} badges unlocked!") if fresh else "Your badges"
    theme.eyebrow(body, eyebrow).pack(fill="x", pady=(34, 0))
    theme.heading(body, title, size=18).pack(fill="x")
    count = theme.text(body, "", size=10, fg=theme.MUTED)
    count.pack(fill="x")
    earned = badge_grid(body, mine, fresh=fresh)
    count.config(text=f"{earned} of {len(data.BADGES)} badges unlocked")

    # ---- Review: your answer vs the correct answer
    theme.heading(body, "Review your answers", size=18).pack(fill="x", pady=(34, 8))
    for i, q in enumerate(quiz["questions"]):
        chosen = attempt["answers"][i] if i < len(attempt["answers"]) else None
        right = chosen == q["answer"]
        item = theme.card(body, padx=22, pady=14)
        item.config(highlightbackground=theme.BORDER if right else theme.DANGER)
        item.pack(fill="x", pady=5)
        head = tk.Frame(item, bg=theme.CARD)
        head.pack(fill="x")
        theme.text(head, f"{i + 1}. {q['text']}", size=12, bg=theme.CARD, fg=theme.WHITE, weight="bold",
                   wrap=760).pack(side="left")
        theme.text(head, "✓ Correct" if right else "✗ Incorrect", size=10, weight="bold", bg=theme.CARD,
                   fg=theme.SUCCESS if right else theme.DANGER).pack(side="right")
        theme.text(item, "Your answer: " + ("Not answered" if chosen is None else q["options"][chosen]),
                   bg=theme.CARD).pack(fill="x", pady=(6, 0))
        theme.text(item, "Correct answer: " + q["options"][q["answer"]], bg=theme.CARD).pack(fill="x")
    tk.Frame(body, bg=theme.BG, height=30).pack()
