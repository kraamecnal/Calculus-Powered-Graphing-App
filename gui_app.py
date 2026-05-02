"""
CALC_PIT v2.0 — Calculus Engine
Theme: "Void Cartographer" — deep space blacks + electric cyan/violet accents
"""

import sys
import os

os.environ["QT_API"] = "pyqt6"

import matplotlib
matplotlib.rcParams.update({
    'font.family':       'monospace',
    'axes.facecolor':    '#1a1a2e',
    'figure.facecolor':  '#121212',
    'axes.edgecolor':    '#2a2a4a',
    'axes.labelcolor':   '#8888aa',
    'xtick.color':       '#666688',
    'ytick.color':       '#666688',
    'grid.color':        '#1e1e3a',
    'text.color':        '#e0e0ff',
    'axes.titlecolor':   '#c8c8ff',
    'legend.facecolor':  '#1e1e2e',
    'legend.edgecolor':  '#3a3a5a',
    'lines.antialiased': True,
    'patch.antialiased': True,
})

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QTextEdit, QFrame, QSizePolicy,
    QStackedWidget, QScrollArea, QFileDialog, QGraphicsOpacityEffect,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal
from PyQt6.QtGui import QClipboard


# ══════════════════════════════════════════════════════════════════════════════
# DESIGN TOKENS
# ══════════════════════════════════════════════════════════════════════════════

BG_BASE      = "#0d0d14"
BG_SURFACE   = "#13131f"
BG_ELEVATED  = "#1a1a2e"
BG_SIDEBAR   = "#0f0f1a"

BORDER_SUBTLE = "#1e1e35"
BORDER_NORMAL = "#2a2a45"
BORDER_FOCUS  = "#00d4ff"

ACCENT_CYAN   = "#00d4ff"
ACCENT_VIOLET = "#9b59ff"
ACCENT_GREEN  = "#00ff9d"
ACCENT_AMBER  = "#ffaa00"
ACCENT_RED    = "#ff4d6d"

TEXT_PRIMARY   = "#f0f0ff"
TEXT_SECONDARY = "#9090b8"
TEXT_SUBTLE    = "#50507a"

SIDEBAR_WIDTH = 64

NAV_ITEMS = [
    ("⌂",  "Home",     0),
    ("◈",  "Graph",    3),
    ("f′", "Evaluate", 1),
    ("∫",  "Integral", 2),
    ("Σ",  "Symbolic", 4),
    ("⊢⊣", "Area",    5),
]


# ══════════════════════════════════════════════════════════════════════════════
# STYLESHEET
# ══════════════════════════════════════════════════════════════════════════════

STYLESHEET = f"""
* {{ outline: none; }}

QMainWindow, QWidget {{
    background-color: {BG_BASE};
    color: {TEXT_PRIMARY};
    font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", sans-serif;
    font-size: 13px;
}}

/* ── Sidebar ── */
QWidget#sidebar {{
    background-color: {BG_SIDEBAR};
    border-right: 1px solid {BORDER_SUBTLE};
}}
QPushButton#navBtn {{
    background-color: transparent;
    color: {TEXT_SUBTLE};
    border: none;
    border-radius: 10px;
    padding: 10px 6px;
    font-size: 20px;
    text-align: center;
}}
QPushButton#navBtn:hover {{
    background-color: {BG_ELEVATED};
    color: {TEXT_SECONDARY};
}}
QPushButton#navBtn[active="true"] {{
    background-color: rgba(0, 212, 255, 0.08);
    color: {ACCENT_CYAN};
    border-left: 2px solid {ACCENT_CYAN};
    border-radius: 0px;
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
}}
QLabel#navLabel {{
    color: {TEXT_SUBTLE};
    font-size: 9px;
    letter-spacing: 1px;
    text-align: center;
}}

/* ── Inputs ── */
QLineEdit#funcInput {{
    padding: 14px 20px;
    font-size: 15px;
    font-family: "Consolas", "Cascadia Code", monospace;
    border: 1.5px solid {BORDER_NORMAL};
    border-radius: 12px;
    background-color: {BG_SURFACE};
    color: {ACCENT_CYAN};
    selection-background-color: rgba(0,212,255,0.2);
}}
QLineEdit#funcInput:focus {{
    border: 1.5px solid {ACCENT_CYAN};
    background-color: rgba(0, 212, 255, 0.04);
}}
QLineEdit#boundInput {{
    padding: 10px 14px;
    font-size: 14px;
    font-family: "Consolas", monospace;
    border: 1.5px solid {BORDER_NORMAL};
    border-radius: 10px;
    background-color: {BG_SURFACE};
    color: {ACCENT_AMBER};
}}
QLineEdit#boundInput:focus {{
    border: 1.5px solid {ACCENT_AMBER};
    background-color: rgba(255, 170, 0, 0.04);
}}
QLineEdit#evalInput {{
    padding: 10px 14px;
    font-size: 14px;
    font-family: "Consolas", monospace;
    border: 1.5px solid {BORDER_NORMAL};
    border-radius: 10px;
    background-color: {BG_SURFACE};
    color: {ACCENT_GREEN};
}}
QLineEdit#evalInput:focus {{
    border: 1.5px solid {ACCENT_GREEN};
    background-color: rgba(0, 255, 157, 0.04);
}}

/* ── Buttons ── */
QPushButton#actionCard {{
    background-color: {BG_SURFACE};
    color: {TEXT_PRIMARY};
    padding: 18px 24px;
    font-size: 13px;
    border: 1px solid {BORDER_NORMAL};
    border-radius: 14px;
    text-align: left;
}}
QPushButton#actionCard:hover {{
    background-color: {BG_ELEVATED};
    border-color: {ACCENT_CYAN};
}}
QPushButton#actionCard:pressed {{
    background-color: rgba(0,212,255,0.06);
}}
QPushButton#accentCyan {{
    background-color: {ACCENT_CYAN};
    color: #000000;
    padding: 11px 28px;
    font-size: 12px;
    font-weight: 700;
    border: none;
    border-radius: 10px;
    letter-spacing: 1.5px;
}}
QPushButton#accentCyan:hover  {{ background-color: #33ddff; }}
QPushButton#accentCyan:pressed {{ background-color: #0099cc; }}

QPushButton#accentGreen {{
    background-color: transparent;
    color: {ACCENT_GREEN};
    padding: 11px 28px;
    font-size: 12px;
    font-weight: 700;
    border: 1.5px solid {ACCENT_GREEN};
    border-radius: 10px;
    letter-spacing: 1.5px;
}}
QPushButton#accentGreen:hover {{ background-color: rgba(0, 255, 157, 0.1); }}

QPushButton#accentAmber {{
    background-color: transparent;
    color: {ACCENT_AMBER};
    padding: 11px 28px;
    font-size: 12px;
    font-weight: 700;
    border: 1.5px solid {ACCENT_AMBER};
    border-radius: 10px;
    letter-spacing: 1.5px;
}}
QPushButton#accentAmber:hover {{ background-color: rgba(255, 170, 0, 0.1); }}

QPushButton#accentViolet {{
    background-color: transparent;
    color: {ACCENT_VIOLET};
    padding: 11px 28px;
    font-size: 12px;
    font-weight: 700;
    border: 1.5px solid {ACCENT_VIOLET};
    border-radius: 10px;
    letter-spacing: 1.5px;
}}
QPushButton#accentViolet:hover {{ background-color: rgba(155, 89, 255, 0.1); }}

QPushButton#toolBtn {{
    background-color: {BG_SURFACE};
    color: {TEXT_SECONDARY};
    padding: 7px 14px;
    font-size: 11px;
    font-family: "Consolas", monospace;
    border: 1px solid {BORDER_NORMAL};
    border-radius: 8px;
}}
QPushButton#toolBtn:hover {{
    background-color: {BG_ELEVATED};
    color: {TEXT_PRIMARY};
    border-color: {BORDER_FOCUS};
}}
QPushButton#toggleBtn {{
    background-color: {BG_SURFACE};
    color: {TEXT_SUBTLE};
    padding: 6px 12px;
    font-size: 11px;
    border: 1px solid {BORDER_NORMAL};
    border-radius: 8px;
}}
QPushButton#toggleBtn[active="true"] {{
    background-color: rgba(0, 212, 255, 0.1);
    color: {ACCENT_CYAN};
    border-color: rgba(0, 212, 255, 0.4);
}}
QPushButton#toggleBtn:hover {{
    border-color: {TEXT_SUBTLE};
    color: {TEXT_SECONDARY};
}}

/* ── Output & Labels ── */
QTextEdit#outputDisplay {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_NORMAL};
    border-radius: 12px;
    font-family: "Cascadia Code", "Consolas", monospace;
    font-size: 13px;
    color: {TEXT_PRIMARY};
    padding: 18px;
    selection-background-color: rgba(0,212,255,0.2);
}}
QLabel#pageTitle {{
    color: {TEXT_PRIMARY};
    font-size: 22px;
    font-weight: 700;
    letter-spacing: -0.5px;
}}
QLabel#pageSubtitle {{
    color: {TEXT_SUBTLE};
    font-size: 11px;
    letter-spacing: 3px;
    font-family: "Consolas", monospace;
}}
QLabel#sectionLabel {{
    color: {TEXT_SUBTLE};
    font-size: 10px;
    letter-spacing: 3px;
    font-weight: 600;
}}
QWidget#miniGraphFrame {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_NORMAL};
    border-radius: 12px;
}}

/* ── Scrollbars ── */
QScrollBar:vertical {{
    background: transparent;
    width: 4px;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: {BORDER_NORMAL};
    border-radius: 2px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{ background: {TEXT_SUBTLE}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QScrollBar:horizontal {{ height: 0px; }}

/* ── Misc ── */
QFrame#separator {{
    color: {BORDER_SUBTLE};
    background-color: {BORDER_SUBTLE};
    max-height: 1px;
}}
"""


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def make_separator() -> QFrame:
    sep = QFrame()
    sep.setFrameShape(QFrame.Shape.HLine)
    sep.setObjectName("separator")
    return sep


def make_scroll_page() -> tuple[QVBoxLayout, QWidget]:
    """Returns (inner_layout, outer_widget) for a scrollable page."""
    outer = QWidget()
    outer_lay = QVBoxLayout(outer)
    outer_lay.setContentsMargins(0, 0, 0, 0)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    outer_lay.addWidget(scroll)

    card = QWidget()
    scroll.setWidget(card)

    lay = QVBoxLayout(card)
    lay.setContentsMargins(40, 40, 40, 40)
    lay.setSpacing(0)
    lay.setAlignment(Qt.AlignmentFlag.AlignTop)

    return lay, outer


def make_header(lay: QVBoxLayout, title: str, subtitle: str = ""):
    t = QLabel(title)
    t.setObjectName("pageTitle")
    lay.addWidget(t)
    if subtitle:
        s = QLabel(subtitle)
        s.setObjectName("pageSubtitle")
        lay.addWidget(s)
    lay.addSpacing(8)
    lay.addWidget(make_separator())


def make_section_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("sectionLabel")
    return lbl


def make_func_label(func_str: str) -> str:
    return f"f(x) = {func_str}" if func_str else "No function set — go to Home and enter f(x)"


def style_func_label(lbl: QLabel, has_func: bool):
    if has_func:
        lbl.setStyleSheet(f"color: {ACCENT_CYAN}; font-family: Consolas; font-size: 13px;")
    else:
        lbl.setStyleSheet(f"color: {TEXT_SUBTLE}; font-family: Consolas; font-size: 12px;")


def make_output_display(max_width=520, min_height=160) -> QTextEdit:
    out = QTextEdit()
    out.setObjectName("outputDisplay")
    out.setReadOnly(True)
    out.setMaximumWidth(max_width)
    out.setMinimumHeight(min_height)
    return out


def make_bounds_row(lower: QLineEdit, upper: QLineEdit, btn: QPushButton) -> QHBoxLayout:
    row = QHBoxLayout()
    arrow = QLabel("→")
    arrow.setStyleSheet(f"color: {TEXT_SUBTLE}; font-size: 14px; padding: 0 8px;")
    row.addWidget(lower)
    row.addWidget(arrow)
    row.addWidget(upper)
    row.addSpacing(16)
    row.addWidget(btn)
    row.addStretch()
    return row


def refresh_button_style(btn: QPushButton):
    btn.style().unpolish(btn)
    btn.style().polish(btn)


# ══════════════════════════════════════════════════════════════════════════════
# TOAST NOTIFICATION
# ══════════════════════════════════════════════════════════════════════════════

class Toast(QWidget):
    def __init__(self, parent, message: str, is_error=False):
        super().__init__(parent)
        self.setFixedWidth(360)

        accent = ACCENT_RED    if is_error else ACCENT_GREEN
        bg     = "rgba(255,77,109,0.12)"  if is_error else "rgba(0,255,157,0.1)"
        border = "rgba(255,77,109,0.3)"   if is_error else "rgba(0,255,157,0.3)"

        self.setStyleSheet(f"""
            QWidget {{ background-color: {bg}; border: 1px solid {border}; border-radius: 10px; }}
            QLabel  {{ color: {accent}; font-size: 12px; background: transparent; border: none; }}
        """)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)

        icon = QLabel("⊘" if is_error else "✓")
        icon.setStyleSheet(f"font-size: 14px; color: {accent}; border: none; background: transparent;")
        msg_lbl = QLabel(message)
        msg_lbl.setWordWrap(True)

        lay.addWidget(icon)
        lay.addWidget(msg_lbl, 1)

        self._opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity)
        self._position()
        self.show()
        QTimer.singleShot(2500, self._fade_out)

    def _position(self):
        self.adjustSize()
        pw, ph = self.parent().width(), self.parent().height()
        self.move(pw - self.width() - 20, ph - self.height() - 20)

    def _fade_out(self):
        self._anim = QPropertyAnimation(self._opacity, b"opacity")
        self._anim.setDuration(400)
        self._anim.setStartValue(1.0)
        self._anim.setEndValue(0.0)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.finished.connect(self.deleteLater)
        self._anim.start()


# ══════════════════════════════════════════════════════════════════════════════
# MATPLOTLIB CANVASES
# ══════════════════════════════════════════════════════════════════════════════

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=6, height=5, dpi=110):
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(200)
        self.style_axes()

    def style_axes(self):
        self.ax.set_facecolor('#1a1a2e')
        self.fig.patch.set_facecolor('#121212')
        for spine in self.ax.spines.values():
            spine.set_color('#2a2a4a')
            spine.set_linewidth(0.5)
        self.ax.tick_params(colors='#666688', labelsize=8, length=3)
        self.ax.set_xlabel('x', color='#8888aa', fontsize=9, labelpad=8)
        self.ax.set_ylabel('y', color='#8888aa', fontsize=9, labelpad=8)
        self.ax.grid(True, color='#1e1e3a', linewidth=0.5, alpha=0.8)
        self.ax.axhline(0, color='#333355', linewidth=0.8, zorder=1)
        self.ax.axvline(0, color='#333355', linewidth=0.8, zorder=1)
        self.ax.set_title("awaiting input", color='#50507a',
                          fontsize=9, fontstyle='italic', pad=12, fontfamily='Consolas')


class MiniCanvas(FigureCanvas):
    """Compact live-preview canvas for the homepage."""
    def __init__(self, parent=None):
        self.fig, self.ax = plt.subplots(figsize=(4, 2), dpi=80)
        super().__init__(self.fig)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(120)
        self._style()

    def _style(self):
        self.ax.set_facecolor('#1a1a2e')
        self.fig.patch.set_facecolor('#13131f')
        self.fig.subplots_adjust(left=0.05, right=0.98, top=0.92, bottom=0.12)
        for spine in self.ax.spines.values():
            spine.set_color('#2a2a4a')
            spine.set_linewidth(0.4)
        self.ax.tick_params(colors='#444466', labelsize=7, length=2)
        self.ax.grid(True, color='#1a1a30', linewidth=0.4, alpha=0.7)
        self.ax.axhline(0, color='#2a2a44', linewidth=0.6, zorder=1)
        self.ax.axvline(0, color='#2a2a44', linewidth=0.6, zorder=1)
        self.ax.set_title("live preview", color='#333355', fontsize=8, fontstyle='italic', pad=6)

    def update_preview(self, func_str: str):
        try:
            import numpy as np
            from sympy import sympify, lambdify
            from sympy.abc import x

            f = lambdify(x, sympify(func_str), "numpy")
            x_vals = np.linspace(-8, 8, 400)
            y_vals = np.clip(f(x_vals) * np.ones_like(x_vals), -100, 100)

            self.ax.clear()
            self._style()
            self.ax.plot(x_vals, y_vals, color=ACCENT_CYAN, linewidth=1.5, antialiased=True, zorder=3)
            self.ax.fill_between(x_vals, y_vals, alpha=0.06, color=ACCENT_CYAN)
            self.ax.set_title(f"f(x) = {func_str}", color='#6666aa', fontsize=8, fontstyle='italic', pad=6)
        except Exception:
            self.ax.clear()
            self._style()
        self.draw()


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ══════════════════════════════════════════════════════════════════════════════

class SidebarNav(QWidget):
    page_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(SIDEBAR_WIDTH)
        self._active = 0
        self._btns: list[tuple[QPushButton, QLabel]] = []
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 16, 6, 16)
        lay.setSpacing(4)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        logo = QLabel("◉")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(f"color: {ACCENT_CYAN}; font-size: 22px; padding: 8px 0 16px 0;")
        lay.addWidget(logo)
        lay.addWidget(make_separator())
        lay.addSpacing(8)

        for i, (icon, label, page_idx) in enumerate(NAV_ITEMS):
            cell = QWidget()
            cell_lay = QVBoxLayout(cell)
            cell_lay.setContentsMargins(0, 0, 0, 0)
            cell_lay.setSpacing(2)

            btn = QPushButton(icon)
            btn.setObjectName("navBtn")
            btn.setFixedHeight(44)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setToolTip(label)
            btn.clicked.connect(lambda _, pi=page_idx, ni=i: self._select(ni, pi))

            lbl = QLabel(label.upper())
            lbl.setObjectName("navLabel")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f"color: {TEXT_SUBTLE}; font-size: 8px; letter-spacing: 1px;")

            cell_lay.addWidget(btn)
            cell_lay.addWidget(lbl)
            lay.addWidget(cell)
            self._btns.append((btn, lbl))

        lay.addStretch()

        footer = QLabel("⊙")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(f"color: {TEXT_SUBTLE}; font-size: 16px; padding: 8px;")
        lay.addWidget(footer)

        self._select(0, 0)

    def _select(self, nav_idx: int, page_idx: int):
        if self._active < len(self._btns):
            old_btn, old_lbl = self._btns[self._active]
            old_btn.setProperty("active", False)
            refresh_button_style(old_btn)
            old_lbl.setStyleSheet(f"color: {TEXT_SUBTLE}; font-size: 8px; letter-spacing: 1px;")

        self._active = nav_idx
        btn, lbl = self._btns[nav_idx]
        btn.setProperty("active", True)
        refresh_button_style(btn)
        lbl.setStyleSheet(f"color: {ACCENT_CYAN}; font-size: 8px; letter-spacing: 1px;")

        self.page_changed.emit(page_idx)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ══════════════════════════════════════════════════════════════════════════════

class HomePage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self._preview_timer = QTimer()
        self._preview_timer.setSingleShot(True)
        self._preview_timer.timeout.connect(self._update_preview)
        self._build()

    def _build(self):
        lay, outer = make_scroll_page()
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(outer)

        make_header(lay, "Calculus-Powered", "GRAPHING APP")
        lay.addSpacing(28)

        # Function input
        lay.addWidget(make_section_label("FUNCTION"))
        lay.addSpacing(8)
        self.func_input = QLineEdit()
        self.func_input.setObjectName("funcInput")
        self.func_input.setPlaceholderText("f(x) = ")
        self.func_input.textChanged.connect(lambda: self._preview_timer.start(400))
        self.func_input.returnPressed.connect(self._go_graph)
        lay.addWidget(self.func_input)
        lay.addSpacing(20)

        # Mini preview
        lay.addWidget(make_section_label("LIVE PREVIEW"))
        lay.addSpacing(8)
        preview_frame = QWidget()
        preview_frame.setObjectName("miniGraphFrame")
        preview_frame.setFixedHeight(130)
        pf_lay = QVBoxLayout(preview_frame)
        pf_lay.setContentsMargins(4, 4, 4, 4)
        self.mini_canvas = MiniCanvas(self)
        pf_lay.addWidget(self.mini_canvas)
        lay.addWidget(preview_frame)
        lay.addSpacing(28)

        # Action cards
        lay.addWidget(make_section_label("OPERATIONS"))
        lay.addSpacing(10)

        actions = [
            ("◈  Plot  f(x),  f′(x)  and area",    ACCENT_CYAN,   self._go_graph),
            ("f′  Evaluate and Higher Derivatives", ACCENT_GREEN,  self._go_eval),
            ("∫  Definite Integral",                ACCENT_AMBER,  self._go_integral),
            ("Σ  Symbolic Analysis",                ACCENT_VIOLET, self._go_symbolic),
            ("⊢⊣  Area Between Curves",             ACCENT_VIOLET, self._go_area),
        ]
        for label, color, slot in actions:
            btn = QPushButton(label)
            btn.setObjectName("actionCard")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(56)
            btn.clicked.connect(slot)
            btn.setStyleSheet(btn.styleSheet() + f"QPushButton#actionCard {{ border-left: 3px solid {color}; }}")
            lay.addWidget(btn)
            lay.addSpacing(6)

        lay.addStretch()

    def _update_preview(self):
        text = self.func_input.text().strip()
        if text:
            self.mini_canvas.update_preview(text)
        else:
            self.mini_canvas.ax.clear()
            self.mini_canvas._style()
            self.mini_canvas.draw()

    def _func(self) -> str:
        return self.func_input.text().strip()

    def _navigate(self, page_idx: int, nav_idx: int):
        self.app.stack.setCurrentIndex(page_idx)
        self.app.sidebar._select(nav_idx, page_idx)

    def _go_graph(self):
        f = self._func()
        if f:
            self.app.graph_page.plot(f)
            self._navigate(3, 1)

    def _go_eval(self):
        self.app.eval_page.set_func(self._func())
        self._navigate(1, 2)

    def _go_integral(self):
        self.app.integral_page.set_func(self._func())
        self._navigate(2, 3)

    def _go_area(self):
        self.app.area_page.set_func1(self._func())
        self._navigate(5, 5)

    def _go_symbolic(self):
        f = self._func()
        if f:
            self.app.symbolic_page.show_symbolic(f)
        self._navigate(4, 4)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: EVALUATE AT POINT
# ══════════════════════════════════════════════════════════════════════════════

class EvalPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.func_str = ""
        self._build()

    def _build(self):
        lay, outer = make_scroll_page()
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(outer)

        make_header(lay, "Evaluate", "f(x) AND f′(x) AT A POINT")
        lay.addSpacing(24)

        self.func_label = QLabel(make_func_label(""))
        style_func_label(self.func_label, False)
        lay.addWidget(self.func_label)
        lay.addSpacing(24)

        # Derivative order toggles
        lay.addWidget(make_section_label("DERIVATIVE ORDER"))
        lay.addSpacing(8)
        order_row = QHBoxLayout()
        self.deriv_order = 1
        self._order_buttons: list[tuple[int, QPushButton]] = []
        order_icons = ["1", "′", "″", "‴"]
        for i, icon in enumerate(order_icons, 1):
            btn = QPushButton(icon)
            btn.setObjectName("toggleBtn")
            btn.setProperty("active", i == 1)
            btn.setFixedWidth(50)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, o=i: self._set_order(o))
            order_row.addWidget(btn)
            self._order_buttons.append((i, btn))
        order_row.addStretch()
        lay.addLayout(order_row)
        lay.addSpacing(20)

        # x value input
        lay.addWidget(make_section_label("X VALUE"))
        lay.addSpacing(8)
        input_row = QHBoxLayout()
        self.x_input = QLineEdit()
        self.x_input.setObjectName("evalInput")
        self.x_input.setPlaceholderText("Enter the value of x")
        self.x_input.setFixedWidth(200)
        self.x_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.x_input.returnPressed.connect(self._calc)
        calc_btn = QPushButton("EVALUATE")
        calc_btn.setObjectName("accentGreen")
        calc_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        calc_btn.clicked.connect(self._calc)
        input_row.addWidget(self.x_input)
        input_row.addWidget(calc_btn)
        input_row.addStretch()
        lay.addLayout(input_row)
        lay.addSpacing(24)

        lay.addWidget(make_section_label("RESULT"))
        lay.addSpacing(8)
        self.output = make_output_display(min_height=160)
        lay.addWidget(self.output)
        lay.addStretch()

    def set_func(self, func_str: str):
        self.func_str = func_str or ""
        self.func_label.setText(make_func_label(self.func_str))
        style_func_label(self.func_label, bool(self.func_str))
        self.output.clear()

    def _set_order(self, order: int):
        self.deriv_order = order
        for o, btn in self._order_buttons:
            btn.setProperty("active", o == order)
            refresh_button_style(btn)

    def _deriv_notation(self) -> str:
        return ["f′", "f″", "f‴", f"f^({self.deriv_order})"][min(self.deriv_order - 1, 3)]

    def _calc(self):
        if not self.func_str:
            Toast(self.app.central_widget, "No function set. Return to Home.", is_error=True)
            return
        x_str = self.x_input.text().strip()
        if not x_str:
            Toast(self.app.central_widget, "Please enter an x value.", is_error=True)
            return
        try:
            x_val = float(x_str)
            import core.parser as parser
            import core.differentiator as differentiator

            pretty_f = parser.parse_function(self.func_str)
            f_at_x   = parser.parse_function(self.func_str, x_val, True)
            df_at_x  = differentiator.differentiate(self.func_str, x_val, True, self.deriv_order)
            df_sym   = differentiator.differentiate(self.func_str, order=self.deriv_order)
            dn       = self._deriv_notation()

            self.output.setText(
                f"f(x) = {pretty_f}\n"
                f"{dn}(x) = {df_sym}\n\n"
                f"// EVALUATION  @  x = {x_val}\n\n"
                f"   f({x_val})    =  {f_at_x}\n"
                f"   {dn}({x_val})   =  {df_at_x}"
            )
            Toast(self.app.central_widget, "Evaluated successfully.")
        except Exception as e:
            self.output.setText(f"// [error]  {e}")
            Toast(self.app.central_widget, str(e), is_error=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DEFINITE INTEGRAL
# ══════════════════════════════════════════════════════════════════════════════

class IntegralPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.func_str = ""
        self._build()

    def _build(self):
        lay, outer = make_scroll_page()
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(outer)

        make_header(lay, "Definite Integral", "NUMERICAL INTEGRATION BETWEEN BOUNDS")
        lay.addSpacing(24)

        self.func_label = QLabel(make_func_label(""))
        style_func_label(self.func_label, False)
        lay.addWidget(self.func_label)
        lay.addSpacing(24)

        lay.addWidget(make_section_label("BOUNDS"))
        lay.addSpacing(8)

        self.lower = QLineEdit()
        self.lower.setObjectName("boundInput")
        self.lower.setPlaceholderText("a")
        self.lower.setFixedWidth(90)
        self.lower.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.upper = QLineEdit()
        self.upper.setObjectName("boundInput")
        self.upper.setPlaceholderText("b")
        self.upper.setFixedWidth(90)
        self.upper.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.upper.returnPressed.connect(self._calc)

        calc_btn = QPushButton("∫ COMPUTE")
        calc_btn.setObjectName("accentAmber")
        calc_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        calc_btn.clicked.connect(self._calc)

        lay.addLayout(make_bounds_row(self.lower, self.upper, calc_btn))
        lay.addSpacing(24)

        lay.addWidget(make_section_label("RESULT"))
        lay.addSpacing(8)
        self.output = make_output_display(min_height=160)
        lay.addWidget(self.output)
        lay.addStretch()

    def set_func(self, func_str: str):
        self.func_str = func_str or ""
        self.func_label.setText(make_func_label(self.func_str))
        style_func_label(self.func_label, bool(self.func_str))
        self.output.clear()

    def _calc(self):
        if not self.func_str:
            Toast(self.app.central_widget, "No function set. Return to Home.", is_error=True)
            return
        a_str, b_str = self.lower.text().strip(), self.upper.text().strip()
        if not (a_str and b_str):
            Toast(self.app.central_widget, "Please enter both bounds a and b.", is_error=True)
            return
        try:
            a, b = float(a_str), float(b_str)
            import core.integrator as integrator
            result = integrator.integration(self.func_str, a, b, True)
            self.output.setText(
                f"// DEFINITE INTEGRAL\n\n"
                f"   ∫ f(x) dx   from  {a}  to  {b}\n\n"
                f"   =  {result}"
            )
            Toast(self.app.central_widget, "Integral computed.")
        except Exception as e:
            self.output.setText(f"// [error]  {e}")
            Toast(self.app.central_widget, str(e), is_error=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: GRAPH
# ══════════════════════════════════════════════════════════════════════════════

class GraphPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self._show_grid   = True
        self._show_legend = True
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(0)

        # Top bar
        top = QHBoxLayout()
        top.setSpacing(8)

        title = QLabel("◈ Graph")
        title.setObjectName("pageTitle")
        self.func_lbl = QLabel("")
        self.func_lbl.setStyleSheet(f"color: {ACCENT_CYAN}; font-family: Consolas; font-size: 12px;")

        self.grid_btn = QPushButton("⊞ Grid")
        self.grid_btn.setObjectName("toggleBtn")
        self.grid_btn.setProperty("active", True)
        self.grid_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.grid_btn.clicked.connect(self._toggle_grid)

        self.legend_btn = QPushButton("☰ Legend")
        self.legend_btn.setObjectName("toggleBtn")
        self.legend_btn.setProperty("active", True)
        self.legend_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.legend_btn.clicked.connect(self._toggle_legend)

        export_btn = QPushButton("↓ Export")
        export_btn.setObjectName("toolBtn")
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_btn.clicked.connect(self._export)

        top.addWidget(title)
        top.addSpacing(12)
        top.addWidget(self.func_lbl, 1)
        top.addWidget(self.grid_btn)
        top.addWidget(self.legend_btn)
        top.addSpacing(4)
        top.addWidget(export_btn)

        lay.addLayout(top)
        lay.addSpacing(12)
        lay.addWidget(make_separator())
        lay.addSpacing(8)

        self.canvas = MplCanvas(self, width=8, height=6, dpi=110)
        lay.addWidget(self.canvas, 1)

    # ── Toggles ──────────────────────────────────────────────────────────────

    def _toggle_grid(self):
        self._show_grid = not self._show_grid
        self.grid_btn.setProperty("active", self._show_grid)
        refresh_button_style(self.grid_btn)
        self.canvas.ax.grid(self._show_grid)
        self.canvas.draw()

    def _toggle_legend(self):
        self._show_legend = not self._show_legend
        self.legend_btn.setProperty("active", self._show_legend)
        refresh_button_style(self.legend_btn)
        legend = self.canvas.ax.get_legend()
        if legend:
            legend.set_visible(self._show_legend)
        self.canvas.draw()

    def _export(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Plot", "calc_plot.png",
            "PNG (*.png);;SVG (*.svg);;PDF (*.pdf)"
        )
        if path:
            self.canvas.fig.savefig(path, dpi=300, bbox_inches='tight')
            Toast(self.app.central_widget, f"Saved: {os.path.basename(path)}")

    # ── Plotting ──────────────────────────────────────────────────────────────

    def _legend_kwargs(self) -> dict:
        return dict(framealpha=0.85, fontsize=9, labelcolor=TEXT_PRIMARY,
                    facecolor='#1a1a2e', edgecolor='#2a2a4a')

    def _finalize(self, title_str: str):
        self.canvas.ax.set_title(title_str, color='#8888cc',
                                  fontsize=10, pad=12, fontfamily='Consolas')
        if self._show_legend:
            self.canvas.ax.legend(**self._legend_kwargs())
        self.canvas.ax.grid(self._show_grid)
        self.canvas.draw()

    def plot(self, func_str: str):
        self.func_lbl.setText(f"f(x) = {func_str}")
        try:
            import numpy as np
            from sympy import sympify, lambdify, diff
            from sympy.abc import x

            sym  = sympify(func_str)
            x_v  = np.linspace(-10, 10, 800)
            y_f  = np.clip(lambdify(x, sym, "numpy")(x_v)  * np.ones_like(x_v), -200, 200)
            y_df = np.clip(lambdify(x, diff(sym), "numpy")(x_v) * np.ones_like(x_v), -200, 200)

            self.canvas.ax.clear()
            self.canvas.style_axes()
            self.canvas.ax.plot(x_v, y_f,  label="f(x)",  color=ACCENT_CYAN,   linewidth=2.0, zorder=3)
            self.canvas.ax.plot(x_v, y_df, label="f′(x)", color=ACCENT_VIOLET, linewidth=1.4,
                                linestyle="--", alpha=0.85, zorder=3)
            self.canvas.ax.fill_between(x_v, y_f, alpha=0.06, color=ACCENT_CYAN, zorder=2)
            self._finalize(f"f(x) = {func_str}")
        except Exception as e:
            self._plot_error(e)

    def plot_area(self, func1_str: str, func2_str: str):
        self.func_lbl.setText(f"f(x) = {func1_str},  g(x) = {func2_str}")
        try:
            import numpy as np
            from sympy import sympify, lambdify
            from sympy.abc import x

            x_v  = np.linspace(-10, 10, 800)
            y_f1 = np.clip(lambdify(x, sympify(func1_str), "numpy")(x_v) * np.ones_like(x_v), -200, 200)
            y_f2 = np.clip(lambdify(x, sympify(func2_str), "numpy")(x_v) * np.ones_like(x_v), -200, 200)

            self.canvas.ax.clear()
            self.canvas.style_axes()
            self.canvas.ax.plot(x_v, y_f1, label=f"f(x) = {func1_str}", color=ACCENT_CYAN,  linewidth=2.0, zorder=3)
            self.canvas.ax.plot(x_v, y_f2, label=f"g(x) = {func2_str}", color=ACCENT_GREEN, linewidth=2.0, zorder=3)
            self.canvas.ax.fill_between(x_v, y_f1, y_f2, where=(y_f1 >= y_f2),
                                        alpha=0.25, color=ACCENT_VIOLET, label="Area between", zorder=2)
            self.canvas.ax.fill_between(x_v, y_f1, y_f2, where=(y_f1 < y_f2),
                                        alpha=0.25, color=ACCENT_AMBER, zorder=2)
            self._finalize("Area between curves")
            Toast(self.app.central_widget, "Area visualization loaded.")
        except Exception as e:
            self._plot_error(e)

    def _plot_error(self, e: Exception):
        self.canvas.ax.clear()
        self.canvas.style_axes()
        self.canvas.ax.set_title(f"parse error: {e}", color=ACCENT_RED, fontsize=9)
        self.canvas.draw()
        Toast(self.app.central_widget, str(e), is_error=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SYMBOLIC ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

class SymbolicPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self._build()

    def _build(self):
        lay, outer = make_scroll_page()
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(outer)

        make_header(lay, "Symbolic Analysis", "EXACT DERIVATIVE AND ANTIDERIVATIVE")
        lay.addSpacing(24)

        lay.addWidget(make_section_label("EXPRESSIONS"))
        lay.addSpacing(8)
        self.output = make_output_display(max_width=600, min_height=220)
        lay.addWidget(self.output)
        lay.addSpacing(12)

        copy_btn = QPushButton("⎘ Copy to Clipboard")
        copy_btn.setObjectName("toolBtn")
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.clicked.connect(self._copy)
        row = QHBoxLayout()
        row.addWidget(copy_btn)
        row.addStretch()
        lay.addLayout(row)
        lay.addStretch()

    def show_symbolic(self, func_str: str):
        try:
            import core.parser as parser
            import core.differentiator as differentiator
            import core.integrator as integrator

            pretty_f = parser.parse_function(func_str)
            integ    = integrator.integration(func_str)

            derivs = []
            for n in range(1, 11):
                d = differentiator.differentiate(func_str, order=n)
                if d == '0':
                    break
                derivs.append(d)

            ordinals = ['FIRST', 'SECOND', 'THIRD', 'FOURTH', 'FIFTH',
                        'SIXTH', 'SEVENTH', 'EIGHTH', 'NINTH', 'TENTH']
            lines = [f"// ── FUNCTION ────────────────────────────────\n   f(x)   =  {pretty_f}\n"]
            for i, d in enumerate(derivs, 1):
                ordinal = ordinals[i - 1] if i <= len(ordinals) else f"{i}TH"
                prime   = "'" * i
                lines.append(
                    f"// ── {ordinal} DERIVATIVE  f{prime}(x) ────────────────\n"
                    f"   f{prime}(x)  =  {d}\n"
                )
            lines.append(f"// ── ANTIDERIVATIVE  ∫f(x) dx ────────────────\n   F(x)   =  {integ}  +  C")

            self.output.setText('\n'.join(lines))
            Toast(self.app.central_widget, "Symbolic analysis complete.")
        except Exception as e:
            self.output.setText(f"// [error]  {e}")
            Toast(self.app.central_widget, str(e), is_error=True)

    def _copy(self):
        text = self.output.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            Toast(self.app.central_widget, "Copied to clipboard.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AREA BETWEEN CURVES
# ══════════════════════════════════════════════════════════════════════════════

class AreaPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self._build()

    def _build(self):
        lay, outer = make_scroll_page()
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(outer)

        make_header(lay, "Area Between Curves", "CALCULATE AREA BETWEEN TWO FUNCTIONS")
        lay.addSpacing(24)

        for attr, label, placeholder in [
            ("func1_input", "FIRST FUNCTION",  " "),
            ("func2_input", "SECOND FUNCTION", " "),
        ]:
            lay.addWidget(make_section_label(label))
            lay.addSpacing(8)
            inp = QLineEdit()
            inp.setObjectName("funcInput")
            inp.setPlaceholderText(placeholder)
            setattr(self, attr, inp)
            lay.addWidget(inp)
            lay.addSpacing(16)

        lay.addWidget(make_section_label("BOUNDS"))
        lay.addSpacing(8)

        self.lower = QLineEdit()
        self.lower.setObjectName("boundInput")
        self.lower.setPlaceholderText("a")
        self.lower.setFixedWidth(90)
        self.lower.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.upper = QLineEdit()
        self.upper.setObjectName("boundInput")
        self.upper.setPlaceholderText("b")
        self.upper.setFixedWidth(90)
        self.upper.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.upper.returnPressed.connect(self._calc)

        compute_btn = QPushButton("◆ COMPUTE AREA")
        compute_btn.setObjectName("accentViolet")
        compute_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        compute_btn.clicked.connect(self._calc)
        lay.addLayout(make_bounds_row(self.lower, self.upper, compute_btn))
        lay.addSpacing(24)

        plot_btn = QPushButton("◈ Visualize in Graph")
        plot_btn.setObjectName("accentCyan")
        plot_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        plot_btn.clicked.connect(self._plot)
        row = QHBoxLayout()
        row.addWidget(plot_btn)
        row.addStretch()
        lay.addLayout(row)
        lay.addSpacing(16)

        lay.addWidget(make_section_label("RESULT"))
        lay.addSpacing(8)
        self.output = make_output_display(min_height=160)
        lay.addWidget(self.output)
        lay.addStretch()

    def set_func1(self, func_str: str):
        self.func1_input.setText(func_str or "")
        self.output.clear()

    def _calc(self):
        f1    = self.func1_input.text().strip()
        f2    = self.func2_input.text().strip()
        a_str = self.lower.text().strip()
        b_str = self.upper.text().strip()

        if not (f1 and f2):
            Toast(self.app.central_widget, "Please enter both functions.", is_error=True)
            return
        if not (a_str and b_str):
            Toast(self.app.central_widget, "Please enter both bounds a and b.", is_error=True)
            return
        try:
            a, b = float(a_str), float(b_str)
            import core.integrator as integrator
            area = integrator.area_between_curves(f1, f2, a, b)
            self.output.setText(
                f"// AREA BETWEEN CURVES\n\n"
                f"   f(x) = {f1}\n"
                f"   g(x) = {f2}\n\n"
                f"   Area from {a} to {b}\n\n"
                f"   A = {area:.6f}"
            )
            Toast(self.app.central_widget, "Area computed successfully.")
        except Exception as e:
            self.output.setText(f"// [error]  {e}")
            Toast(self.app.central_widget, str(e), is_error=True)

    def _plot(self):
        f1 = self.func1_input.text().strip()
        f2 = self.func2_input.text().strip()
        if f1 and f2:
            self.app.graph_page.plot_area(f1, f2)
            self.app.stack.setCurrentIndex(3)
            self.app.sidebar._select(1, 3)
        else:
            Toast(self.app.central_widget, "Please enter both functions.", is_error=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN WINDOW
# ══════════════════════════════════════════════════════════════════════════════

class CalculusApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CALC_PIT  ·  v2.0")
        self.setMinimumSize(960, 680)
        self.setStyleSheet(STYLESHEET)
        self._build()

    def _build(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        root = QHBoxLayout(self.central_widget)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = SidebarNav(self)
        root.addWidget(self.sidebar)

        vline = QFrame()
        vline.setFrameShape(QFrame.Shape.VLine)
        vline.setObjectName("separator")
        vline.setFixedWidth(1)
        root.addWidget(vline)

        self.stack = QStackedWidget()
        self.stack.setObjectName("contentArea")
        root.addWidget(self.stack, 1)

        # Instantiate pages
        self.home_page     = HomePage(self)
        self.eval_page     = EvalPage(self)
        self.integral_page = IntegralPage(self)
        self.graph_page    = GraphPage(self)
        self.symbolic_page = SymbolicPage(self)
        self.area_page     = AreaPage(self)

        for page in (self.home_page, self.eval_page, self.integral_page,
                     self.graph_page, self.symbolic_page, self.area_page):
            self.stack.addWidget(page)

        self.sidebar.page_changed.connect(self.stack.setCurrentIndex)
        self.stack.setCurrentIndex(0)


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = CalculusApp()
    window.show()
    sys.exit(app.exec())