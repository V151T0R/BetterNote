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
    hover = base.lighter(108) if is_dark else QColor(241, 243, 247)
    pressed = base.lighter(116) if is_dark else QColor(230, 233, 240)
    panel = QColor(base)
    panel.setAlpha(245)
    border = QColor(mid)
    border.setAlpha(120)
    subtext = QColor(text)
    subtext.setAlpha(160)
    disabled_text = QColor(text)
    disabled_text.setAlpha(90)

    pt = max(base_point_size, 8)
    font_family = "'Segoe UI', 'SF Pro Text', 'Inter', -apple-system, sans-serif"

    # Soothing desk background that lets the crisp white page with its drop shadow stand out
    desk_bg = QColor("#575757") if is_dark else QColor("#F0F2F6")

    return f"""
QMainWindow {{
    background-color: {window.name()};
}}

/* ---------- Scroll Area ---------- */
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
QScrollBar:vertical {{
    width: 10px;
}}
QScrollBar:horizontal {{
    height: 10px;
}}
QScrollBar::handle {{
    background: {_rgba(border, 180)};
    border-radius: 5px;
    min-height: 24px;
    min-width: 24px;
}}
QScrollBar::handle:hover {{
    background: {_rgba(border, 230)};
}}

/* Thickness Slider */
QSlider::groove:horizontal {{
    border: none;
    height: 4px;
    background: {border.name()};
    border-radius: 2px;
}}
QSlider::sub-page:horizontal {{
    background: {accent.name()};
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: #ffffff;
    border: 2px solid {_rgba(border, 140)};
    width: 16px;
    margin-top: -6px;
    margin-bottom: -6px;
    border-radius: 9px;
}}
QSlider::handle:horizontal:hover {{
    border: 4px solid {accent.name()};
}}
QSlider::handle:horizontal:pressed {{
    border: 5px solid {accent.name()};
}}

/* Vertical Thickness Slider */
QSlider:vertical, QSlider#thicknessSlider {{
    width: 24px;
}}
QSlider::groove:vertical {{
    border: none;
    width: 4px;
    background: {border.name()};
    border-radius: 2px;
}}
QSlider::add-page:vertical {{
    background: {accent.name()};
    border-radius: 2px;
}}
QSlider::sub-page:vertical {{
    background: {border.name()};
    border-radius: 2px;
}}
QSlider::handle:vertical {{
    background: #ffffff;
    border: 2px solid {_rgba(border, 140)};
    height: 14px;
    width: 18px;
    margin: 0 -7px;
    border-radius: 9px;
}}
QSlider::handle:vertical:hover {{
    border: 3px solid {accent.name()};
}}
QSlider::handle:vertical:pressed {{
    border: 4px solid {accent.name()};
}}
QScrollBar::add-line, QScrollBar::sub-line,
QScrollBar::add-page, QScrollBar::sub-page {{
    height: 0px;
    width: 0px;
    background: transparent;
}}

/* ---------- Floating Toolbar / Zoom Bar ---------- */
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

/* ---------- Generic Buttons ---------- */
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
    border-color: {border.name()};
}}
QPushButton:checked {{
    background-color: {accent.name()};
    color: {accent_text.name()};
    border-color: {accent.name()};
}}
QPushButton:checked:hover {{
    background-color: {accent.darker(108).name()};
    border-color: {accent.darker(108).name()};
}}
QPushButton:disabled {{
    background-color: transparent;
    border-color: transparent;
    color: {_rgba(text, 100)};
}}

/* ---------- Icon / Nav Buttons ---------- */
QPushButton#iconButton, QToolButton#iconButton, QPushButton#navButton {{
    padding: 6px;
    border-radius: 16px;
    background-color: transparent;
    border: 1px solid transparent;
}}
QPushButton#iconButton:hover, QToolButton#iconButton:hover, QPushButton#navButton:hover {{
    background-color: {_rgba(accent, 22)};
    border-color: transparent;
}}
QPushButton#iconButton:pressed, QToolButton#iconButton:pressed, QPushButton#navButton:pressed {{
    background-color: {_rgba(accent, 45)};
    border-color: transparent;
}}
QPushButton#iconButton:checked {{
    background-color: {accent.name()};
    border-color: {accent.name()};
}}
QPushButton#iconButton:checked:hover {{
    background-color: {accent.darker(110).name()};
    border-color: {accent.darker(110).name()};
}}
QPushButton#iconButton:disabled, QToolButton#iconButton:disabled, QPushButton#navButton:disabled {{
    background-color: transparent;
    border-color: transparent;
}}

/* ---------- Zoom Button ---------- */
QPushButton#zoomButton {{
    padding: 0px;
    border-radius: 14px;
    font-size: {pt + 2}pt;
}}
QPushButton#zoomButton:hover {{
    background-color: {_rgba(accent, 22)};
}}
QPushButton#zoomButton:pressed {{
    background-color: {_rgba(accent, 45)};
}}

/* ---------- File Menu Button ---------- */
QToolButton#fileMenuButton {{
    background-color: {accent.name()};
    color: {accent_text.name()};
    border: none;
    border-radius: 16px;
    padding: 7px 16px;
    font-size: {pt}pt;
    font-weight: 600;
}}
QToolButton#fileMenuButton:hover {{
    background-color: {accent.darker(112).name()};
}}
QToolButton#fileMenuButton:pressed {{
    background-color: {accent.darker(120).name()};
}}
QToolButton#fileMenuButton::menu-indicator {{
    width: 0px;
    height: 0px;
    image: none;
}}

/* ---------- Menu-indicator suppression (icon/color tools) ---------- */
QToolButton#iconButton::menu-indicator,
QToolButton#colorButton::menu-indicator {{
    width: 0px;
    height: 0px;
    image: none;
}}

/* ---------- Color / Thickness swatches ---------- */
QToolButton#colorButton {{
    padding: 0px;
    margin: 0px;
    border: 2px solid {_rgba(border, 140)};
    background: transparent;
}}
QPushButton#colorSwapButton {{
    padding: 0px;
    margin: 0px;
    border: 2px solid {_rgba(border, 140)};
    background: transparent;
}}
QPushButton#thicknessButton {{
    padding: 0px;
    margin: 0px;
    border: 2px solid {_rgba(border, 140)};
    background: transparent;
}}

/* ---------- Divider ---------- */
QFrame#toolbarDivider {{
    background-color: {border.name()};
    max-width: 1px;
    margin: 6px 3px;
}}

/* ---------- Menus ---------- */
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
    background-color: {_rgba(accent, 25)};
    color: {accent.name()};
}}
QMenu::item:disabled {{
    color: {_rgba(text, 100)};
}}
QMenu::separator {{
    height: 1px;
    background: {border.name()};
    margin: 6px 4px;
}}

/* ---------- Labels ---------- */
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

/* ---------- Dialogs & Message Boxes ---------- */
QMessageBox QLabel {{
    color: {text.name()};
    font-size: {pt}pt;
    qproperty-alignment: 'AlignCenter';
    min-width: 260px;
    padding: 8px;
}}
QMessageBox QPushButton {{
    background-color: {_rgba(border, 70)};
    border: 1px solid {_rgba(border, 120)};
    border-radius: 8px;
    padding: 6px 16px;
    min-width: 64px;
    font-size: {pt}pt;
    font-weight: 500;
    color: {text.name()};
}}
QMessageBox QPushButton:hover {{
    background-color: {_rgba(accent, 22)};
    border-color: {accent.name()};
}}
QMessageBox QPushButton:default {{
    background-color: {accent.name()};
    color: {accent_text.name()};
    border: 1px solid {accent.name()};
    font-weight: 600;
}}
QMessageBox QPushButton:default:hover {{
    background-color: {accent.darker(110).name()};
}}
"""

class Application:
    def __init__(self, sys_argv):
        self.app = QApplication(sys_argv)
        self.app.setStyle("Fusion")
        
        palette = self.app.palette()
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#4F46E5"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        self.app.setPalette(palette)
        
        self.main_window = MainWindow()

    def run(self):
        self.main_window.show()
        return self.app.exec()
