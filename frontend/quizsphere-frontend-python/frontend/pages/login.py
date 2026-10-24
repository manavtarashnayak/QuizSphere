"""Log in screen (login.html)."""

import tkinter as tk

import data
import theme


def role_toggle(parent, var, bg=theme.CARD):
    """Two buttons side by side: Student | Instructor. The chosen one is gold."""
    tk.Label(parent, text="I am a", font=theme.font(10, "bold"), bg=bg, fg=theme.WHITE,
             anchor="w").pack(fill="x", pady=(18, 4))
    row = tk.Frame(parent, bg=bg)
    row.pack(fill="x")
    buttons = {}

    def paint():
        for role, btn in buttons.items():
            if var.get() == role:
                btn.set_colors(theme.GOLD, theme.BG, theme.GOLD_DARK)
            else:
                btn.set_colors(theme.INPUT, theme.TEXT_SOFT, theme.BORDER)

    for role, label in (("student", "Student"), ("instructor", "Instructor")):
        btn = theme.Button(row, label, lambda r=role: (var.set(r), paint()), kind="ghost", pady=8)
        btn.pack(side="left", fill="x", expand=True)
        buttons[role] = btn
    paint()
    return paint


def build(app, page):
    page.shrink_wrap()
    outer = tk.Frame(page.body, bg=theme.DEEP)
    outer.pack(pady=40)
    box = theme.card(outer, padx=36, pady=30)
    box.pack()
    bg = theme.CARD

    theme.pill(box, "Offline Demo Mode", bg=bg).pack(anchor="w")
    theme.heading(box, "Welcome back", size=24, bg=bg).pack(fill="x", pady=(12, 0))
    theme.text(box, "Sign in to take or create quizzes.", bg=bg, size=12).pack(fill="x")

    role = tk.StringVar(value="student")
    repaint = role_toggle(box, role)
    email = theme.field(box, "Email address", placeholder="you@college.edu")
    password = theme.field(box, "Password", show="•", placeholder="Your password")
    error = theme.message(box)
    error.pack(fill="x", pady=(10, 0))

    def submit(_e=None):
        error.hide()
        e, p = theme.value_of(email), theme.value_of(password)
        if not e or not p:
            error.show("Please enter your email and password.")
            return
        user = data.login(e, p, role.get())
        if not user:
            error.show("Email, password or role is not correct. Try a demo account.")
            return
        app.show(app.dashboard_for(user))  # each role goes to its own dashboard

    theme.Button(box, "Sign in", submit).pack(fill="x", pady=(14, 0))
    for w in (email, password):
        w.bind("<Return>", submit)

    # Demo buttons fill in the form for you
    def fill_demo(r):
        user = next(u for u in data.DEMO_USERS if u["role"] == r)
        theme.set_value(email, user["email"])
        theme.set_value(password, user["password"])
        role.set(r)
        repaint()
        error.hide()

    theme.text(box, "Or fill in a demo account", bg=bg, size=10, fg=theme.MUTED).pack(pady=(20, 6))
    demo = tk.Frame(box, bg=bg)
    demo.pack(fill="x")
    theme.Button(demo, "Demo Student", lambda: fill_demo("student"), kind="ghost").pack(side="left", fill="x", expand=True, padx=(0, 6))
    theme.Button(demo, "Demo Instructor", lambda: fill_demo("instructor"), kind="ghost").pack(side="left", fill="x", expand=True, padx=(6, 0))

    bottom = tk.Frame(box, bg=bg)
    bottom.pack(pady=(18, 0))
    theme.text(bottom, "New here?", bg=bg, size=10, fg=theme.MUTED).pack(side="left")
    theme.Button(bottom, "Create an account", lambda: app.show("register"), kind="link", size=10, padx=4, pady=0).pack(side="left")
