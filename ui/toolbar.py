from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QToolButton, QMenu, QWidgetAction,
    QFrame, QLabel, QGraphicsDropShadowEffect, QSlider, QStyleOptionSlider, QStyle
)
from PySide6.QtGui import QColor, QKeySequence, QAction, QPainter, QPen
from PySide6.QtCore import Qt, QRectF, QPointF

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

class ColorSwapButton(QPushButton):
    def __init__(self, hex_color, on_click, accent_hex="#FFFFFF", removable_cb=None):
        super().__init__()
        self.hex_color = hex_color
        self.setObjectName("colorSwapButton")
        self.setFixedSize(24, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(f"{hex_color}  (right-click to remove)")
        self.setStyleSheet(f"""
            QPushButton#colorSwapButton {{
                background-color: {hex_color} !important;
                border: 2px solid rgba(0, 0, 0, 40) !important;
                border-radius: 12px !important;
            }}
            QPushButton#colorSwapButton:hover {{
                border: 2px solid {accent_hex} !important;
            }}
        """)
        self.clicked.connect(lambda: on_click(hex_color))
        if removable_cb:
            self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.customContextMenuRequested.connect(lambda _: removable_cb(hex_color))


class ThicknessSlider(QSlider):
    def __init__(self, orientation=Qt.Orientation.Vertical, parent=None):
        super().__init__(orientation, parent)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        opt = QStyleOptionSlider()
        self.initStyleOption(opt)

        handle_rect = self.style().subControlRect(
            QStyle.ComplexControl.CC_Slider, opt, QStyle.SubControl.SC_SliderHandle, self
        )

        gx = self.width() / 2.0
        track_w = 4.0
        margin = 10.0

        # Background track
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(100, 100, 100, 120))
        painter.drawRoundedRect(
            QRectF(gx - track_w / 2.0, margin, track_w, self.height() - 2.0 * margin), 2.0, 2.0
        )

        # Active lower track (filled in vibrant green)
        hy = handle_rect.center().y()
        bot_y = self.height() - margin
        if bot_y > hy:
            painter.setBrush(QColor("#20A756"))
            painter.drawRoundedRect(
                QRectF(gx - track_w / 2.0, hy, track_w, bot_y - hy), 2.0, 2.0
            )

        radius = 8.0
        center = QPointF(gx, hy)
        is_active = self.underMouse() or (opt.state & QStyle.StateFlag.State_Sunken)

        # Glowing ring light when hovered or dragged
        if is_active:
            painter.setPen(QPen(QColor(32, 167, 86, 120), 4.0))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center, radius + 2.5, radius + 2.5)

        # Perfectly antialiased circular thumb
        border_col = QColor("#20A756") if is_active else QColor(190, 190, 190)
        painter.setPen(QPen(border_col, 2.0))
        painter.setBrush(QColor("#ffffff"))
        painter.drawEllipse(center, radius, radius)
        painter.end()

