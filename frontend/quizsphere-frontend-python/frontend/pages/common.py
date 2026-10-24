"""Small pieces several pages share."""

import tkinter as tk

import data
import effects
import theme


def topic_tag(parent, topic, bg=theme.CARD):
    """Coloured subject label, e.g. "Maths" in gold."""
    return theme.pill(parent, data.TOPIC_NAMES.get(topic, "Mixed"), bg=bg, color=theme.TOPIC_COLORS.get(topic, theme.CYAN))


def badge_grid(parent, attempts, fresh=None, bg=theme.BG):
    """Draw all 6 achievement coins in a row. Returns how many are unlocked."""
    unlocked = data.unlocked_ids(attempts)
    row = tk.Frame(parent, bg=bg)
    row.pack(fill="x", pady=(10, 0))
    for i, badge in enumerate(data.BADGES):
        coin = effects.BadgeCoin(row, badge, badge["id"] in unlocked,
                                 fresh=bool(fresh) and badge["id"] in fresh, bg=bg)
        coin.grid(row=0, column=i, padx=4, pady=4)
        row.grid_columnconfigure(i, weight=1)
    return len(unlocked)


def section(parent, title, top=36):
    """A section heading with space above it."""
    theme.heading(parent, title, size=18).pack(fill="x", pady=(top, 4))


def stat_card(parent, label, value, column, bg=theme.CARD):
    box = theme.card(parent)
    box.grid(row=0, column=column, sticky="nsew", padx=8, pady=8)
    theme.text(box, label, size=10, bg=bg, fg=theme.MUTED).pack(fill="x")
    lbl = tk.Label(box, text=value, font=theme.head_font(28), bg=bg, fg=theme.GOLD, anchor="w")
    lbl.pack(fill="x", pady=(4, 0))
    return lbl


def card_hover(card, color, widgets=(), on_enter=None, on_leave=None):
    """Light up a card's border in its subject colour when the mouse is over it."""
    def on(_e):
        card.config(highlightbackground=color)
        if on_enter:
            on_enter()

    def off(_e):
        card.config(highlightbackground=theme.BORDER)
        if on_leave:
            on_leave()
    for w in (card, *widgets):
        w.bind("<Enter>", on, add="+")
        w.bind("<Leave>", off, add="+")
