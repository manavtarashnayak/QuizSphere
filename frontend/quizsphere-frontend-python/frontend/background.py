"""
Floating 3D background (does the job of js/background.js on the website).

Slowly turning wireframe shapes (cube, globe, planet, ring, layers ...) and a
web of small dots, drawn on the canvas behind every page.
  - Each subject has its own colour and shapes: Maths = gold, General
    Knowledge = green, Web & Code = cyan, Mixed = blue.
  - Shapes lean towards the mouse, dots move away from it.
  - Click near a shape and it spins and bounces.
  - On the quiz screen everything moves more slowly so you can focus.

How it is drawn: every shape is a list of 3D points and the lines between
them. 30 times a second each point is turned a little, then flattened to 2D
(far points are pulled closer to the middle, which is what makes it look 3D).
"""

import math
import random

THEMES = {
    "mix": {"colour": (125, 170, 255), "shapes": ["icosa", "globe", "layers", "torus", "cube", "octa", "planet"]},
    "math": {"colour": (251, 191, 36), "shapes": ["icosa", "cube", "torus", "octa", "tetra", "icosa", "cube"]},
    "gk": {"colour": (52, 211, 153), "shapes": ["globe", "planet", "octa", "globe", "tetra", "planet", "icosa"]},
    "web": {"colour": (34, 211, 238), "shapes": ["layers", "cube", "octa", "layers", "icosa", "cube", "layers"]},
}
BG_RGB = (6, 5, 4)    # colour around the page, used to fade shapes in and out


def _hex(rgb, alpha):
    """Colour `rgb` at strength `alpha` (0..1) on top of the dark background."""
    return "#" + "".join(f"{round(b + (c - b) * alpha):02x}" for c, b in zip(rgb, BG_RGB))


# ---------------------------------------------------------------- building shapes

def _connect_by_length(points, length):
    edges = []
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            if abs(math.dist(points[i], points[j]) - length) < 0.01:
                edges.append((i, j))
    return edges


def _box(pts, edges, cx, cy, cz, sx, sy, sz):
    start = len(pts)
    for i in range(8):
        pts.append((cx + (sx if i & 1 else -sx), cy + (sy if i & 2 else -sy), cz + (sz if i & 4 else -sz)))
    for i in range(8):
        for j in range(i + 1, 8):
            if (i ^ j) in (1, 2, 4):
                edges.append((start + i, start + j))


def _ring(pts, edges, n, point_at):
    start = len(pts)
    for i in range(n):
        pts.append(point_at(i / n * math.tau))
    for i in range(n):
        edges.append((start + i, start + (i + 1) % n))


def _globe(pts, edges, r, n=16):
    for deg in (-60, -30, 0, 30, 60):
        la = math.radians(deg)
        _ring(pts, edges, n, lambda t: (math.cos(t) * r * math.cos(la), r * math.sin(la), math.sin(t) * r * math.cos(la)))
    for k in range(6):
        lon = k / 6 * math.pi
        _ring(pts, edges, n, lambda t: (r * math.cos(t) * math.cos(lon), r * math.sin(t), r * math.cos(t) * math.sin(lon)))


def build(kind):
    """Return (points, edges) for one shape."""
    pts, edges = [], []
    if kind == "cube":
        _box(pts, edges, 0, 0, 0, 0.8, 0.8, 0.8)
    elif kind == "octa":
        pts = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
        edges = _connect_by_length(pts, math.sqrt(2))
    elif kind == "tetra":
        raw = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]
        edges = _connect_by_length(raw, math.sqrt(8))
        pts = [tuple(v * 0.75 for v in p) for p in raw]
    elif kind == "icosa":
        p = (1 + math.sqrt(5)) / 2
        raw = []
        for a in (-1, 1):
            for b in (-1, 1):
                raw += [(0, a, b * p), (a, b * p, 0), (b * p, 0, a)]
        edges = _connect_by_length(raw, 2)
        pts = [tuple(v / p for v in q) for q in raw]
    elif kind == "torus":
        U, V, R, r = 16, 8, 0.8, 0.32
        for u in range(U):
            for w in range(V):
                a, b = u / U * math.tau, w / V * math.tau
                pts.append(((R + r * math.cos(b)) * math.cos(a), r * math.sin(b), (R + r * math.cos(b)) * math.sin(a)))
                edges += [(u * V + w, ((u + 1) % U) * V + w), (u * V + w, u * V + (w + 1) % V)]
    elif kind == "globe":
        _globe(pts, edges, 1)
    elif kind == "planet":
        _globe(pts, edges, 0.6, n=12)
        tilt = 0.45
        for rad in (1.15, 1.4):
            _ring(pts, edges, 32, lambda t: (math.cos(t) * rad, math.sin(t) * rad * math.sin(tilt), math.sin(t) * rad * math.cos(tilt)))
    elif kind == "layers":
        for y in (-0.55, 0, 0.55):
            _box(pts, edges, 0, y, 0, 0.9, 0.12, 0.9)
    return pts, edges


# ---------------------------------------------------------------- the animation

class Background:
    """Draws the floating shapes on `canvas` (the scrolling canvas behind a page).
    Page widgets sit on top of the canvas, so the shapes show in the open space around them."""

    def __init__(self, canvas, theme="mix", calm=False, shapes=True):
        self.canvas = canvas
        self.pace = 0.35 if calm else 1.0     # slower on the quiz screen
        self.count = (3 if calm else 4) if shapes else 0   # shapes=False: no 3D shapes or dots
        self.enabled = shapes
        self.theme = None
        self.shapes = []
        self.dots = []
        self.links = []                        # reusable line items joining nearby dots
        self.colour = list(THEMES["mix"]["colour"])
        self.mouse = (-9999, -9999, 0.0, 0.0)  # x, y, and -1..1 position across the window
        self.size = (0, 0)
        self.set_theme(theme)
        if shapes:
            canvas.after(60, self._loop)

    # ---- size of the visible area
    def _area(self):
        return max(self.canvas.winfo_width(), 300), max(self.canvas.winfo_height(), 300)

    # ---- one shape
    def _make_shape(self, kind, i, total, rgb):
        w, h = self._area()
        depth = 0.35 + random.random() * 0.65          # 1 = close to you, 0.35 = far away
        pts, edges = build(kind)
        shape = {
            "pts": pts, "edges": edges, "depth": depth, "rgb": rgb,
            "x": ((i + 0.5) / total + (random.random() - 0.5) * 0.12) * w,
            "y": (0.12 + random.random() * 0.76) * h,
            "size": 85 * depth + random.random() * 25,
            "rx": random.random() * 6, "ry": random.random() * 6,
            "rsx": (random.random() - 0.5) * 0.006, "rsy": 0.003 + random.random() * 0.006,
            "dx": (random.random() - 0.5) * 0.5, "dy": (random.random() - 0.5) * 0.4,
            "alpha": 0.0, "target": 1.0, "spin": 0.0, "pulse": 0.3, "shown": -1,
        }
        width = 0.8 + depth * 1.2
        shape["lines"] = [self.canvas.create_line(0, 0, 0, 0, width=width, fill=_hex(rgb, 0), tags="bg")
                          for _ in edges]
        return shape

    def _make_dots(self):
        self.canvas.delete("bgdot")
        w, h = self._area()
        self.dots = []
        for _ in range(30 if self.pace < 1 else 55):
            r = random.random() * 1.8 + 0.6
            self.dots.append({"x": random.random() * w, "y": random.random() * h, "r": r,
                              "dx": (random.random() - 0.5) * 0.6, "dy": (random.random() - 0.5) * 0.6,
                              "item": self.canvas.create_oval(0, 0, 0, 0, outline="", tags=("bg", "bgdot"))})
        self.size = (w, h)

    def set_theme(self, name):
        """Change subject: old shapes fade out, new ones fade in."""
        if name not in THEMES:
            name = "mix"
        if name == self.theme:
            return
        self.theme = name
        t = THEMES[name]
        for s in self.shapes:
            s["target"] = 0.0
        for i in range(self.count):
            self.shapes.append(self._make_shape(t["shapes"][i % len(t["shapes"])], i, self.count, t["colour"]))

    # ---- clicking near a shape makes it spin and bounce (main.py calls this)
    def poke(self, event):
        try:
            x = event.x_root - self.canvas.winfo_rootx()
            y = event.y_root - self.canvas.winfo_rooty()
        except Exception:
            return
        for s in self.shapes:
            if math.hypot(s["x"] - x, s["y"] - y) < s["size"] * 3:
                s["spin"], s["pulse"] = 0.15, 0.25
            else:
                s["spin"] += 0.02

    # ---- every frame
    def _loop(self):
        c = self.canvas
        try:
            if not c.winfo_exists():
                return
        except Exception:
            return
        w, h = self._area()
        if (w, h) != self.size:
            self._make_dots()
        px, py = c.winfo_pointerxy()
        mx, my = px - c.winfo_rootx(), py - c.winfo_rooty()
        self.mouse = (mx, my, (mx / w - 0.5) * 2, (my / h - 0.5) * 2) if 0 <= mx <= w and 0 <= my <= h else (-9999, -9999, 0, 0)
        top = c.canvasy(0)    # the page may be scrolled: draw relative to what you can see
        self._update(w, h)
        self._draw_dots(w, h, top)
        for s in sorted(self.shapes, key=lambda s: s["depth"]):   # far ones first
            self._draw_shape(s, top)
        c.tag_lower("bg")      # always behind everything else
        c.tag_lower("bglink")
        c.after(33, self._loop)

    def _update(self, w, h):
        for s in self.shapes:
            s["alpha"] += (s["target"] - s["alpha"]) * 0.04
            s["rx"] += s["rsx"] * self.pace + s["spin"] * 0.3
            s["ry"] += s["rsy"] * self.pace + s["spin"]
            s["spin"] *= 0.96
            s["pulse"] *= 0.93
            s["x"] += s["dx"] * self.pace
            s["y"] += s["dy"] * self.pace
            m = s["size"] * 2
            if s["x"] < -m:
                s["x"] = w + m
            if s["x"] > w + m:
                s["x"] = -m
            if s["y"] < -m:
                s["y"] = h + m
            if s["y"] > h + m:
                s["y"] = -m
        for s in [s for s in self.shapes if s["target"] == 0 and s["alpha"] < 0.01]:
            for item in s["lines"]:
                self.canvas.delete(item)
            self.shapes.remove(s)
        goal = THEMES[self.theme]["colour"]
        self.colour = [a + (b - a) * 0.04 for a, b in zip(self.colour, goal)]

    def _draw_shape(self, s, top):
        _, _, nx, ny = self.mouse
        ax, ay = s["rx"] + ny * 0.4, s["ry"] + nx * 0.4          # lean towards the mouse
        cx, sx, cy, sy = math.cos(ax), math.sin(ax), math.cos(ay), math.sin(ay)
        scale = s["size"] * (1 + s["pulse"])
        ox = s["x"] + nx * 30 * s["depth"]
        oy = s["y"] + ny * 20 * s["depth"] + top
        flat = []
        for x, y, z in s["pts"]:
            y1, z1 = y * cx - z * sx, y * sx + z * cx
            x2, z2 = x * cy + z1 * sy, -x * sy + z1 * cy
            persp = 500 / (500 + z2 * scale)                      # far points shrink
            flat.append((ox + x2 * scale * persp, oy + y1 * scale * persp))
        coords = self.canvas.coords
        for item, (a, b) in zip(s["lines"], s["edges"]):
            coords(item, flat[a][0], flat[a][1], flat[b][0], flat[b][1])
        strength = round(s["alpha"] * (0.45 + 0.55 * s["depth"]) * 20)   # only recolour when it changes
        if strength != s["shown"]:
            s["shown"] = strength
            colour = _hex(s["rgb"], strength / 20)
            for item in s["lines"]:
                self.canvas.itemconfigure(item, fill=colour)

    def _draw_dots(self, w, h, top):
        c = self.canvas
        mx, my, _, _ = self.mouse
        dot_colour = _hex([round(v) for v in self.colour], 0.7)
        for d in self.dots:
            dist = math.hypot(d["x"] - mx, d["y"] - my)
            if 0 < dist < 120:                                   # move away from the mouse
                d["x"] += (d["x"] - mx) / dist
                d["y"] += (d["y"] - my) / dist
            d["x"] += d["dx"] * self.pace
            d["y"] += d["dy"] * self.pace
            if d["x"] < 0 or d["x"] > w:
                d["dx"] *= -1
            if d["y"] < 0 or d["y"] > h:
                d["dy"] *= -1
            r = d["r"]
            c.coords(d["item"], d["x"] - r, d["y"] - r + top, d["x"] + r, d["y"] + r + top)
            c.itemconfigure(d["item"], fill=dot_colour)

        # thin lines between dots that are close together
        link_colour = _hex([round(v) for v in self.colour], 0.12)
        used = 0
        for i, a in enumerate(self.dots):
            for b in self.dots[i + 1:]:
                if abs(a["x"] - b["x"]) < 110 and math.hypot(a["x"] - b["x"], a["y"] - b["y"]) < 110:
                    if used == len(self.links):
                        self.links.append(c.create_line(0, 0, 0, 0, tags=("bg", "bglink")))
                    c.coords(self.links[used], a["x"], a["y"] + top, b["x"], b["y"] + top)
                    c.itemconfigure(self.links[used], fill=link_colour, state="normal")
                    used += 1
        for item in self.links[used:]:
            c.itemconfigure(item, state="hidden")
