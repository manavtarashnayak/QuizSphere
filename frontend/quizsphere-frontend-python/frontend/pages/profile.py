"""Profile (profile.html): account details and changing your display name."""

import tkinter as tk

import data
import theme


def build(app, page):
    person = data.get_current_user()
    page.shrink_wrap()
    outer = tk.Frame(page.body, bg=theme.DEEP)
    outer.pack(pady=40)
    box = theme.card(outer, padx=36, pady=30)
    box.pack()
    bg = theme.CARD

    # Round avatar with the person's initials
    avatar = tk.Canvas(box, width=96, height=96, bg=bg, highlightthickness=0)
    avatar.pack()
    avatar.create_oval(4, 4, 92, 92, fill=theme.GOLD, outline=theme.GOLD_DARK, width=3)
    letters = avatar.create_text(48, 48, text=data.initials(person["name"]), fill=theme.BG, font=theme.head_font(24))

    theme.heading(box, "Your profile", size=24, bg=bg).pack(pady=(14, 4))
    theme.pill(box, "Instructor" if person["role"] == "instructor" else "Student", bg=bg).pack()

    theme.text(box, "Email", size=10, bg=bg, fg=theme.MUTED).pack(fill="x", pady=(22, 0))
    theme.text(box, person["email"], size=12, bg=bg, fg=theme.WHITE).pack(fill="x")

    name = theme.field(box, "Display name", width=40)
    name.insert(0, person["name"])
    note = theme.message(box)
    note.pack(fill="x", pady=(10, 0))

    # Live preview of the initials while typing
    def preview(_e=None):
        note.hide()
        avatar.itemconfigure(letters, text=data.initials(name.get().strip() or "?"))

    watch = tk.StringVar(value=name.get())
    name.config(textvariable=watch)
    name.watch = watch   # keep it alive (Python would otherwise throw it away)
    watch.trace_add("write", lambda *_: preview())

    def save(_e=None):
        note.hide()
        new_name = " ".join(name.get().split())
        if len(new_name) < 2:
            note.show("Please enter a name with at least 2 characters.")
            return
        data.update_user_name(person["email"], new_name)
        name.delete(0, "end")
        name.insert(0, new_name)
        preview()
        note.show(f'Saved! Your dashboard and the leaderboard will now show "{new_name}".', ok=True)

    name.bind("<Return>", save)
    theme.Button(box, "Save name", save).pack(fill="x", pady=(14, 0))
