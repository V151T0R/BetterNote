import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from ui.main_window import MainWindow

def _rgba(color: QColor, alpha=None):
    a = color.alpha() if alpha is None else alpha
    return f"rgba({color.red()}, {color.green()}, {color.blue()}, {a})"

def build_theme_stylesheet(palette: QPalette, base_point_size: float) -> str:
    window = palette.color(QPalette.ColorRole.Window)
    base = palette.color(QPalette.ColorRole.Base)
    text = palette.color(QPalette.ColorRole.WindowText)
    mid = palette.color(QPalette.ColorRole.Mid)
    accent = palette.color(QPalette.ColorRole.Highlight)
    accent_text = palette.color(QPalette.ColorRole.HighlightedText)

    is_dark = base.lightness() < 128
    hover = base.lighter(130) if is_dark else base.darker(106)
    pressed = base.lighter(160) if is_dark else base.darker(112)
    panel = QColor(base)
    panel.setAlpha(240)
    border = QColor(mid)
    border.setAlpha(140)
    subtext = QColor(text)
    subtext.setAlpha(160)

    pt = max(base_point_size, 8)

    # For the background desk area (the scroll area viewport)
    desk_bg = window.darker(105) if is_dark else window.darker(103)

    return f"""
QMainWindow {{
    background-color: {window.name()};
}}
QScrollArea {{
    border: none;
    background: {desk_bg.name()};
}}
QScrollArea > QWidget > QWidget {{
    background: {desk_bg.name()};
}}
QScrollBar:vertical, QScrollBar:horizontal {{
    background: transparent;
    border: none;
    margin: 0px;
}}
QScrollBar:vertical {{ width: 10px; }}
QScrollBar:horizontal {{ height: 10px; }}
QScrollBar::handle {{
    background: {_rgba(border, 180)};
    border-radius: 5px;
    min-height: 24px;
    min-width: 24px;
}}
QScrollBar::handle:hover {{ background: {_rgba(border, 230)}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0px; width: 0px; }}
QWidget#floatingToolbar {{
    background-color: {_rgba(panel)};
    border: 1px solid {_rgba(border)};
    border-radius: 20px;
}}
QWidget#zoomBar {{
    background-color: {_rgba(panel)};
    border: 1px solid {_rgba(border)};
    border-radius: 16px;
}}
QPushButton {{
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: {pt}pt;
    color: {text.name()};
}}
QPushButton:hover {{
    background-color: {hover.name()};
    border-color: {border.name()};
}}
QPushButton:pressed {{
    background-color: {pressed.name()};
}}
QPushButton:checked {{
    background-color: {accent.name()};
    color: {accent_text.name()};
    border-color: {accent.name()};
}}
QPushButton#iconButton, QToolButton#iconButton, QPushButton#navButton {{
    padding: 6px;
    border-radius: 16px;
}}
QPushButton#zoomButton {{
    padding: 0px;
    border-radius: 14px;
    font-size: {pt + 2}pt;
}}
QToolButton#fileMenuButton {{
    background-color: {accent.name()};
    color: {accent_text.name()};
    border: none;
    border-radius: 16px;
    padding: 7px 16px;
    font-size: {pt}pt;
    font-weight: 600;
}}
QToolButton#fileMenuButton::menu-indicator {{ subcontrol-position: right center; }}
QToolButton#fileMenuButton:hover {{
    background-color: {accent.darker(112).name()};
}}
QToolButton#iconButton::menu-indicator {{ 
    image: none; 
}}
QToolButton#colorButton::menu-indicator {{ 
    image: none; 
}}
QToolButton#colorButton {{
    padding: 0px !important;
    margin: 0px !important;
}}
QPushButton#colorSwatch {{
    padding: 0px !important;
    margin: 0px !important;
}}
QPushButton#thicknessButton {{
    padding: 0px !important;
    margin: 0px !important;
}}
QFrame#toolbarDivider {{
    background-color: {border.name()};
    max-width: 1px;
    margin: 6px 3px;
}}
QMenu {{
    background-color: {base.name()};
    border: 1px solid {border.name()};
    border-radius: 12px;
    padding: 6px;
    font-size: {pt}pt;
}}
QMenu::item {{
    padding: 8px 20px;
    border-radius: 6px;
    color: {text.name()};
}}
QMenu::item:selected {{
    background-color: {hover.name()};
}}
QMenu::separator {{
    height: 1px;
    background: {border.name()};
    margin: 6px 4px;
}}
QLabel#pageLabel {{
    font-weight: 600;
    color: {text.name()};
    padding: 0 4px;
    font-size: {pt}pt;
}}
QLabel#zoomLabel {{
    font-weight: 600;
    color: {subtext.name()};
    padding: 0 2px;
    font-size: {max(pt - 1, 7)}pt;
    min-width: 42px;
}}
"""

class Application:
    def __init__(self, sys_argv):
        self.app = QApplication(sys_argv)
        self.app.setStyle("Fusion")
        self.main_window = MainWindow()

    def run(self):
        self.main_window.show()
        return self.app.exec()
