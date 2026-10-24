"""
Flower border around the page (the open space on the left and right).

  - A flower vine runs down each side of the page: a wavy green stem with
    leaves and slowly turning flowers (pink, purple, gold and white).
  - Between the vine and the window edge, single flowers float gently upwards.
    Each one has its own "lane" and the flowers in a lane stay evenly spaced,
    so they never bunch up or overlap. When one floats off the top it comes
    back in at the bottom.

Everything is drawn on the canvas behind the page, 30 times a second.
Items are created once and only moved after that, which keeps it fast.
"""

import math
import random

PETALS = ["#f472b6", "#c084fc", "#fbbf24", "#fda4af", "#f9fafb", "#fb7185"]
CENTRES = ["#fbbf24", "#f59e0b", "#fde68a"]
LEAF = "#2f9e6e"
STEM = "#1f6f4d"
DARK = (6, 5, 4)          # the colour behind everything, for fading

VINE_SPACING = 92         # pixels between flowers on a vine
LANE_WIDTH = 64           # each floating flower lane is this wide
PER_LANE = 3              # floating flowers in each lane (spread evenly top to bottom)


def _fade(hex_colour, strength):
    """Mix a colour with the dark background. strength 1 = full colour, 0 = invisible."""
    rgb = [int(hex_colour[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(d + (c - d) * strength):02x}" for c, d in zip(rgb, DARK))


def _turn(points, cx, cy, angle):
    """Rotate a list of (x, y) points around (cx, cy)."""
    c, s = math.cos(angle), math.sin(angle)
    out = []
    for x, y in points:
        out += [cx + x * c - y * s, cy + x * s + y * c]
    return out


class Border:
    """Flower vines along the page edges + gently floating flowers beside them.

    canvas : the scrolling canvas behind the page
    panel  : a function that returns (left, right) of the page column, in canvas pixels
    """

    def __init__(self, canvas, panel, calm=False):
        self.canvas = canvas
        self.panel = panel
        self.pace = 0.4 if calm else 1.0
        self.t = 0.0
        self.size = (0, 0, 0, 0)
        self.vines = {}
        self.vine_flowers = {"left": [], "right": []}
        self.floaters = []
        canvas.after(80, self._loop)

    # ------------------------------------------------------------ one flower

    def _make_flower(self, colour, size, strength=1.0, leaf=False):
        c = self.canvas
        petals = random.choice((5, 6, 8))
        return {
            "size": size, "petals": petals,
            "turn": random.random() * math.tau,
            "spin": random.uniform(0.004, 0.012) * random.choice((-1, 1)),
            "leaf_side": random.choice((-1, 1)),
            "leaf": c.create_polygon(0, 0, 0, 0, fill=LEAF, outline="", smooth=True, tags="border") if leaf else None,
            "items": [c.create_polygon(0, 0, 0, 0, fill=_fade(colour, 0.85 * strength),
                                       outline=_fade(colour, strength), smooth=True, tags="border")
                      for _ in range(petals)],
            "centre": c.create_oval(0, 0, 0, 0, fill=_fade(random.choice(CENTRES), strength),
                                    outline="", tags="border"),
        }

    def _place_flower(self, fl, x, y, state):
        c = self.canvas
        fl["turn"] += fl["spin"] * self.pace
        r = fl["size"] * (1 + 0.06 * math.sin(self.t * 2 + y / 30))   # gentle "breathing"
        if fl["leaf"]:
            side = fl["leaf_side"]
            leaf = [(p[0] * side, p[1]) for p in [(0, -4), (9, -7), (16, 0), (9, 5), (0, 3)]]
            c.coords(fl["leaf"], *_turn(leaf, x + side * 4, y + 18, 0.5 * side))
            c.itemconfigure(fl["leaf"], state=state)
        petal = [(0, 0), (r * 0.35, -r * 0.35), (r, -r * 0.3), (r * 1.25, 0), (r, r * 0.3), (r * 0.35, r * 0.35)]
        for i, item in enumerate(fl["items"]):
            c.coords(item, *_turn(petal, x, y, fl["turn"] + i * math.tau / fl["petals"]))
            c.itemconfigure(item, state=state)
        cr = r * 0.38
        c.coords(fl["centre"], x - cr, y - cr, x + cr, y + cr)
        c.itemconfigure(fl["centre"], state=state)

    # ------------------------------------------------------------ building

    def _build(self, w, h, left, right):
        """Make all the items. Runs again when the window or page width changes."""
        self.canvas.delete("border")
        self.size = (w, h, left, right)

        # vines: a stem with a flower every VINE_SPACING pixels
        for n, side in enumerate(("left", "right")):
            self.vines[side] = self.canvas.create_line(0, 0, 0, 0, fill=STEM, width=2, smooth=True, tags="border")
            self.vine_flowers[side] = []
            for i in range(int(h // VINE_SPACING) + 2):
                fl = self._make_flower(PETALS[(i + n * 3) % len(PETALS)], random.uniform(9, 14), leaf=True)
                fl["y"] = i * VINE_SPACING + 40
                self.vine_flowers[side].append(fl)

        # floating flowers: lanes across each gutter, flowers in a lane evenly spaced
        self.floaters = []
        gutters = {"left": (0, left - 44), "right": (right + 44, w)}   # keep clear of the vines
        for side, (g0, g1) in gutters.items():
            lanes = int((g1 - g0) // LANE_WIDTH)
            for lane in range(lanes):
                x = g0 + LANE_WIDTH * (lane + 0.5) + ((g1 - g0) - lanes * LANE_WIDTH) / 2
                speed = random.uniform(0.25, 0.45)
                offset = random.random() * h
                for k in range(PER_LANE):
                    fl = self._make_flower(random.choice(PETALS), random.uniform(10, 16),
                                           strength=random.uniform(0.55, 0.85))
                    fl.update({"x": x, "y": (offset + k * (h + 80) / PER_LANE) % (h + 80) - 40,
                               "vy": speed, "sway": random.random() * math.tau})
                    self.floaters.append(fl)

    # ------------------------------------------------------------ every frame

    def _loop(self):
        c = self.canvas
        try:
            if not c.winfo_exists():
                return
        except Exception:
            return
        w, h = max(c.winfo_width(), 200), max(c.winfo_height(), 200)
        left, right = self.panel()
        if right <= left:                     # page not laid out yet
            c.after(100, self._loop)
            return
        if (w, h, left, right) != self.size:
            self._build(w, h, left, right)
        top = c.canvasy(0)                    # stay fixed while the page scrolls
        self.t += 0.03 * self.pace

        for side, edge, room in (("left", left - 18, left), ("right", right + 18, w - right)):
            state = "normal" if room > 34 else "hidden"
            pts = []
            for y in range(-20, int(h) + 40, 24):
                pts += [edge + math.sin(y / 46 + self.t) * 5, y + top]
            c.coords(self.vines[side], *pts)
            c.itemconfigure(self.vines[side], state=state)
            for fl in self.vine_flowers[side]:
                x = edge + math.sin(fl["y"] / 46 + self.t) * 5
                self._place_flower(fl, x, fl["y"] + top, state)

        for fl in self.floaters:
            fl["y"] -= fl["vy"] * self.pace
            if fl["y"] < -40:                 # off the top: back in at the bottom, same spacing
                fl["y"] += h + 80
            fl["sway"] += 0.02 * self.pace
            self._place_flower(fl, fl["x"] + math.sin(fl["sway"]) * 6, fl["y"] + top, "normal")
        c.after(33, self._loop)
