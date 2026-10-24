"""Take quiz screen (take-quiz.html): one question at a time, countdown timer,
question palette and a Submit button."""

import tkinter as tk
from tkinter import messagebox

import data
import theme

LETTERS = ["A", "B", "C", "D"]


def build(app, page, quiz_id=None):
    student = data.get_current_user()
    quiz = data.get_quiz(quiz_id)
    if not quiz:
        page.after(1, lambda: app.show("student-dashboard"))
        return

    questions = quiz["questions"]
    total_seconds = quiz["minutes"] * 60
    state = {"current": 0, "answers": [None] * len(questions), "left": total_seconds, "finished": False}
    color = theme.TOPIC_COLORS[data.theme_of(quiz)]
    page.background.set_theme(data.theme_of(quiz))   # background shows this subject's shapes
    body = page.body

    # ---- Top: quiz name, timer and bars
    top = tk.Frame(body, bg=theme.BG)
    top.pack(fill="x", pady=(26, 8))
    left = tk.Frame(top, bg=theme.BG)
    left.pack(side="left", fill="x", expand=True)
    theme.eyebrow(left, data.TOPIC_NAMES[data.theme_of(quiz)], fg=color).pack(fill="x")
    theme.heading(left, quiz["title"], size=24).pack(fill="x")
    clock = tk.Frame(top, bg=theme.BG)
    clock.pack(side="right")
    timer = tk.Label(clock, text="", font=theme.head_font(26), bg=theme.BG, fg=theme.GOLD)
    timer.pack(anchor="e")
    theme.text(clock, "Time left", size=9, fg=theme.MUTED).pack(anchor="e")

    time_bar = tk.Canvas(body, height=8, bg=theme.BORDER, highlightthickness=0)
    time_bar.pack(fill="x", pady=(4, 10))
    answered_row = tk.Frame(body, bg=theme.BG)
    answered_row.pack(fill="x")
    theme.text(answered_row, "Answered", size=9, fg=theme.MUTED).pack(side="left")
    progress = tk.Canvas(answered_row, height=6, bg=theme.BORDER, highlightthickness=0)
    progress.pack(side="left", fill="x", expand=True, padx=(10, 0))

    # ---- Middle: question card on the left, palette on the right
    middle = tk.Frame(body, bg=theme.BG)
    middle.pack(fill="x", pady=(18, 30))
    qcard = theme.card(middle, padx=28, pady=24)
    qcard.pack(side="left", fill="both", expand=True)
    counter = theme.text(qcard, "", size=10, bg=theme.CARD, fg=theme.GOLD, weight="bold")
    counter.pack(fill="x")
    qtext = theme.heading(qcard, "", size=17, bg=theme.CARD, wraplength=560)
    qtext.pack(fill="x", pady=(8, 16))
    options_box = tk.Frame(qcard, bg=theme.CARD)
    options_box.pack(fill="x")
    nav = tk.Frame(qcard, bg=theme.CARD)
    nav.pack(fill="x", pady=(20, 0))
    prev_btn = theme.Button(nav, "Previous", lambda: move(-1), kind="ghost")
    prev_btn.pack(side="left")
    next_btn = theme.Button(nav, "Next", lambda: move(1), kind="ghost")
    next_btn.pack(side="right")

    side = theme.card(middle, padx=20, pady=20)
    side.pack(side="right", fill="y", padx=(16, 0))
    theme.text(side, "Questions", size=11, bg=theme.CARD, fg=theme.WHITE, weight="bold").pack(fill="x")
    palette = tk.Frame(side, bg=theme.CARD)
    palette.pack(pady=(10, 18))
    pal_buttons = []
    for i in range(len(questions)):
        b = theme.Button(palette, str(i + 1), lambda n=i: go(n), kind="ghost", size=11, padx=12, pady=6)
        b.grid(row=i // 5, column=i % 5, padx=3, pady=3)
        pal_buttons.append(b)
    theme.Button(side, "Submit quiz", lambda: ask_submit()).pack(fill="x", side="bottom")

    # ---- Drawing the current question
    def show_question():
        i = state["current"]
        q = questions[i]
        counter.config(text=f"Question {i + 1} of {len(questions)}")
        qtext.config(text=q["text"])
        for w in options_box.winfo_children():
            w.destroy()
        for n, option in enumerate(q["options"]):
            chosen = state["answers"][i] == n
            row = tk.Frame(options_box, bg=theme.CARD_HOVER if chosen else theme.INPUT, cursor="hand2",
                           highlightthickness=2 if chosen else 1,
                           highlightbackground=theme.GOLD if chosen else theme.BORDER)
            row.pack(fill="x", pady=5)
            letter = tk.Label(row, text=LETTERS[n], font=theme.font(11, "bold"), width=3, pady=8,
                              bg=theme.GOLD if chosen else theme.BORDER, fg=theme.BG if chosen else theme.WHITE)
            letter.pack(side="left", padx=10, pady=8)
            words = tk.Label(row, text=option, font=theme.font(12), bg=row.cget("bg"), fg=theme.WHITE,
                             anchor="w", justify="left", wraplength=480)
            words.pack(side="left", fill="x", expand=True)
            for w in (row, letter, words):
                w.bind("<Button-1>", lambda e, pick=n: choose(pick))

        prev_btn.set_enabled(i > 0)
        next_btn.set_enabled(i < len(questions) - 1)
        for n, b in enumerate(pal_buttons):
            if n == i:
                b.set_colors(theme.GOLD, theme.BG, theme.GOLD_DARK)
            elif state["answers"][n] is not None:
                b.set_colors("#16362a", theme.SUCCESS, theme.SUCCESS)
            else:
                b.set_colors(theme.CARD, theme.WHITE, theme.BORDER)
        draw_bar(progress, sum(a is not None for a in state["answers"]) / len(questions), theme.CYAN)

    def draw_bar(canvas, fraction, fill):
        canvas.delete("all")
        width = canvas.winfo_width() or 600
        canvas.create_rectangle(0, 0, width * fraction, 10, fill=fill, outline="")

    def choose(n):
        state["answers"][state["current"]] = n
        show_question()

    def go(n):
        state["current"] = n
        show_question()

    def move(step):
        n = state["current"] + step
        if 0 <= n < len(questions):
            go(n)

    # ---- Countdown timer (runs once a second)
    def tick():
        if state["finished"] or not timer.winfo_exists():
            return
        left = state["left"]
        timer.config(text=f"{left // 60:02d}:{left % 60:02d}", fg=theme.DANGER if left <= 30 else theme.GOLD)
        fraction = left / total_seconds
        draw_bar(time_bar, fraction, theme.DANGER if left <= 30 or fraction <= 0.2 else color)
        if left <= 0:
            finish()   # time is up: hand it in automatically
            return
        state["left"] -= 1
        timer.after(1000, tick)

    # ---- Submitting
    def ask_submit():
        unanswered = sum(a is None for a in state["answers"])
        msg = (f"You have {unanswered} unanswered question(s). You cannot change answers after submitting."
               if unanswered else "All questions answered. You cannot change answers after submitting.")
        if messagebox.askyesno("Submit quiz?", msg + "\n\nSubmit now?"):
            finish()

    def finish():
        if state["finished"]:
            return  # stop double submits
        state["finished"] = True
        app.leave_check = None
        correct = sum(1 for q, a in zip(questions, state["answers"]) if a == q["answer"])
        attempt = {
            "id": data.new_id(),
            "email": student["email"],
            "quizId": quiz["id"],
            "quizTitle": quiz["title"],
            "answers": state["answers"],
            "correct": correct,
            "total": len(questions),
            "percent": data.js_round(correct / len(questions) * 100),
            "date": data.now_iso(),
        }
        data.save_attempt(attempt)
        app.show("results", attempt_id=attempt["id"], new=True)  # new=True shows fresh badges once

    # Ask before leaving the quiz half-way
    def ok_to_leave():
        if state["finished"]:
            return True
        if messagebox.askyesno("Leave this quiz?", "Your answers will be lost if you leave now. Leave anyway?"):
            state["finished"] = True
            return True
        return False

    time_bar.bind("<Configure>", lambda e: draw_bar(
        time_bar, state["left"] / total_seconds, theme.DANGER if state["left"] <= 30 else color))
    app.leave_check = ok_to_leave
    progress.bind("<Configure>", lambda e: show_question())
    show_question()
    tick()
