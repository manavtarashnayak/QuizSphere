"""Create quiz (create-quiz.html): quiz details plus a question builder."""

import tkinter as tk

import data
import theme

LETTERS = ["A", "B", "C", "D"]
SUBJECTS = [("math", "Maths"), ("gk", "General Knowledge"), ("web", "Web & Code"), ("mix", "Mixed")]


def build(app, page):
    body = page.body
    author = data.get_current_user()
    bg = theme.CARD

    theme.eyebrow(body, "Instructor").pack(fill="x", pady=(30, 0))
    theme.heading(body, "Create a new quiz", size=28).pack(fill="x", pady=(0, 14))

    # ---- Quiz details
    details = theme.card(body, padx=26, pady=20)
    details.pack(fill="x")
    theme.heading(details, "Quiz details", size=16, bg=bg).pack(fill="x")
    title = theme.field(details, "Quiz title", placeholder="e.g. Science Basics")
    desc = theme.field(details, "Short description", placeholder="What is this quiz about?")

    row = tk.Frame(details, bg=bg)
    row.pack(fill="x", pady=(12, 0))
    left = tk.Frame(row, bg=bg)
    left.pack(side="left", fill="x", expand=True, padx=(0, 10))
    tk.Label(left, text="Subject", font=theme.font(10, "bold"), bg=bg, fg=theme.WHITE, anchor="w").pack(fill="x", pady=(0, 4))
    subject = tk.StringVar(value="Maths")
    menu = tk.OptionMenu(left, subject, *[name for _, name in SUBJECTS])
    menu.config(font=theme.font(11), bg=theme.INPUT, fg=theme.WHITE, activebackground=theme.CARD_HOVER,
                activeforeground=theme.WHITE, relief="flat", highlightthickness=1,
                highlightbackground=theme.BORDER, anchor="w")
    menu["menu"].config(bg=theme.INPUT, fg=theme.WHITE, activebackground=theme.GOLD, activeforeground=theme.BG)
    menu.pack(fill="x", ipady=4)
    subject.trace_add("write", lambda *_: page.background.set_theme(
        next(key for key, name in SUBJECTS if name == subject.get())))
    page.background.set_theme("math")

    right = tk.Frame(row, bg=bg)
    right.pack(side="left", fill="x", expand=True, padx=(10, 0))
    tk.Label(right, text="Time limit (minutes)", font=theme.font(10, "bold"), bg=bg, fg=theme.WHITE,
             anchor="w").pack(fill="x", pady=(0, 4))
    minutes = tk.Spinbox(right, from_=1, to=180, font=theme.font(12), bg=theme.INPUT, fg=theme.WHITE,
                         insertbackground=theme.WHITE, buttonbackground=theme.CARD, relief="flat",
                         highlightthickness=1, highlightbackground=theme.BORDER)
    minutes.delete(0, "end")
    minutes.insert(0, "10")
    minutes.pack(fill="x", ipady=6)

    # ---- Question blocks
    question_list = tk.Frame(body, bg=theme.BG)
    question_list.pack(fill="x", pady=(10, 0))
    blocks = []   # each block = {"frame", "legend", "text", "options", "correct"}
    error = theme.message(body, bg=theme.BG)

    def renumber():
        for i, b in enumerate(blocks):
            b["legend"].config(text=f"Question {i + 1}")

    def add_question():
        frame = theme.card(question_list, padx=26, pady=18)
        frame.pack(fill="x", pady=(12, 0))
        legend = theme.heading(frame, "", size=15, bg=bg)
        legend.pack(fill="x")
        text_box = theme.field(frame, "Question text")
        theme.text(frame, "Type the 4 answer choices and select the correct one.", size=9, bg=bg,
                   fg=theme.MUTED).pack(fill="x", pady=(10, 4))
        correct = tk.IntVar(value=0)
        options = []
        for i, letter in enumerate(LETTERS):
            line = tk.Frame(frame, bg=bg)
            line.pack(fill="x", pady=3)
            tk.Radiobutton(line, variable=correct, value=i, bg=bg, activebackground=bg,
                           selectcolor=theme.INPUT, fg=theme.GOLD, highlightthickness=0,
                           cursor="hand2").pack(side="left")
            tk.Label(line, text=letter, font=theme.font(11, "bold"), width=3, bg=theme.BORDER,
                     fg=theme.WHITE, pady=4).pack(side="left", padx=(2, 8))
            box = theme.entry(line, placeholder=f"Option {letter}")
            box.pack(side="left", fill="x", expand=True, ipady=5)
            options.append(box)
        block = {"frame": frame, "legend": legend, "text": text_box, "options": options, "correct": correct}

        def remove():
            if len(blocks) == 1:
                error.show("A quiz needs at least one question.")
                return
            blocks.remove(block)
            frame.destroy()
            renumber()

        theme.Button(frame, "Remove question", remove, kind="ghost", size=10, pady=6).pack(anchor="w", pady=(12, 0))
        blocks.append(block)
        renumber()
        text_box.focus_set()

    def save():
        error.hide()
        quiz_title = theme.value_of(title).strip()
        description = theme.value_of(desc).strip()
        try:
            mins = int(minutes.get())
        except ValueError:
            mins = 0
        if not quiz_title:
            error.show("Please give the quiz a title.")
            return
        if mins < 1 or mins > 180:
            error.show("Time limit must be between 1 and 180 minutes.")
            return
        questions = []
        for n, b in enumerate(blocks, start=1):
            q_text = theme.value_of(b["text"]).strip()
            opts = [theme.value_of(o).strip() for o in b["options"]]
            if not q_text or not all(opts):
                error.show(f"Question {n} needs its text and all 4 options filled in.")
                return
            questions.append({"text": q_text, "options": opts, "answer": b["correct"].get()})
        topic = next(key for key, name in SUBJECTS if name == subject.get())
        data.save_quiz({
            "id": "quiz-" + data.new_id(),
            "title": quiz_title,
            "theme": topic,
            "description": description or f"A quiz created by {author['name']}.",
            "minutes": mins,
            "questions": questions,
        })
        app.show("instructor-dashboard")

    actions = tk.Frame(body, bg=theme.BG)
    actions.pack(fill="x", pady=(16, 0))
    theme.Button(actions, "+ Add question", add_question, kind="ghost").pack(side="left")
    theme.Button(actions, "Save quiz", save).pack(side="right")
    error.pack(fill="x", pady=(10, 30))

    add_question()   # start with one empty question
