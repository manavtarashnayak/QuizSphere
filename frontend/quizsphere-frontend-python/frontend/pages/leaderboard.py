"""Leaderboard (leaderboard.html): real students on this computer + sample classmates,
ranked by average score, with a gold / silver / bronze podium."""

import tkinter as tk

import data
import theme

MEDALS = {1: ("#fbbf24", "#b45309"), 2: ("#e5e7eb", "#6b7280"), 3: ("#f59e0b", "#7c2d12")}


def ranking_for(me):
    # 1. Group real attempts by student email
    by_email = {}
    for a in data.get_all_attempts():
        by_email.setdefault(a["email"], []).append(a["percent"])
    users = data.get_users()
    people = []
    for email, scores in by_email.items():
        account = next((u for u in users if u["email"] == email), None)
        people.append({"name": account["name"] if account else email,
                       "average": data.js_round(sum(scores) / len(scores)),
                       "quizzes": len(scores), "isMe": email == me["email"]})
    # A student with no attempts yet still appears (0%), so they can see where they start
    if me["role"] == "student" and me["email"] not in by_email:
        people.append({"name": me["name"], "average": 0, "quizzes": 0, "isMe": True})

    # 2. Mix in sample classmates; highest average first, then most quizzes
    people += [dict(c, sample=True) for c in data.SAMPLE_CLASSMATES]
    people.sort(key=lambda p: (-p["average"], -p["quizzes"]))
    return people


def tags(person):
    return ("  (You)" if person.get("isMe") else "") + ("  · sample" if person.get("sample") else "")


def build(app, page):
    body = page.body
    me = data.get_current_user()
    ranking = ranking_for(me)

    theme.eyebrow(body, "Class rankings").pack(fill="x", pady=(30, 0))
    theme.heading(body, "Leaderboard", size=28).pack(fill="x")
    theme.text(body, 'Ranked by average score. Names marked "sample" are demo classmates.',
               fg=theme.MUTED).pack(fill="x")

    # ---- Podium: 2nd, 1st, 3rd so the winner stands in the middle
    theme.heading(body, "Top three students", size=16).pack(fill="x", pady=(26, 6))
    podium = tk.Canvas(body, height=330, bg=theme.BG, highlightthickness=0)
    podium.pack(fill="x")

    def draw_podium(_e=None):
        podium.delete("all")
        w = podium.winfo_width() or 900
        col = min(220, w / 3.4)
        heights = {1: 150, 2: 110, 3: 80}
        for slot, rank in enumerate((2, 1, 3)):
            if rank > len(ranking):
                continue
            p = ranking[rank - 1]
            cx = w / 2 + (slot - 1) * (col + 16)
            base = 320
            top = base - heights[rank]
            light, dark = MEDALS[rank]
            podium.create_rectangle(cx - col / 2, top, cx + col / 2, base, fill="#1d1712",
                                    outline=light if p.get("isMe") else theme.BORDER, width=2)
            podium.create_text(cx, top + heights[rank] / 2, text=str(rank), fill=light, font=theme.head_font(30))
            r = 34 if rank == 1 else 28
            ay = top - 100
            podium.create_oval(cx - r, ay - r, cx + r, ay + r, fill=light, outline=dark, width=3)
            podium.create_text(cx, ay, text=data.initials(p["name"]), fill=theme.BG, font=theme.head_font(14))
            podium.create_text(cx, ay + r + 18, text=p["name"] + tags(p), fill=theme.WHITE,
                               font=theme.font(11, "bold"), width=col)
            podium.create_text(cx, ay + r + 42, text=f"{p['average']}%", fill=light, font=theme.head_font(16))
            if rank == 1:
                podium.create_text(cx, ay - r - 14, text="♛", fill=light, font=theme.font(20))

    podium.bind("<Configure>", draw_podium)

    # ---- Everyone from 4th place down
    theme.heading(body, "Everyone else", size=16).pack(fill="x", pady=(20, 6))
    for i, p in enumerate(ranking[3:], start=4):
        row = theme.card(body, padx=18, pady=12)
        if p.get("isMe"):
            row.config(highlightbackground=theme.GOLD, highlightthickness=2)
        row.pack(fill="x", pady=4)
        tk.Label(row, text=f"#{i}", font=theme.head_font(15), bg=theme.CARD, fg=theme.GOLD, width=4,
                 anchor="w").pack(side="left")
        tk.Label(row, text=f"{p['average']}%", font=theme.head_font(16), bg=theme.CARD,
                 fg=theme.WHITE).pack(side="right", padx=(16, 0))
        mid = tk.Frame(row, bg=theme.CARD)
        mid.pack(side="left", fill="x", expand=True)
        theme.text(mid, p["name"] + tags(p), size=12, bg=theme.CARD, fg=theme.WHITE, weight="bold").pack(fill="x")
        hint = "Take a quiz to join the ranking" if p["quizzes"] == 0 else f"{p['quizzes']} quiz(zes)"
        theme.text(mid, hint, size=9, bg=theme.CARD, fg=theme.MUTED).pack(fill="x")
        meter = tk.Canvas(mid, height=6, bg=theme.BORDER, highlightthickness=0)
        meter.pack(fill="x", pady=(6, 0))
        meter.bind("<Configure>", lambda e, m=meter, pct=p["average"]: (
            m.delete("all"), m.create_rectangle(0, 0, e.width * pct / 100, 6, fill=theme.GOLD, outline="")))
    tk.Frame(body, bg=theme.BG, height=30).pack()
