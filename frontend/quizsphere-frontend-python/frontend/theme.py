"""
QuizSphere look and feel (does the job of css/site.css on the website).

Colours, fonts and small reusable widgets: buttons, cards, text styles,
text boxes and a scrollable page.
"""

import sys
import tkinter as tk
import tkinter.font as tkfont

# 1. Colours (same as the website's CSS variables)
BG = "#0b0907"          # page background (very dark brown)
DEEP = "#060504"        # the space around the page, where the 3D shapes float
PANEL_EDGE = "#2a2119"  # thin border around the page column
BG_2 = "#1c140d"        # navbar / footer
CARD = "#1d1712"        # "glass" card
CARD_HOVER = "#2a211a"
BORDER = "#3a3029"
INPUT = "#14100c"
GOLD = "#fbbf24"
GOLD_DARK = "#b45309"
CYAN = "#22d3ee"
WHITE = "#ffffff"
TEXT_SOFT = "#c7d2fe"
MUTED = "#a8a29e"
SUCCESS = "#34d399"
DANGER = "#f87171"

# Each subject has its own colour (like the website's 3D background themes)
TOPIC_COLORS = {"math": "#fbbf24", "gk": "#34d399", "web": "#22d3ee", "mix": "#93b4ff"}

# 2. Fonts: pick the first family installed on this computer
FAMILY = "Helvetica"
HEAD_FAMILY = "Helvetica"


def init_fonts(root):
    global FAMILY, HEAD_FAMILY
    installed = set(tkfont.families(root))
    for name in ("Segoe UI", "SF Pro Text", "Helvetica Neue", "DejaVu Sans", "Arial", "Helvetica"):
        if name in installed:
            FAMILY = name
            break
    for name in ("Segoe UI Black", "Segoe UI Semibold", "Arial Black", FAMILY):
        if name in installed:
            HEAD_FAMILY = name
            break


def font(size=11, weight="normal"):
    return (FAMILY, size, weight)


def head_font(size=24):
    return (HEAD_FAMILY, size, "bold")


# 3. Small text helpers ------------------------------------------------------

def heading(parent, text, size=26, bg=BG, fg=WHITE, **kw):
    return tk.Label(parent, text=text, font=head_font(size), bg=bg, fg=fg, anchor="w", justify="left", **kw)


def eyebrow(parent, text, bg=BG, fg=GOLD):
    """Small gold UPPERCASE label above a heading."""
    return tk.Label(parent, text=text.upper(), font=font(9, "bold"), bg=bg, fg=fg, anchor="w")


def text(parent, value, size=11, bg=BG, fg=TEXT_SOFT, wrap=0, weight="normal", **kw):
    return tk.Label(parent, text=value, font=font(size, weight), bg=bg, fg=fg, anchor="w",
                    justify="left", wraplength=wrap, **kw)


def pill(parent, value, bg=BG, color=CYAN):
    """Rounded-looking tag, like the website's .badge."""
    return tk.Label(parent, text=" " + value + " ", font=font(9, "bold"), bg=bg, fg=color,
                    highlightthickness=1, highlightbackground=color, padx=6, pady=1)


def card(parent, bg=CARD, padx=20, pady=18, **kw):
    """A dark rounded-feel panel, like the website's "glass" cards."""
    return tk.Frame(parent, bg=bg, highlightthickness=1, highlightbackground=BORDER,
                    padx=padx, pady=pady, **kw)


# 4. Buttons -------------------------------------------------------------------

class Button(tk.Label):
    """A flat button that looks the same on Windows, Mac and Linux.

    kind = "primary" (gold), "ghost" (dark outline), "danger" (red) or "link" (text only).
    """

    STYLES = {
        "primary": {"bg": GOLD, "fg": BG, "hover": "#fcd34d", "border": GOLD_DARK},
        "ghost": {"bg": CARD, "fg": WHITE, "hover": CARD_HOVER, "border": BORDER},
        "danger": {"bg": "#7f1d1d", "fg": WHITE, "hover": "#991b1b", "border": DANGER},
        "link": {"bg": None, "fg": CYAN, "hover": None, "border": None},
        "nav": {"bg": BG_2, "fg": TEXT_SOFT, "hover": "#2a2016", "border": BG_2},
        "nav-active": {"bg": "#2a2016", "fg": GOLD, "hover": "#2a2016", "border": "#2a2016"},
    }

    def __init__(self, parent, label, command=None, kind="primary", size=11, padx=18, pady=9, **kw):
        style = self.STYLES[kind]
        parent_bg = parent.cget("bg")
        self._bg = style["bg"] or parent_bg
        self._hover = style["hover"] or parent_bg
        self._fg = style["fg"]
        self._command = command
        self._enabled = True
        weight = "bold" if kind in ("primary", "nav-active") else "normal"
        if kind == "link":
            weight = "underline"
        super().__init__(parent, text=label, font=font(size, weight), bg=self._bg, fg=self._fg,
                         padx=padx, pady=pady, cursor="hand2",
                         highlightthickness=0 if kind == "link" else 1,
                         highlightbackground=style["border"] or parent_bg, **kw)
        self.bind("<Enter>", lambda e: self._enabled and self.config(bg=self._hover))
        self.bind("<Leave>", lambda e: self.config(bg=self._bg))
        self.bind("<Button-1>", self._click)

    def _click(self, _event=None):
        if self._enabled and self._command:
            self._command()

    def set_enabled(self, enabled):
        self._enabled = enabled
        self.config(fg=self._fg if enabled else MUTED, cursor="hand2" if enabled else "arrow")

    def set_colors(self, bg, fg, border=None):
        self._bg = self._hover = bg
        self._fg = fg
        self.config(bg=bg, fg=fg)
        if border:
            self.config(highlightbackground=border)


# 5. Text boxes ------------------------------------------------------------------

def entry(parent, show=None, width=40, placeholder=""):
    box = tk.Entry(parent, font=font(12), bg=INPUT, fg=WHITE, insertbackground=WHITE,
                   relief="flat", highlightthickness=1, highlightbackground=BORDER,
                   highlightcolor=GOLD, width=width, show=show or "")
    if placeholder:
        add_placeholder(box, placeholder, show)
    return box


def add_placeholder(box, hint, show=None):
    """Grey hint text inside an empty text box (like HTML's placeholder)."""
    def put_hint(_e=None):
        if not box.get():
            box.config(fg=MUTED, show="")
            box.insert(0, hint)
            box._showing_hint = True

    def clear_hint(_e=None):
        if getattr(box, "_showing_hint", False):
            box.delete(0, "end")
            box.config(fg=WHITE, show=show or "")
            box._showing_hint = False

    box.bind("<FocusIn>", clear_hint, add="+")
    box.bind("<FocusOut>", put_hint, add="+")
    put_hint()


def value_of(box):
    """Read a text box, ignoring the grey placeholder hint."""
    return "" if getattr(box, "_showing_hint", False) else box.get()


def set_value(box, new_text):
    if getattr(box, "_showing_hint", False):
        box.delete(0, "end")
        box._showing_hint = False
    box.config(fg=WHITE, show=getattr(box, "_real_show", box.cget("show")))
    box.delete(0, "end")
    box.insert(0, new_text)


def field(parent, label, bg=CARD, **entry_kw):
    """A label with a text box under it. Returns the text box."""
    tk.Label(parent, text=label, font=font(10, "bold"), bg=bg, fg=WHITE, anchor="w").pack(fill="x", pady=(12, 4))
    box = entry(parent, **entry_kw)
    box._real_show = entry_kw.get("show") or ""
    box.pack(fill="x", ipady=7)
    return box


def message(parent, bg=CARD):
    """A red (error) or green (success) message line. Empty until .show() is called."""
    lbl = tk.Label(parent, text="", font=font(10, "bold"), bg=bg, fg=DANGER, anchor="w",
                   justify="left", wraplength=420)
    lbl.show = lambda msg, ok=False: lbl.config(text=msg, fg=SUCCESS if ok else DANGER)
    lbl.hide = lambda: lbl.config(text="")
    return lbl


# 6. Scrollable page -----------------------------------------------------------

class ScrollPage(tk.Frame):
    """A page that scrolls with the mouse wheel. Put widgets inside `.body`."""

    def __init__(self, parent, max_width=1000):
        super().__init__(parent, bg=BG)
        self.canvas = tk.Canvas(self, bg=DEEP, highlightthickness=0, bd=0)
        bar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # The page column: a panel with a thin border, the shapes drift behind it
        self.body = tk.Frame(self.canvas, bg=BG, highlightthickness=1, highlightbackground=PANEL_EDGE,
                             padx=24)
        self._window = self.canvas.create_window(0, 0, window=self.body, anchor="n")
        self.max_width = max_width

        self.body.bind("<Configure>", lambda e: self._set_scroll_area())
        self.canvas.bind("<Configure>", self._resize)
        self.bind("<Enter>", lambda e: self._wheel(True))
        self.bind("<Leave>", lambda e: self._wheel(False))

    def _resize(self, event):
        # A "shrink-wrapped" page is only as wide as its content, so the
        # floating background shows on both sides of it
        width = 0 if self.max_width is None else min(event.width - 40, self.max_width)
        self.canvas.itemconfigure(self._window, width=width)
        self.canvas.coords(self._window, event.width / 2, 0)   # keep the page centred
        self._set_scroll_area()

    def _set_scroll_area(self):
        # Scroll area = full window width x page height (starting at the top-left corner)
        self.canvas.configure(scrollregion=(0, 0, self.canvas.winfo_width(), self.body.winfo_reqheight()))

    def _wheel(self, on):
        if on:
            self.bind_all("<MouseWheel>", self._on_wheel)          # Windows and Mac
            self.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-3, "units"))  # Linux
            self.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(3, "units"))
        else:
            self.unbind_all("<MouseWheel>")
            self.unbind_all("<Button-4>")
            self.unbind_all("<Button-5>")

    def _on_wheel(self, event):
        if self.body.winfo_height() <= self.canvas.winfo_height():
            return  # nothing to scroll
        if sys.platform.startswith("win"):
            units = -int(event.delta / 120) * 3   # Windows sends 120 per wheel "click"
        else:
            units = -event.delta                   # Mac sends small numbers
        if units == 0:
            units = -1 if event.delta > 0 else 1
        self.canvas.yview_scroll(units, "units")

    def shrink_wrap(self):
        """Use for small centred forms (login, register, profile)."""
        self.max_width = None
        self.canvas.itemconfigure(self._window, width=0)
        self.body.config(bg=DEEP, highlightthickness=0, padx=0)   # no panel: just the form card

    def destroy(self):
        self._wheel(False)   # stop listening to the mouse wheel when the page closes
        super().destroy()

    def to_top(self):
        self.canvas.yview_moveto(0)


def grid_columns(frame, count):
    for i in range(count):
        frame.grid_columnconfigure(i, weight=1, uniform="col")
