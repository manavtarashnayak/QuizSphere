"""Register screen (register.html), with a live password strength meter."""

import re
import tkinter as tk

import data
import theme
from pages.login import role_toggle

LEVEL_WORDS = ["Too short", "Weak", "Fair", "Good", "Strong"]
LEVEL_COLORS = [theme.DANGER, theme.DANGER, "#fb923c", theme.GOLD, theme.SUCCESS]


def password_score(pw):
    """0 to 4: one point for each rule the password follows."""
    score = 0
    if len(pw) >= 8:
        score += 1
    if re.search(r"[A-Z]", pw) and re.search(r"[a-z]", pw):
        score += 1
    if re.search(r"[0-9]", pw):
        score += 1
    if re.search(r"[^A-Za-z0-9]", pw):
        score += 1
    if len(pw) < 8:
        return min(score, 1)  # under 8 characters is always weak
    return score


def build(app, page):
    page.shrink_wrap()
    outer = tk.Frame(page.body, bg=theme.DEEP)
    outer.pack(pady=30)
    box = theme.card(outer, padx=36, pady=28)
    box.pack()
    bg = theme.CARD

    theme.pill(box, "Offline Demo Mode", bg=bg).pack(anchor="w")
    theme.heading(box, "Create your account", size=24, bg=bg).pack(fill="x", pady=(12, 0))
    theme.text(box, "Your account is saved only on this computer.", bg=bg, size=12).pack(fill="x")

    role = tk.StringVar(value="student")
    role_toggle(box, role)
    name = theme.field(box, "Full name", placeholder="e.g. Sumedha Sil")
    email = theme.field(box, "Email address", placeholder="you@college.edu")
    password = theme.field(box, "Password", show="•", placeholder="At least 8 characters")

    # Strength meter: 4 bars that fill up and change colour
    meter = tk.Canvas(box, height=8, bg=bg, highlightthickness=0)
    meter.pack(fill="x", pady=(8, 2))
    hint = theme.text(box, "Use 8+ characters with a capital letter, a number and a symbol.",
                      bg=bg, size=9, fg=theme.MUTED, wrap=420)
    hint.pack(fill="x")

    def update_meter(_e=None):
        pw = theme.value_of(password)
        score = password_score(pw) if pw else 0
        meter.delete("all")
        width = meter.winfo_width() or 420
        gap, bar = 6, (width - 18) / 4
        for i in range(4):
            x = i * (bar + gap)
            color = LEVEL_COLORS[score] if pw and i < max(score, 1) else theme.BORDER
            meter.create_rectangle(x, 0, x + bar, 8, fill=color, outline="")
        hint.config(text=f"Strength: {LEVEL_WORDS[score]}" if pw else
                    "Use 8+ characters with a capital letter, a number and a symbol.")

    watch = tk.StringVar(value=password.get())   # fires on typing AND pasting
    password.config(textvariable=watch)
    password.watch = watch   # keep it alive (Python would otherwise throw it away)
    watch.trace_add("write", lambda *_: update_meter())
    meter.bind("<Configure>", update_meter)

    confirm = theme.field(box, "Confirm password", show="•", placeholder="Type it again")
    error = theme.message(box)
    error.pack(fill="x", pady=(10, 0))

    def submit(_e=None):
        error.hide()
        n = theme.value_of(name).strip()
        e = theme.value_of(email).strip()
        p = theme.value_of(password)
        if not n or not e or not p:
            error.show("Please fill in your name, email and password.")
            return
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", e):
            error.show("Please enter a valid email address.")
            return
        if len(p) < 8 or password_score(p) < 3:
            error.show('Please choose a stronger password (at least "Good").')
            return
        if p != theme.value_of(confirm):
            error.show("The two passwords do not match.")
            return
        if not data.register_user(n, e, p, role.get()):
            error.show("An account with this email already exists. Try logging in.")
            return
        user = data.login(e, p, role.get())  # sign in straight away
        app.show(app.dashboard_for(user))

    theme.Button(box, "Create account", submit).pack(fill="x", pady=(14, 0))
    confirm.bind("<Return>", submit)

    bottom = tk.Frame(box, bg=bg)
    bottom.pack(pady=(18, 0))
    theme.text(bottom, "Already have an account?", bg=bg, size=10, fg=theme.MUTED).pack(side="left")
    theme.Button(bottom, "Log in", lambda: app.show("login"), kind="link", size=10, padx=4, pady=0).pack(side="left")
