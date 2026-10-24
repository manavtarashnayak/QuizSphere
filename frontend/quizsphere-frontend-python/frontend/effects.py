"""
QuizSphere animations, drawn on Tkinter canvases.

The website used CSS 3D and JavaScript for these. Here each one is a small
loop that redraws a canvas about 30-60 times a second using .after().

  - FlowerBloom  : the turning flower on the Home screen
  - confetti     : paper pieces that burst out for scores of 80% or more
  - Trophy       : the spinning gold trophy for a perfect 100%
  - BadgeCoin    : achievement coins that flip over when you click them
"""

import math
import random
import tkinter as tk

import theme


def _alive(widget):
    """True while the widget is still on screen (stops loops after leaving a page)."""
    try:
        return bool(widget.winfo_exists())
    except tk.TclError:
        return False


def _mix(hex_a, hex_b, t):
    """Blend two colours. t=0 gives hex_a, t=1 gives hex_b."""
    a = [int(hex_a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(hex_b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


# ---------------------------------------------------------------- flower

class FlowerBloom(tk.Canvas):
    """An elegant animated flower for the Home screen.

    Three rings of petals (gold outside, rose in the middle, lilac inside) turn
    slowly in opposite directions and gently "breathe". A ring of tiny gold dots
    circles around them, and a glowing gold centre shows a "?" for quizzes.
    """

    # (number of petals, length, width, colour, edge colour, turning speed)
    RINGS = [
        (12, 0.92, 0.26, "#3b2a10", "#fbbf24", 0.0030),
        (10, 0.68, 0.30, "#4a1d34", "#f472b6", -0.0045),
        (8, 0.46, 0.32, "#2e1f47", "#c084fc", 0.0060),
    ]

    def __init__(self, parent, size=330):
        super().__init__(parent, width=size, height=size, bg=theme.BG, highlightthickness=0)
        self.size, self.t = size, 0.0
        c, R = size / 2, size / 2 - 12
        # soft halo rings behind the flower (drawn once)
        for k, colour in enumerate(("#16110b", "#1d160e", "#251b10")):
            r = R * (1.0 - k * 0.12)
            self.create_oval(c - r, c - r, c + r, c + r, fill=colour, outline="")
        self.rings = []
        for n, length, width, fill, edge, speed in self.RINGS:
            items = [self.create_polygon(0, 0, 0, 0, fill=fill, outline=edge, width=2, smooth=True)
                     for _ in range(n)]
            self.rings.append((items, length, width, speed))
        self.dots = [self.create_oval(0, 0, 0, 0, fill=theme.GOLD, outline="") for _ in range(24)]
        self.glow = self.create_oval(0, 0, 0, 0, fill="#f59e0b", outline="")
        self.core = self.create_oval(0, 0, 0, 0, fill=theme.GOLD, outline="#fde68a", width=2)
        self.mark = self.create_text(c, c, text="?", fill=theme.BG, font=theme.head_font(26))
        self._step()

    def _step(self):
        if not _alive(self):
            return
        c, R = self.size / 2, self.size / 2 - 12
        breathe = 1 + 0.035 * math.sin(self.t * 1.6)
        for ring_no, (items, length, width, speed) in enumerate(self.rings):
            n = len(items)
            L = R * length * breathe
            W = R * width
            base = self.t * speed * 33 + ring_no * 0.3
            for i, item in enumerate(items):
                a = base + i * math.tau / n
                # a pointed petal: from the centre out to the tip, round in the middle
                shape = [(0, 0), (L * 0.35, -W / 2), (L * 0.75, -W / 2.4), (L, 0), (L * 0.75, W / 2.4), (L * 0.35, W / 2)]
                ca, sa = math.cos(a), math.sin(a)
                self.coords(item, *[v for x, y in shape for v in (c + x * ca - y * sa, c + x * sa + y * ca)])
        # tiny gold dots circling outside the petals, twinkling
        for i, dot in enumerate(self.dots):
            a = -self.t * 0.25 + i * math.tau / len(self.dots)
            r = R * 0.985
            d = 1.6 + 1.4 * (0.5 + 0.5 * math.sin(self.t * 3 + i))
            x, y = c + r * math.cos(a), c + r * math.sin(a)
            self.coords(dot, x - d, y - d, x + d, y + d)
        g = R * 0.2 * (1 + 0.08 * math.sin(self.t * 2.2))
        self.coords(self.glow, c - g * 1.25, c - g * 1.25, c + g * 1.25, c + g * 1.25)
        self.coords(self.core, c - g, c - g, c + g, c + g)
        self.t += 0.033
        self.after(33, self._step)


# ---------------------------------------------------------------- confetti

def confetti(canvas, seconds=3.0):
    """Burst of paper pieces on any canvas (used on the Results banner)."""
    w = canvas.winfo_width() or int(canvas.cget("width"))
    h = canvas.winfo_height() or int(canvas.cget("height"))
    colours = ["#fbbf24", "#22d3ee", "#ffffff", "#4169e1", "#f59e0b"]
    pieces = [{
        "x": w / 2, "y": h / 3,
        "vx": (random.random() - 0.5) * 16, "vy": random.random() * -12 - 4,
        "size": random.random() * 8 + 5, "spin": random.random() * math.pi,
        "colour": random.choice(colours),
    } for _ in range(140)]
    frames = int(seconds * 30)

    def draw(frame=0):
        if not _alive(canvas):
            return
        canvas.delete("confetti")
        if frame >= frames:
            return
        for p in pieces:
            p["vy"] += 0.35          # gravity pulls pieces down
            p["vx"] *= 0.99          # air slows them a little
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["spin"] += 0.15
            c, s, half = math.cos(p["spin"]), math.sin(p["spin"]), p["size"] / 2
            corners = [(-half, -half / 2), (half, -half / 2), (half, half / 2), (-half, half / 2)]
            xy = [v for dx, dy in corners for v in (p["x"] + dx * c - dy * s, p["y"] + dx * s + dy * c)]
            canvas.create_polygon(xy, fill=p["colour"], outline="", tags="confetti")
        canvas.after(33, draw, frame + 1)

    draw()


# ---------------------------------------------------------------- trophy

class Trophy(tk.Canvas):
    """A gold trophy that spins around (width shrinks and grows like it is turning)."""

    def __init__(self, parent, size=170, bg=theme.CARD):
        super().__init__(parent, width=size, height=size, bg=bg, highlightthickness=0)
        self.size, self.turn = size, 0.0
        self._step()

    def _step(self):
        if not _alive(self):
            return
        self.delete("all")
        k = self.size / 140                       # the drawing is designed for 140px
        squash = abs(math.cos(self.turn)) * 0.85 + 0.15
        shine = _mix(theme.GOLD_DARK, "#fde68a", abs(math.cos(self.turn)))
        cx = self.size / 2

        def x(v):  # squash around the middle line so it looks like it is turning
            return cx + (v - 70) * k * squash

        def y(v):
            return 8 * k + v * k

        cup = [(30, 10), (110, 10), (108, 40), (98, 60), (84, 74), (70, 78), (56, 74), (42, 60), (32, 40)]
        self.create_polygon([v for px, py in cup for v in (x(px), y(py))], fill=shine, outline=theme.GOLD_DARK, width=2, smooth=True)
        self.create_arc(x(10), y(16), x(40), y(50), start=90, extent=180, style="arc", outline=shine, width=int(5 * k))
        self.create_arc(x(100), y(16), x(130), y(50), start=-90, extent=180, style="arc", outline=shine, width=int(5 * k))
        self.create_rectangle(x(64), y(76), x(76), y(100), fill=shine, outline="")
        self.create_polygon(x(50), y(100), x(90), y(100), x(86), y(110), x(54), y(110), fill=shine, outline="")
        self.create_rectangle(x(38), y(110), x(102), y(124), fill=theme.GOLD_DARK, outline="")
        if math.cos(self.turn) > 0:
            self.create_text(cx, y(38), text="★", fill=theme.BG, font=theme.font(int(22 * k * squash) or 1, "bold"))
        self.turn += 0.06
        self.after(33, self._step)


# ---------------------------------------------------------------- badge coins

class BadgeCoin(tk.Canvas):
    """One achievement badge. Click it to flip it over and read how to earn it.

    fresh=True means it was just unlocked: it spins a few times and says "New!".
    """

    def __init__(self, parent, badge, unlocked, fresh=False, size=150, bg=theme.BG):
        super().__init__(parent, width=size, height=size + 6, bg=bg, highlightthickness=0, cursor="hand2")
        self.badge, self.unlocked, self.fresh, self.size = badge, unlocked, fresh, size
        self.back = False      # False = front (medal), True = back (description)
        self.squash = 1.0
        self._draw()
        self.bind("<Button-1>", lambda e: self.flip())
        if fresh:
            self.after(400, self.flip, 4)   # spin 4 half-turns, ending on the front

    def _draw(self):
        self.delete("all")
        s, c = self.size, self.size / 2
        r = s / 2 - 6
        rx = max(r * self.squash, 1)
        if self.unlocked:
            fill, edge, ink = ("#3b2a10" if not self.back else "#2a1f0e"), theme.GOLD, theme.GOLD
        else:
            fill, edge, ink = "#1a1612", "#4a4036", theme.MUTED
        if self.fresh:
            self.create_oval(c - rx - 4, c - r - 4, c + rx + 4, c + r + 4, outline=theme.CYAN, width=2)
        self.create_oval(c - rx, c - r, c + rx, c + r, fill=fill, outline=edge, width=3)
        if self.squash < 0.35:
            return  # too thin to show text mid-flip
        b = self.badge
        wrap = int(s * 0.7)
        if not self.back:
            self.create_text(c, c - 28, text=b["icon"],
                             fill=ink, font=theme.head_font(18))
            self.create_text(c, c + 6, text=b["name"], fill=theme.WHITE if self.unlocked else theme.MUTED,
                             font=theme.font(10, "bold"), width=wrap, justify="center")
            status = "New!" if self.fresh else ("Unlocked" if self.unlocked else "Locked")
            self.create_text(c, c + 32, text=status, fill=theme.CYAN if self.fresh else ink, font=theme.font(9, "bold"))
        else:
            self.create_text(c, c - 26, text=b["name"], fill=ink, font=theme.font(10, "bold"), width=wrap, justify="center")
            self.create_text(c, c + 10, text=b["desc"], fill=theme.TEXT_SOFT, font=theme.font(9), width=wrap, justify="center")

    def flip(self, half_turns=1):
        """Shrink to a thin line, swap sides, grow back. Repeats for spins."""
        steps = 8

        def shrink(i=0):
            if not _alive(self):
                return
            self.squash = 1 - (i + 1) / steps
            self._draw()
            if i + 1 < steps:
                self.after(16, shrink, i + 1)
            else:
                self.back = not self.back
                grow()

        def grow(i=0):
            if not _alive(self):
                return
            self.squash = (i + 1) / steps
            self._draw()
            if i + 1 < steps:
                self.after(16, grow, i + 1)
            elif half_turns > 1:
                self.flip(half_turns - 1)

        shrink()
