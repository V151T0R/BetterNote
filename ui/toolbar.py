from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QToolButton, QMenu, QWidgetAction, QFrame, QLabel, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor, QKeySequence, QAction
from PySide6.QtCore import Qt

class _WrapLayout(QWidget):
    def __init__(self, parent_widget, h_spacing=6, v_spacing=6, cols=8):
        self._container = parent_widget
        super().__init__()
        from PySide6.QtWidgets import QGridLayout
        self._layout = QGridLayout(parent_widget)
        self._layout.setContentsMargins(10, 8, 10, 8)
        self._layout.setHorizontalSpacing(h_spacing)
        self._layout.setVerticalSpacing(v_spacing)
        self._widgets = []
        self._cols = cols

    def addWidget(self, widget):
        idx = len(self._widgets)
        row, col = divmod(idx, self._cols)
        self._layout.addWidget(widget, row, col)
        self._widgets.append(widget)

    def clear(self):
        while self._layout.count():
            item = self._layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self._widgets = []

class ColorSwatchButton(QPushButton):
    def __init__(self, hex_color, on_click, accent_hex="#3d6bfd", removable_cb=None):
        super().__init__()
        self.hex_color = hex_color
        self.setObjectName("colorSwatch")
        self.setFixedSize(24, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(f"{hex_color}  (right-click to remove)")
        self.setStyleSheet(f"""
            QPushButton#colorSwatch {{
                background-color: {hex_color} !important;
                border: 2px solid rgba(0, 0, 0, 40) !important;
                border-radius: 12px !important;
            }}
            QPushButton#colorSwatch:hover {{
                border: 2px solid {accent_hex} !important;
            }}
        """)
        self.clicked.connect(lambda: on_click(hex_color))
        if removable_cb:
            self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.customContextMenuRequested.connect(lambda _: removable_cb(hex_color))
