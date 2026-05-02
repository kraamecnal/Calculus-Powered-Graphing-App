import sys
import os

os.environ["QT_API"] = "pyqt6"

import matplotlib
matplotlib.rcParams.update({
    'font.family': 'monospace',
    'axes.facecolor': '#1a1a2e',
    'figure.facecolor': '#121212',
    'axes.edgecolor': '#2a2a4a',
    'axes.labelcolor': '#8888aa',
    'xtick.color': '#666688',
    'ytick.color': '#666688',
    'grid.color': '#1e1e3a',
    'text.color': '#e0e0ff',
    'axes.titlecolor': '#c8c8ff',
    'legend.facecolor': '#1e1e2e',
    'legend.edgecolor': '#3a3a5a',
    'lines.antialiased': True,
    'patch.antialiased': True,
})

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QTextEdit, QFrame, QSizePolicy,
    QStackedWidget, QScrollArea, QFileDialog, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal
from PyQt6.QtGui import QClipboard, QFont, QPalette, QColor

# ─────────────────────────────────────────────────────────────────
# DESIGN TOKENS — "Void Cartographer" theme
# Deep space blacks + electric cyan/violet accents
# ─────────────────────────────────────────────────────────────────
BG_BASE         = "#0d0d14"   # near-black void
BG_SURFACE      = "#13131f"   # card surface
BG_ELEVATED     = "#1a1a2e"   # elevated panels
BG_SIDEBAR      = "#0f0f1a"   # sidebar bg
BORDER_SUBTLE   = "#1e1e35"   # hairline borders
BORDER_NORMAL   = "#2a2a45"   # normal borders
BORDER_FOCUS    = "#00d4ff"   # focus ring — electric cyan

ACCENT_CYAN     = "#00d4ff"   # primary — electric cyan
ACCENT_VIOLET   = "#9b59ff"   # secondary — violet
ACCENT_GREEN    = "#00ff9d"   # success — neon green
ACCENT_AMBER    = "#ffaa00"   # warning — amber
ACCENT_RED      = "#ff4d6d"   # error — hot coral

TEXT_PRIMARY    = "#f0f0ff"   # near-white
TEXT_SECONDARY  = "#9090b8"   # muted purple-grey
TEXT_SUBTLE     = "#50507a"   # very muted
TEXT_MONO       = "#00d4ff"   # monospace text color

SIDEBAR_WIDTH   = 64
SIDEBAR_EXPANDED = 200

# Nav items: (icon, label, page_index)
NAV_ITEMS = [
    ("⌂", "Home",     0),
    ("◈", "Graph",    3),
    ("f′", "Evaluate", 1),
    ("∫",  "Integral", 2),
    ("⊢⊣", "Area",    5),
    ("Σ",  "Symbolic", 4),
]

STYLESHEET = f"""
/* ── Global Reset ── */
* {{
    outline: none;
}}
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

/* ── Content Area ── */
QWidget#contentArea {{
    background-color: {BG_BASE};
}}

/* ── Page Titles ── */
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

/* ── Function Input (main) ── */
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
QLineEdit#funcInput::placeholder {{
    color: {TEXT_SUBTLE};
    font-style: italic;
}}

/* ── Bound / Eval Inputs ── */
QLineEdit#boundInput {{
    padding: 10px 14px;
    font-size: 14px;
    font-family: "Consolas", monospace;
    border: 1.5px solid {BORDER_NORMAL};
    border-radius: 10px;
    background-color: {BG_SURFACE};
    color: {ACCENT_AMBER};
    selection-background-color: rgba(255,170,0,0.2);
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
    selection-background-color: rgba(0,255,157,0.2);
}}
QLineEdit#evalInput:focus {{
    border: 1.5px solid {ACCENT_GREEN};
    background-color: rgba(0, 255, 157, 0.04);
}}

/* ── Action Cards (Home) ── */
QPushButton#actionCard {{
    background-color: {BG_SURFACE};
    color: {TEXT_PRIMARY};
    padding: 18px 24px;
    font-size: 13px;
    font-weight: 400;
    border: 1px solid {BORDER_NORMAL};
    border-radius: 14px;
    text-align: left;
    letter-spacing: 0.2px;
}}
QPushButton#actionCard:hover {{
    background-color: {BG_ELEVATED};
    border-color: {ACCENT_CYAN};
    color: {TEXT_PRIMARY};
}}
QPushButton#actionCard:pressed {{
    background-color: rgba(0,212,255,0.06);
}}

/* ── Accent Buttons ── */
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
QPushButton#accentCyan:hover {{
    background-color: #33ddff;
}}
QPushButton#accentCyan:pressed {{
    background-color: #0099cc;
}}

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
QPushButton#accentGreen:hover {{
    background-color: rgba(0, 255, 157, 0.1);
}}

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
QPushButton#accentAmber:hover {{
    background-color: rgba(255, 170, 0, 0.1);
}}

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
QPushButton#accentViolet:hover {{
    background-color: rgba(155, 89, 255, 0.1);
}}

/* ── Tool / Utility Buttons ── */
QPushButton#toolBtn {{
    background-color: {BG_SURFACE};
    color: {TEXT_SECONDARY};
    padding: 7px 14px;
    font-size: 11px;
    font-family: "Consolas", monospace;
    border: 1px solid {BORDER_NORMAL};
    border-radius: 8px;
    letter-spacing: 0.5px;
}}
QPushButton#toolBtn:hover {{
    background-color: {BG_ELEVATED};
    color: {TEXT_PRIMARY};
    border-color: {BORDER_FOCUS};
}}

/* ── Toggle Buttons ── */
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

/* ── Output Display ── */
QTextEdit#outputDisplay {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_NORMAL};
    border-radius: 12px;
    font-family: "Cascadia Code", "Consolas", "Courier New", monospace;
    font-size: 13px;
    color: {TEXT_PRIMARY};
    padding: 18px;
    line-height: 1.8;
    selection-background-color: rgba(0,212,255,0.2);
}}

/* ── Mini Graph Preview ── */
QWidget#miniGraphFrame {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_NORMAL};
    border-radius: 12px;
}}

/* ── Error Toast ── */
QLabel#errorToast {{
    background-color: rgba(255, 77, 109, 0.12);
    color: {ACCENT_RED};
    border: 1px solid rgba(255, 77, 109, 0.3);
    border-radius: 10px;
    padding: 10px 18px;
    font-size: 12px;
    font-family: "Consolas", monospace;
}}

/* ── Status/Info Label ── */
QLabel#statusLabel {{
    color: {TEXT_SUBTLE};
    font-size: 11px;
    font-family: "Consolas", monospace;
    letter-spacing: 0.5px;
}}

/* ── Section Divider Label ── */
QLabel#sectionLabel {{
    color: {TEXT_SUBTLE};
    font-size: 10px;
    letter-spacing: 3px;
    font-weight: 600;
}}

/* ── Scroll Bars ── */
QScrollBar:vertical {{
    background: transparent;
    width: 4px;
    border: none;
    margin: 0px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER_NORMAL};
    border-radius: 2px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: {TEXT_SUBTLE};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QScrollBar:horizontal {{ height: 0px; }}

/* ── Separator ── */
QFrame#separator {{
    color: {BORDER_SUBTLE};
    background-color: {BORDER_SUBTLE};
    max-height: 1px;
}}
"""


# ─────────────────────────────────────────────
# TOAST NOTIFICATION WIDGET
# ─────────────────────────────────────────────
class Toast(QWidget):
    """Auto-dismissing toast notification."""
    def __init__(self, parent, message, is_error=False):
        super().__init__(parent)
        self.setFixedWidth(360)
        accent = ACCENT_RED if is_error else ACCENT_GREEN
        bg = "rgba(255,77,109,0.12)" if is_error else "rgba(0,255,157,0.1)"
        border = "rgba(255,77,109,0.3)" if is_error else "rgba(0,255,157,0.3)"

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 10px;
            }}
            QLabel {{ color: {accent}; font-size: 12px; background: transparent; border: none; }}
        """)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        icon = QLabel("⊘" if is_error else "✓")
        icon.setStyleSheet(f"font-size: 14px; color: {accent}; border: none; background: transparent;")
        msg_lbl = QLabel(message)
        msg_lbl.setWordWrap(True)
        lay.addWidget(icon)
        lay.addWidget(msg_lbl, 1)

        self.opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)

        self._position_toast()
        self.show()

        # Auto dismiss after 3s
        QTimer.singleShot(2500, self._fade_out)

    def _position_toast(self):
        pw = self.parent().width()
        ph = self.parent().height()
        self.adjustSize()
        self.move(pw - self.width() - 20, ph - self.height() - 20)

    def _fade_out(self):
        self.anim = QPropertyAnimation(self.opacity, b"opacity")
        self.anim.setDuration(400)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.finished.connect(self.deleteLater)
        self.anim.start()


# ─────────────────────────────────────────────
# MATPLOTLIB CANVAS (Responsive + Styled)
# ─────────────────────────────────────────────
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
        self.ax.grid(True, color='#1e1e3a', linewidth=0.5, linestyle='-', alpha=0.8)
        self.ax.axhline(0, color='#333355', linewidth=0.8, zorder=1)
        self.ax.axvline(0, color='#333355', linewidth=0.8, zorder=1)
        self.ax.set_title("awaiting input", color='#50507a',
                          fontsize=9, fontstyle='italic', pad=12,
                          fontfamily='Consolas')


class MiniCanvas(FigureCanvas):
    """Compact preview canvas for homepage."""
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
        self.ax.set_title("live preview", color='#333355', fontsize=8,
                          fontstyle='italic', pad=6)

    def update_preview(self, func_str):
        try:
            import numpy as np
            from sympy import sympify, lambdify
            from sympy.abc import x
            sympified = sympify(func_str)
            f_callable = lambdify(x, sympified, "numpy")
            x_vals = np.linspace(-8, 8, 400)
            y_vals = f_callable(x_vals) * np.ones_like(x_vals)
            # Clip extreme values
            y_vals = np.clip(y_vals, -100, 100)
            self.ax.clear()
            self._style()
            self.ax.plot(x_vals, y_vals, color=ACCENT_CYAN, linewidth=1.5,
                         antialiased=True, zorder=3)
            self.ax.fill_between(x_vals, y_vals, alpha=0.06, color=ACCENT_CYAN)
            self.ax.set_title(f"f(x) = {func_str}", color='#6666aa',
                              fontsize=8, fontstyle='italic', pad=6)
            self.draw()
        except Exception:
            self.ax.clear()
            self._style()
            self.draw()


# ─────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────
class SidebarNav(QWidget):
    page_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(SIDEBAR_WIDTH)
        self._active = 0
        self._btns = []
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 16, 6, 16)
        lay.setSpacing(4)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        # App logo mark
        logo = QLabel("◉")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(f"color: {ACCENT_CYAN}; font-size: 22px; padding: 8px 0 16px 0;")
        lay.addWidget(logo)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setObjectName("separator")
        lay.addWidget(sep)
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
            btn.clicked.connect(lambda checked, pi=page_idx, ni=i: self._select(ni, pi))

            lbl = QLabel(label.upper())
            lbl.setObjectName("navLabel")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f"color: {TEXT_SUBTLE}; font-size: 8px; letter-spacing: 1px;")

            cell_lay.addWidget(btn)
            cell_lay.addWidget(lbl)
            lay.addWidget(cell)

            self._btns.append((btn, lbl))

        lay.addStretch()

        # Bottom: settings placeholder
        settings = QLabel("⊙")
        settings.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings.setStyleSheet(f"color: {TEXT_SUBTLE}; font-size: 16px; padding: 8px;")
        lay.addWidget(settings)

        self._select(0, 0)

    def _select(self, nav_idx, page_idx):
        # Deactivate old
        if self._active < len(self._btns):
            old_btn, old_lbl = self._btns[self._active]
            old_btn.setProperty("active", False)
            old_btn.style().unpolish(old_btn)
            old_btn.style().polish(old_btn)
            old_lbl.setStyleSheet(f"color: {TEXT_SUBTLE}; font-size: 8px; letter-spacing: 1px;")

        self._active = nav_idx
        btn, lbl = self._btns[nav_idx]
        btn.setProperty("active", True)
        btn.style().unpolish(btn)
        btn.style().polish(btn)
        lbl.setStyleSheet(f"color: {ACCENT_CYAN}; font-size: 8px; letter-spacing: 1px;")

        self.page_changed.emit(page_idx)


# ─────────────────────────────────────────────
# SHARED: PAGE HEADER
# ─────────────────────────────────────────────
def make_header(title: str, subtitle: str = "") -> QVBoxLayout:
    lay = QVBoxLayout()
    lay.setSpacing(4)
    t = QLabel(title)
    t.setObjectName("pageTitle")
    lay.addWidget(t)
    if subtitle:
        s = QLabel(subtitle)
        s.setObjectName("pageSubtitle")
        lay.addWidget(s)
    lay.addSpacing(8)
    sep = QFrame()
    sep.setFrameShape(QFrame.Shape.HLine)
    sep.setObjectName("separator")
    lay.addWidget(sep)
    return lay


# ─────────────────────────────────────────────
# PAGE: HOME
# ─────────────────────────────────────────────
class HomePage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self._preview_timer = QTimer()
        self._preview_timer.setSingleShot(True)
        self._preview_timer.timeout.connect(self._update_preview)
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(scroll)

        card = QWidget()
        scroll.setWidget(card)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(40, 40, 40, 40)
        lay.setSpacing(0)

        # Header
        for w in make_header("Calculus Engine", "VOID CARTOGRAPHER · v2.0").children():
            if isinstance(w, QWidget):
                lay.addWidget(w)
        lay.addSpacing(28)

        # Function input
        input_label = QLabel("FUNCTION")
        input_label.setObjectName("sectionLabel")
        lay.addWidget(input_label)
        lay.addSpacing(8)

        self.func_input = QLineEdit()
        self.func_input.setObjectName("funcInput")
        self.func_input.setPlaceholderText("f(x) = e.g.   sin(x) * x**2 - 3*x + 1")
        self.func_input.textChanged.connect(self._on_text_changed)
        self.func_input.returnPressed.connect(self._go_graph)
        lay.addWidget(self.func_input)
        lay.addSpacing(20)

        # Mini preview
        preview_label = QLabel("LIVE PREVIEW")
        preview_label.setObjectName("sectionLabel")
        lay.addWidget(preview_label)
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
        actions_label = QLabel("OPERATIONS")
        actions_label.setObjectName("sectionLabel")
        lay.addWidget(actions_label)
        lay.addSpacing(10)

        action_defs = [
            ("◈  Plot  f(x),  f′(x)  and area",
             "Render full graph with derivative overlay", self._go_graph, ACCENT_CYAN),
            ("f′  Evaluate and Higher Derivatives",
             "Compute f(x), f′(x), f″(x), f‴(x) at any x value", self._go_eval, ACCENT_GREEN),
            ("∫  Definite Integral",
             "Numerical integration between two bounds", self._go_integral, ACCENT_AMBER),
            ("⊢⊣  Area Between Curves",
             "Calculate and visualize area between two functions", self._go_area, ACCENT_VIOLET),
            ("Σ  Symbolic Analysis",
             "Show derivative and antiderivative expressions", self._go_symbolic, ACCENT_VIOLET),
        ]

        for icon_text, desc, slot, color in action_defs:
            btn = QPushButton(icon_text)
            btn.setObjectName("actionCard")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(56)
            btn.clicked.connect(slot)
            # Inline style for the colored left marker
            btn.setStyleSheet(btn.styleSheet() + f"""
                QPushButton#actionCard {{ border-left: 3px solid {color}; }}
            """)
            lay.addWidget(btn)
            lay.addSpacing(6)

        lay.addStretch()

    def _on_text_changed(self):
        self._preview_timer.start(400)

    def _update_preview(self):
        text = self.func_input.text().strip()
        if text:
            self.mini_canvas.update_preview(text)
        else:
            self.mini_canvas.ax.clear()
            self.mini_canvas._style()
            self.mini_canvas.draw()

    def _func(self): return self.func_input.text().strip()

    def _go_graph(self):
        f = self._func()
        if f:
            self.app.graph_page.plot(f)
            self.app.sidebar.page_changed.emit(3)
            self.app.stack.setCurrentIndex(3)
            self.app.sidebar._select(1, 3)

    def _go_eval(self):
        self.app.eval_page.set_func(self._func())
        self.app.stack.setCurrentIndex(1)
        self.app.sidebar._select(2, 1)

    def _go_integral(self):
        self.app.integral_page.set_func(self._func())
        self.app.stack.setCurrentIndex(2)
        self.app.sidebar._select(3, 2)

    def _go_area(self):
        self.app.area_page.set_func1(self._func())
        self.app.stack.setCurrentIndex(5)
        self.app.sidebar._select(4, 5)

    def _go_symbolic(self):
        f = self._func()
        if f:
            self.app.symbolic_page.show_symbolic(f)
        self.app.stack.setCurrentIndex(4)
        self.app.sidebar._select(4, 4)


# ─────────────────────────────────────────────
# PAGE: EVALUATE AT POINT
# ─────────────────────────────────────────────
class EvalPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.func_str = ""
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)

        card = QWidget()
        scroll.setWidget(card)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(40, 40, 40, 40)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        for w in make_header("Evaluate", "f(x) AND f′(x) AT A POINT").children():
            if isinstance(w, QWidget): lay.addWidget(w)
        lay.addSpacing(24)

        self.func_label = QLabel("No function set — go to Home and enter f(x)")
        self.func_label.setStyleSheet(f"color: {TEXT_SUBTLE}; font-family: Consolas; font-size: 12px;")
        lay.addWidget(self.func_label)
        lay.addSpacing(24)

        # Derivative order
        order_label = QLabel("DERIVATIVE ORDER")
        order_label.setObjectName("sectionLabel")
        lay.addWidget(order_label)
        lay.addSpacing(8)

        order_row = QHBoxLayout()
        order_row.setSpacing(6)

        self.order_buttons = []
        for i in range(1, 5):
            btn = QPushButton(f"{i}" if i == 1 else f"{chr(0x2032) * i}")  # 1, ′, ″, ‴
            btn.setObjectName("toggleBtn")
            btn.setProperty("active", i == 1)
            btn.setFixedWidth(50)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, o=i: self._set_order(o))
            order_row.addWidget(btn)
            self.order_buttons.append((i, btn))

        order_row.addStretch()
        lay.addLayout(order_row)
        self.deriv_order = 1
        lay.addSpacing(20)

        x_label = QLabel("X VALUE")
        x_label.setObjectName("sectionLabel")
        lay.addWidget(x_label)
        lay.addSpacing(8)

        input_row = QHBoxLayout()
        self.x_input = QLineEdit()
        self.x_input.setObjectName("evalInput")
        self.x_input.setPlaceholderText("enter x  e.g.  2.5")
        self.x_input.setFixedWidth(200)
        self.x_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.x_input.returnPressed.connect(self._calc)

        self.calc_btn = QPushButton("EVALUATE")
        self.calc_btn.setObjectName("accentGreen")
        self.calc_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.calc_btn.clicked.connect(self._calc)

        input_row.addWidget(self.x_input)
        input_row.addWidget(self.calc_btn)
        input_row.addStretch()
        lay.addLayout(input_row)
        lay.addSpacing(24)

        out_label = QLabel("RESULT")
        out_label.setObjectName("sectionLabel")
        lay.addWidget(out_label)
        lay.addSpacing(8)

        self.output = QTextEdit()
        self.output.setObjectName("outputDisplay")
        self.output.setReadOnly(True)
        self.output.setMaximumWidth(520)
        self.output.setMinimumHeight(160)
        lay.addWidget(self.output)
        lay.addStretch()

    def set_func(self, func_str):
        self.func_str = func_str or ""
        self.func_label.setText(
            f"f(x) = {func_str}" if func_str
            else "No function set — go to Home and enter f(x)"
        )
        self.func_label.setStyleSheet(
            f"color: {ACCENT_CYAN}; font-family: Consolas; font-size: 13px;"
            if func_str else
            f"color: {TEXT_SUBTLE}; font-family: Consolas; font-size: 12px;"
        )
        self.output.clear()

    def _set_order(self, order):
        self.deriv_order = order
        # Update button states
        for o, btn in self.order_buttons:
            btn.setProperty("active", o == order)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _calc(self):
        if not self.func_str:
            self._show_toast("No function set. Return to Home.", is_error=True)
            return
        x_str = self.x_input.text().strip()
        if not x_str:
            self._show_toast("Please enter an x value.", is_error=True)
            return
        try:
            x_val = float(x_str)
            import core.parser as parser
            import core.differentiator as differentiator
            pretty_f = parser.parse_function(self.func_str)
            f_at_x  = parser.parse_function(self.func_str, x_val, True)
            df_at_x = differentiator.differentiate(self.func_str, x_val, True, self.deriv_order)
            df_sym  = differentiator.differentiate(self.func_str, order=self.deriv_order)
            
            # Build derivative notation
            if self.deriv_order == 1:
                deriv_notation = "f′"
            elif self.deriv_order == 2:
                deriv_notation = "f″"
            elif self.deriv_order == 3:
                deriv_notation = "f‴"
            else:
                deriv_notation = f"f^({self.deriv_order})"
            
            self.output.setText(
                f"f(x) = {pretty_f}\n"
                f"{deriv_notation}(x) = {df_sym}\n\n"
                f"// EVALUATION  @  x = {x_val}\n\n"
                f"   f({x_val})    =  {f_at_x}\n"
                f"   {deriv_notation}({x_val})   =  {df_at_x}"
            )
            self._show_toast("Evaluated successfully.")
        except Exception as e:
            self.output.setText(f"// [error]  {str(e)}")
            self._show_toast(str(e), is_error=True)

    def _show_toast(self, msg, is_error=False):
        Toast(self.app.central_widget, msg, is_error)


# ─────────────────────────────────────────────
# PAGE: DEFINITE INTEGRAL
# ─────────────────────────────────────────────
class IntegralPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.func_str = ""
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)

        card = QWidget()
        scroll.setWidget(card)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(40, 40, 40, 40)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        for w in make_header("Definite Integral", "NUMERICAL INTEGRATION BETWEEN BOUNDS").children():
            if isinstance(w, QWidget): lay.addWidget(w)
        lay.addSpacing(24)

        self.func_label = QLabel("No function set — go to Home and enter f(x)")
        self.func_label.setStyleSheet(f"color: {TEXT_SUBTLE}; font-family: Consolas; font-size: 12px;")
        lay.addWidget(self.func_label)
        lay.addSpacing(24)

        bounds_label = QLabel("BOUNDS")
        bounds_label.setObjectName("sectionLabel")
        lay.addWidget(bounds_label)
        lay.addSpacing(8)

        bounds_row = QHBoxLayout()
        self.lower = QLineEdit()
        self.lower.setObjectName("boundInput")
        self.lower.setPlaceholderText("a")
        self.lower.setFixedWidth(90)
        self.lower.setAlignment(Qt.AlignmentFlag.AlignCenter)

        arrow_lbl = QLabel("→")
        arrow_lbl.setStyleSheet(f"color: {TEXT_SUBTLE}; font-size: 14px; padding: 0 8px;")

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

        bounds_row.addWidget(self.lower)
        bounds_row.addWidget(arrow_lbl)
        bounds_row.addWidget(self.upper)
        bounds_row.addSpacing(16)
        bounds_row.addWidget(calc_btn)
        bounds_row.addStretch()
        lay.addLayout(bounds_row)
        lay.addSpacing(24)

        out_label = QLabel("RESULT")
        out_label.setObjectName("sectionLabel")
        lay.addWidget(out_label)
        lay.addSpacing(8)

        self.output = QTextEdit()
        self.output.setObjectName("outputDisplay")
        self.output.setReadOnly(True)
        self.output.setMaximumWidth(520)
        self.output.setMinimumHeight(160)
        lay.addWidget(self.output)
        lay.addStretch()

    def set_func(self, func_str):
        self.func_str = func_str or ""
        self.func_label.setText(
            f"f(x) = {func_str}" if func_str
            else "No function set — go to Home and enter f(x)"
        )
        self.func_label.setStyleSheet(
            f"color: {ACCENT_CYAN}; font-family: Consolas; font-size: 13px;"
            if func_str else
            f"color: {TEXT_SUBTLE}; font-family: Consolas; font-size: 12px;"
        )
        self.output.clear()

    def _calc(self):
        if not self.func_str:
            self._show_toast("No function set. Return to Home.", is_error=True)
            return
        a_str = self.lower.text().strip()
        b_str = self.upper.text().strip()
        if not (a_str and b_str):
            self._show_toast("Please enter both bounds a and b.", is_error=True)
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
            self._show_toast("Integral computed.")
        except Exception as e:
            self.output.setText(f"// [error]  {str(e)}")
            self._show_toast(str(e), is_error=True)

    def _show_toast(self, msg, is_error=False):
        Toast(self.app.central_widget, msg, is_error)


# ─────────────────────────────────────────────
# PAGE: GRAPH
# ─────────────────────────────────────────────
class GraphPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self._show_grid = True
        self._show_legend = True
        self._current_func = ""
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(0)

        # Top bar
        top = QHBoxLayout()
        top.setSpacing(8)

        self.title_lbl = QLabel("◈ Graph")
        self.title_lbl.setObjectName("pageTitle")

        self.func_lbl = QLabel("")
        self.func_lbl.setStyleSheet(f"color: {ACCENT_CYAN}; font-family: Consolas; font-size: 12px;")

        top.addWidget(self.title_lbl)
        top.addSpacing(12)
        top.addWidget(self.func_lbl, 1)

        # Toggle buttons
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

        self.dl_btn = QPushButton("↓ Export")
        self.dl_btn.setObjectName("toolBtn")
        self.dl_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dl_btn.clicked.connect(self._download)

        top.addWidget(self.grid_btn)
        top.addWidget(self.legend_btn)
        top.addSpacing(4)
        top.addWidget(self.dl_btn)
        lay.addLayout(top)
        lay.addSpacing(12)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setObjectName("separator")
        lay.addWidget(sep)
        lay.addSpacing(8)

        self.canvas = MplCanvas(self, width=8, height=6, dpi=110)
        lay.addWidget(self.canvas, 1)

    def _toggle_grid(self):
        self._show_grid = not self._show_grid
        self.grid_btn.setProperty("active", self._show_grid)
        self.grid_btn.style().unpolish(self.grid_btn)
        self.grid_btn.style().polish(self.grid_btn)
        self.canvas.ax.grid(self._show_grid)
        self.canvas.draw()

    def _toggle_legend(self):
        self._show_legend = not self._show_legend
        self.legend_btn.setProperty("active", self._show_legend)
        self.legend_btn.style().unpolish(self.legend_btn)
        self.legend_btn.style().polish(self.legend_btn)
        legend = self.canvas.ax.get_legend()
        if legend:
            legend.set_visible(self._show_legend)
        self.canvas.draw()

    def _download(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Plot", "calc_plot.png",
            "PNG (*.png);;SVG (*.svg);;PDF (*.pdf)"
        )
        if path:
            self.canvas.fig.savefig(path, dpi=300, bbox_inches='tight')
            Toast(self.app.central_widget, f"Saved: {os.path.basename(path)}")

    def plot(self, func_str):
        self._current_func = func_str
        self.func_lbl.setText(f"f(x) = {func_str}")
        try:
            import numpy as np
            from sympy import sympify, lambdify, diff
            from sympy.abc import x

            sym = sympify(func_str)
            x_vals = np.linspace(-10, 10, 800)
            f_fn = lambdify(x, sym, "numpy")
            df_fn = lambdify(x, diff(sym), "numpy")

            y_f  = f_fn(x_vals) * np.ones_like(x_vals)
            y_df = df_fn(x_vals) * np.ones_like(x_vals)

            # Clip
            y_f  = np.clip(y_f, -200, 200)
            y_df = np.clip(y_df, -200, 200)

            self.canvas.ax.clear()
            self.canvas.style_axes()

            self.canvas.ax.plot(x_vals, y_f, label="f(x)",
                                color=ACCENT_CYAN, linewidth=2.0,
                                antialiased=True, zorder=3)
            self.canvas.ax.plot(x_vals, y_df, label="f′(x)",
                                color=ACCENT_VIOLET, linewidth=1.4,
                                linestyle="--", antialiased=True, zorder=3, alpha=0.85)
            self.canvas.ax.fill_between(x_vals, y_f, alpha=0.06,
                                        color=ACCENT_CYAN, zorder=2)

            self.canvas.ax.set_title(
                f"f(x) = {func_str}", color='#8888cc',
                fontsize=10, pad=12, fontfamily='Consolas'
            )

            if self._show_legend:
                self.canvas.ax.legend(
                    framealpha=0.85, fontsize=9,
                    labelcolor=TEXT_PRIMARY,
                    facecolor='#1a1a2e', edgecolor='#2a2a4a'
                )

            self.canvas.ax.grid(self._show_grid)
            self.canvas.draw()

        except Exception as e:
            self.canvas.ax.clear()
            self.canvas.style_axes()
            self.canvas.ax.set_title(f"parse error: {e}",
                                     color=ACCENT_RED, fontsize=9)
            self.canvas.draw()
            Toast(self.app.central_widget, str(e), is_error=True)

    def plot_area(self, func1_str, func2_str):
        """Plot two functions with shaded area between them."""
        self.func_lbl.setText(f"f(x) = {func1_str},  g(x) = {func2_str}")
        try:
            import numpy as np
            from sympy import sympify, lambdify
            from sympy.abc import x

            sym1 = sympify(func1_str)
            sym2 = sympify(func2_str)
            
            x_vals = np.linspace(-10, 10, 800)
            f1_fn = lambdify(x, sym1, "numpy")
            f2_fn = lambdify(x, sym2, "numpy")

            y_f1 = f1_fn(x_vals) * np.ones_like(x_vals)
            y_f2 = f2_fn(x_vals) * np.ones_like(x_vals)

            # Clip
            y_f1 = np.clip(y_f1, -200, 200)
            y_f2 = np.clip(y_f2, -200, 200)

            self.canvas.ax.clear()
            self.canvas.style_axes()

            self.canvas.ax.plot(x_vals, y_f1, label=f"f(x) = {func1_str}",
                                color=ACCENT_CYAN, linewidth=2.0,
                                antialiased=True, zorder=3)
            self.canvas.ax.plot(x_vals, y_f2, label=f"g(x) = {func2_str}",
                                color=ACCENT_GREEN, linewidth=2.0,
                                antialiased=True, zorder=3)
            
            # Shade area between curves
            self.canvas.ax.fill_between(x_vals, y_f1, y_f2, 
                                        where=(y_f1 >= y_f2),
                                        alpha=0.25, color=ACCENT_VIOLET, 
                                        label="Area between", zorder=2)
            self.canvas.ax.fill_between(x_vals, y_f1, y_f2, 
                                        where=(y_f1 < y_f2),
                                        alpha=0.25, color=ACCENT_AMBER, zorder=2)

            self.canvas.ax.set_title(
                f"Area between curves", color='#8888cc',
                fontsize=10, pad=12, fontfamily='Consolas'
            )

            if self._show_legend:
                self.canvas.ax.legend(
                    framealpha=0.85, fontsize=9,
                    labelcolor=TEXT_PRIMARY,
                    facecolor='#1a1a2e', edgecolor='#2a2a4a'
                )

            self.canvas.ax.grid(self._show_grid)
            self.canvas.draw()
            Toast(self.app.central_widget, "Area visualization loaded.")

        except Exception as e:
            self.canvas.ax.clear()
            self.canvas.style_axes()
            self.canvas.ax.set_title(f"parse error: {e}",
                                     color=ACCENT_RED, fontsize=9)
            self.canvas.draw()
            Toast(self.app.central_widget, str(e), is_error=True)


# ─────────────────────────────────────────────
# PAGE: SYMBOLIC
# ─────────────────────────────────────────────
class SymbolicPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)

        card = QWidget()
        scroll.setWidget(card)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(40, 40, 40, 40)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        for w in make_header("Symbolic Analysis", "EXACT DERIVATIVE AND ANTIDERIVATIVE").children():
            if isinstance(w, QWidget): lay.addWidget(w)
        lay.addSpacing(24)

        out_label = QLabel("EXPRESSIONS")
        out_label.setObjectName("sectionLabel")
        lay.addWidget(out_label)
        lay.addSpacing(8)

        self.output = QTextEdit()
        self.output.setObjectName("outputDisplay")
        self.output.setReadOnly(True)
        self.output.setMaximumWidth(600)
        self.output.setMinimumHeight(220)
        lay.addWidget(self.output)
        lay.addSpacing(12)

        # Copy button
        copy_row = QHBoxLayout()
        self.copy_btn = QPushButton("⎘ Copy to Clipboard")
        self.copy_btn.setObjectName("toolBtn")
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.clicked.connect(self._copy)
        copy_row.addWidget(self.copy_btn)
        copy_row.addStretch()
        lay.addLayout(copy_row)
        lay.addStretch()

    def show_symbolic(self, func_str):
        try:
            import core.parser as parser
            import core.differentiator as differentiator
            import core.integrator as integrator

            pretty_f  = parser.parse_function(func_str)
            
            # Calculate multiple derivatives
            deriv1_sym = differentiator.differentiate(func_str, order=1)
            deriv2_sym = differentiator.differentiate(func_str, order=2)
            deriv3_sym = differentiator.differentiate(func_str, order=3)
            
            integ_sym = integrator.integration(func_str)

            self.output.setText(
                f"// ── FUNCTION ────────────────────────────────\n"
                f"   f(x)   =  {pretty_f}\n\n"
                f"// ── FIRST DERIVATIVE  f′(x) ────────────────\n"
                f"   f′(x)  =  {deriv1_sym}\n\n"
                f"// ── SECOND DERIVATIVE  f″(x) ───────────────\n"
                f"   f″(x)  =  {deriv2_sym}\n\n"
                f"// ── THIRD DERIVATIVE  f‴(x) ────────────────\n"
                f"   f‴(x)  =  {deriv3_sym}\n\n"
                f"// ── ANTIDERIVATIVE  ∫f(x) dx ────────────────\n"
                f"   F(x)   =  {integ_sym}  +  C"
            )
            Toast(self.app.central_widget, "Symbolic analysis complete.")
        except Exception as e:
            self.output.setText(f"// [error]  {str(e)}")
            Toast(self.app.central_widget, str(e), is_error=True)

    def _copy(self):
        text = self.output.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            Toast(self.app.central_widget, "Copied to clipboard.")


# ─────────────────────────────────────────────
# PAGE: AREA BETWEEN CURVES
# ─────────────────────────────────────────────
class AreaPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.func1_str = ""
        self.func2_str = ""
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)

        card = QWidget()
        scroll.setWidget(card)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(40, 40, 40, 40)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        for w in make_header("Area Between Curves", "CALCULATE AREA BETWEEN TWO FUNCTIONS").children():
            if isinstance(w, QWidget): lay.addWidget(w)
        lay.addSpacing(24)

        # Function 1
        func1_label = QLabel("FIRST FUNCTION f(x)")
        func1_label.setObjectName("sectionLabel")
        lay.addWidget(func1_label)
        lay.addSpacing(8)

        self.func1_input = QLineEdit()
        self.func1_input.setObjectName("funcInput")
        self.func1_input.setPlaceholderText("e.g.   x**2")
        lay.addWidget(self.func1_input)
        lay.addSpacing(16)

        # Function 2
        func2_label = QLabel("SECOND FUNCTION g(x)")
        func2_label.setObjectName("sectionLabel")
        lay.addWidget(func2_label)
        lay.addSpacing(8)

        self.func2_input = QLineEdit()
        self.func2_input.setObjectName("funcInput")
        self.func2_input.setPlaceholderText("e.g.   x")
        lay.addWidget(self.func2_input)
        lay.addSpacing(20)

        # Bounds
        bounds_label = QLabel("BOUNDS")
        bounds_label.setObjectName("sectionLabel")
        lay.addWidget(bounds_label)
        lay.addSpacing(8)

        bounds_row = QHBoxLayout()
        self.lower = QLineEdit()
        self.lower.setObjectName("boundInput")
        self.lower.setPlaceholderText("a")
        self.lower.setFixedWidth(90)
        self.lower.setAlignment(Qt.AlignmentFlag.AlignCenter)

        arrow_lbl = QLabel("→")
        arrow_lbl.setStyleSheet(f"color: {TEXT_SUBTLE}; font-size: 14px; padding: 0 8px;")

        self.upper = QLineEdit()
        self.upper.setObjectName("boundInput")
        self.upper.setPlaceholderText("b")
        self.upper.setFixedWidth(90)
        self.upper.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.upper.returnPressed.connect(self._calc)

        calc_btn = QPushButton("◆ COMPUTE AREA")
        calc_btn.setObjectName("accentViolet")
        calc_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        calc_btn.clicked.connect(self._calc)

        bounds_row.addWidget(self.lower)
        bounds_row.addWidget(arrow_lbl)
        bounds_row.addWidget(self.upper)
        bounds_row.addSpacing(16)
        bounds_row.addWidget(calc_btn)
        bounds_row.addStretch()
        lay.addLayout(bounds_row)
        lay.addSpacing(24)

        # Plot button
        plot_row = QHBoxLayout()
        self.plot_btn = QPushButton("◈ Visualize in Graph")
        self.plot_btn.setObjectName("accentCyan")
        self.plot_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.plot_btn.clicked.connect(self._plot)
        plot_row.addWidget(self.plot_btn)
        plot_row.addStretch()
        lay.addLayout(plot_row)
        lay.addSpacing(16)

        out_label = QLabel("RESULT")
        out_label.setObjectName("sectionLabel")
        lay.addWidget(out_label)
        lay.addSpacing(8)

        self.output = QTextEdit()
        self.output.setObjectName("outputDisplay")
        self.output.setReadOnly(True)
        self.output.setMaximumWidth(520)
        self.output.setMinimumHeight(160)
        lay.addWidget(self.output)
        lay.addStretch()

    def set_func1(self, func_str):
        self.func1_str = func_str or ""
        self.func1_input.setText(func_str)
        self.output.clear()

    def _calc(self):
        f1 = self.func1_input.text().strip()
        f2 = self.func2_input.text().strip()
        a_str = self.lower.text().strip()
        b_str = self.upper.text().strip()

        if not (f1 and f2):
            self._show_toast("Please enter both functions.", is_error=True)
            return
        if not (a_str and b_str):
            self._show_toast("Please enter both bounds a and b.", is_error=True)
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
            self._show_toast("Area computed successfully.")
        except Exception as e:
            self.output.setText(f"// [error]  {str(e)}")
            self._show_toast(str(e), is_error=True)

    def _plot(self):
        f1 = self.func1_input.text().strip()
        f2 = self.func2_input.text().strip()
        if f1 and f2:
            self.app.graph_page.plot_area(f1, f2)
            self.app.stack.setCurrentIndex(3)
            self.app.sidebar._select(1, 3)
        else:
            self._show_toast("Please enter both functions.", is_error=True)

    def _show_toast(self, msg, is_error=False):
        Toast(self.app.central_widget, msg, is_error)


# ─────────────────────────────────────────────
# MAIN WINDOW
# ─────────────────────────────────────────────
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

        # Sidebar
        self.sidebar = SidebarNav(self)
        root.addWidget(self.sidebar)

        # Thin separator line
        vline = QFrame()
        vline.setFrameShape(QFrame.Shape.VLine)
        vline.setObjectName("separator")
        vline.setFixedWidth(1)
        root.addWidget(vline)

        # Content stack
        self.stack = QStackedWidget()
        self.stack.setObjectName("contentArea")
        root.addWidget(self.stack, 1)

        # Pages
        self.home_page     = HomePage(self)
        self.eval_page     = EvalPage(self)
        self.integral_page = IntegralPage(self)
        self.graph_page    = GraphPage(self)
        self.symbolic_page = SymbolicPage(self)
        self.area_page     = AreaPage(self)

        # Order matches NAV_ITEMS page_idx values
        for page in (self.home_page, self.eval_page, self.integral_page,
                     self.graph_page, self.symbolic_page, self.area_page):
            self.stack.addWidget(page)

        # Wire sidebar
        self.sidebar.page_changed.connect(self.stack.setCurrentIndex)
        self.stack.setCurrentIndex(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = CalculusApp()
    window.show()
    sys.exit(app.exec())