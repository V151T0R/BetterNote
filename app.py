import sys
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QFileDialog, QColorDialog,
                               QLabel, QMessageBox, QFrame, QToolButton, QMenu,
                               QSizePolicy, QWidgetAction, QGraphicsDropShadowEffect,
                               QScrollArea)
from PySide6.QtGui import (QPainter, QPainterPath, QPen, QColor, QMouseEvent,
                           QTabletEvent, QPalette, QIcon, QPixmap, QAction,
                           QKeySequence, QPageLayout, QGuiApplication, QWheelEvent,
                           QTransform, QCursor)
from PySide6.QtCore import Qt, QPointF, QEvent, QRectF, QSizeF, QSize
from PySide6.QtPrintSupport import QPrinter


# A handful of default "pinned" colors shown as quick-access swatches
DEFAULT_PINNED_COLORS = ["#000000", "#e53935", "#1e88e5", "#43a047", "#fb8c00"]

# Base (unzoomed) canvas size — the page itself, in logical pixels
BASE_PAGE_WIDTH = 850
BASE_PAGE_HEIGHT = 1100

MIN_ZOOM = 0.25
MAX_ZOOM = 4.0
ZOOM_STEP = 1.15


class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # --- Multi-page document model ---
        self.pages = [self._new_page()]
        self.page_paths = [[]]
        self.current_page_index = 0

        # State variables for active drawing
        self.current_stroke_data = None
        self.current_path = QPainterPath()
        self.is_drawing = False

        self.active_color = None
        self.active_width = 3.0

        # Eraser
        self.eraser_mode = False
        self.eraser_radius = 12.0
        self.is_erasing = False

        # --- Zoom / pan state ---
        self.zoom = 1.0
        self._panning = False
        self._pan_last_pos = None
        self.space_pan_mode = False  # held-space temporary pan tool

        self.dirty = False
        self._update_widget_size()

    # --- Page geometry / zoom ---

    def page_size(self):
        return QSizeF(BASE_PAGE_WIDTH * self.zoom, BASE_PAGE_HEIGHT * self.zoom)

    def _update_widget_size(self):
        size = self.page_size()
        self.setFixedSize(int(size.width()), int(size.height()))

    def set_zoom(self, new_zoom, anchor_widget_pos=None):
        new_zoom = max(MIN_ZOOM, min(MAX_ZOOM, new_zoom))
        if abs(new_zoom - self.zoom) < 1e-4:
            return
        old_zoom = self.zoom
        self.zoom = new_zoom
        self._update_widget_size()

        # Keep the point under the cursor stationary by adjusting the
        # scroll area's viewport position after resizing, if we're inside one.
        scroll_area = self._find_scroll_area()
        if scroll_area and anchor_widget_pos is not None:
            ratio = new_zoom / old_zoom
            hbar = scroll_area.horizontalScrollBar()
            vbar = scroll_area.verticalScrollBar()
            new_x = anchor_widget_pos.x() * ratio - (anchor_widget_pos.x() - hbar.value())
            new_y = anchor_widget_pos.y() * ratio - (anchor_widget_pos.y() - vbar.value())
            hbar.setValue(int(new_x))
            vbar.setValue(int(new_y))

        self.update()

    def zoom_in(self):
        center = QPointF(self.width() / 2, self.height() / 2)
        self.set_zoom(self.zoom * ZOOM_STEP, center)

    def zoom_out(self):
        center = QPointF(self.width() / 2, self.height() / 2)
        self.set_zoom(self.zoom / ZOOM_STEP, center)

    def zoom_reset(self):
        center = QPointF(self.width() / 2, self.height() / 2)
        self.set_zoom(1.0, center)

    def _find_scroll_area(self):
        parent = self.parent()
        while parent is not None:
            if isinstance(parent, QScrollArea):
                return parent
            parent = parent.parent()
        return None

    def widget_to_page(self, pos: QPointF) -> QPointF:
        """Convert a widget-space coordinate (post-zoom) into page-space
        (unzoomed) coordinates, so strokes remain resolution-independent."""
        return QPointF(pos.x() / self.zoom, pos.y() / self.zoom)

    def page_to_widget(self, pos: QPointF) -> QPointF:
        return QPointF(pos.x() * self.zoom, pos.y() * self.zoom)

    # --- Page model helpers ---

    def _new_page(self, background=None):
        return {"strokes": [], "background": background}

    def _rebuild_paths_for_page(self, page):
        """Rebuild QPainterPaths (in page-space) from a page's raw coordinate data."""
        paths = []
        for stroke in page["strokes"]:
            path = QPainterPath()
            pts = stroke["points"]
            if not pts:
                continue
            path.moveTo(pts[0]["x"], pts[0]["y"])
            for i in range(1, len(pts)):
                if i >= 2:
                    p1 = QPointF(pts[i - 1]["x"], pts[i - 1]["y"])
                    p2 = QPointF(pts[i]["x"], pts[i]["y"])
                    path.quadTo(p1, (p1 + p2) / 2.0)
                else:
                    path.lineTo(pts[i]["x"], pts[i]["y"])
            paths.append(path)
        return paths

    @property
    def strokes(self):
        return self.pages[self.current_page_index]["strokes"]

    def current_background_color(self):
        bg = self.pages[self.current_page_index]["background"]
        if bg:
            return QColor(bg)
        return self.palette().color(QPalette.ColorRole.Base)

    def set_page_background(self, hex_color):
        self.pages[self.current_page_index]["background"] = hex_color
        self.dirty = True
        self.update()

    def add_page(self):
        current_bg = self.pages[self.current_page_index]["background"]
        self.pages.insert(self.current_page_index + 1, self._new_page(current_bg))
        self.page_paths.insert(self.current_page_index + 1, [])
        self.current_page_index += 1
        self.dirty = True
        self._reset_active_stroke()
        self.update()

    def delete_current_page(self):
        if len(self.pages) <= 1:
            return False
        del self.pages[self.current_page_index]
        del self.page_paths[self.current_page_index]
        self.current_page_index = max(0, self.current_page_index - 1)
        self.dirty = True
        self._reset_active_stroke()
        self.update()
        return True

    def go_to_page(self, index):
        if 0 <= index < len(self.pages):
            self.current_page_index = index
            self._reset_active_stroke()
            self.update()

    def next_page(self):
        self.go_to_page(self.current_page_index + 1)

    def prev_page(self):
        self.go_to_page(self.current_page_index - 1)

    def _reset_active_stroke(self):
        self.is_drawing = False
        self.is_erasing = False
        self.current_stroke_data = None
        self.current_path = QPainterPath()

    # --- Drawing (all stroke data stored in page-space, not widget-space) ---

    def get_current_color(self):
        if self.active_color:
            return self.active_color
        return self.palette().color(QPalette.ColorRole.Text).name()

    def start_stroke(self, widget_pos):
        pos = self.widget_to_page(widget_pos)
        self.is_drawing = True
        self.current_stroke_data = {
            "color": self.get_current_color(),
            "width": self.active_width,
            "points": []
        }
        self.current_path = QPainterPath()
        self.current_path.moveTo(pos)
        self.add_point(widget_pos, 1.0)

    def add_point(self, widget_pos, pressure):
        if not self.is_drawing:
            return
        pos = self.widget_to_page(widget_pos)

        pts = self.current_stroke_data["points"]
        pts.append({"x": pos.x(), "y": pos.y(), "p": pressure})

        if len(pts) > 2:
            p1 = QPointF(pts[-2]["x"], pts[-2]["y"])
            p2 = QPointF(pts[-1]["x"], pts[-1]["y"])
            midpoint = (p1 + p2) / 2.0
            self.current_path.quadTo(p1, midpoint)
        elif len(pts) == 2:
            self.current_path.lineTo(pos)

        self.update()

    def end_stroke(self):
        if self.is_drawing and self.current_stroke_data and self.current_stroke_data["points"]:
            self.pages[self.current_page_index]["strokes"].append(self.current_stroke_data)
            self.page_paths[self.current_page_index].append(self.current_path)
            self.dirty = True
        self.is_drawing = False
        self.current_stroke_data = None
        self.current_path = QPainterPath()
        self.update()

    # --- Eraser ---

    def erase_at(self, widget_pos):
        pos = self.widget_to_page(widget_pos)
        r = self.eraser_radius
        rect = QRectF(pos.x() - r, pos.y() - r, r * 2, r * 2)
        strokes = self.pages[self.current_page_index]["strokes"]
        paths = self.page_paths[self.current_page_index]

        to_remove = [i for i, path in enumerate(paths) if path.intersects(rect)]
        if to_remove:
            for i in reversed(to_remove):
                del strokes[i]
                del paths[i]
            self.dirty = True
            self.update()

    # --- Hardware Event Handlers ---

    def tabletEvent(self, e: QTabletEvent):
        pos = e.position()
        pressure = e.pressure()
        is_touching = pressure > 0.0

        if self.eraser_mode:
            if e.type() == QEvent.Type.TabletPress and is_touching:
                self.is_erasing = True
                self.erase_at(pos)
            elif e.type() == QEvent.Type.TabletMove:
                if is_touching and self.is_erasing:
                    self.erase_at(pos)
            elif e.type() == QEvent.Type.TabletRelease:
                self.is_erasing = False
            e.accept()
            return

        if e.type() == QEvent.Type.TabletPress and is_touching:
            self.start_stroke(pos)
        elif e.type() == QEvent.Type.TabletMove:
            if is_touching:
                if not self.is_drawing:
                    self.start_stroke(pos)
                else:
                    self.add_point(pos, pressure)
            else:
                if self.is_drawing:
                    self.end_stroke()
        elif e.type() == QEvent.Type.TabletRelease:
            if self.is_drawing:
                self.end_stroke()

        e.accept()

    def mousePressEvent(self, e: QMouseEvent):
        if e.source() != Qt.MouseEventSource.MouseEventNotSynthesized:
            return
        if e.button() == Qt.MouseButton.MiddleButton or (
            e.button() == Qt.MouseButton.LeftButton and self.space_pan_mode
        ):
            self._panning = True
            self._pan_last_pos = e.globalPosition()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            return
        if e.button() == Qt.MouseButton.LeftButton:
            if self.eraser_mode:
                self.is_erasing = True
                self.erase_at(e.position())
            else:
                self.start_stroke(e.position())

    def mouseMoveEvent(self, e: QMouseEvent):
        if e.source() != Qt.MouseEventSource.MouseEventNotSynthesized:
            return
        if self._panning and self._pan_last_pos is not None:
            delta = e.globalPosition() - self._pan_last_pos
            self._pan_last_pos = e.globalPosition()
            scroll_area = self._find_scroll_area()
            if scroll_area:
                hbar = scroll_area.horizontalScrollBar()
                vbar = scroll_area.verticalScrollBar()
                hbar.setValue(int(hbar.value() - delta.x()))
                vbar.setValue(int(vbar.value() - delta.y()))
            return
        if e.buttons() & Qt.MouseButton.LeftButton:
            if self.eraser_mode:
                if self.is_erasing:
                    self.erase_at(e.position())
            else:
                self.add_point(e.position(), 1.0)

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.source() != Qt.MouseEventSource.MouseEventNotSynthesized:
            return
        if self._panning and e.button() in (Qt.MouseButton.MiddleButton, Qt.MouseButton.LeftButton):
            self._panning = False
            self._pan_last_pos = None
            self.setCursor(Qt.CursorShape.OpenHandCursor if self.space_pan_mode else Qt.CursorShape.ArrowCursor)
            return
        if e.button() == Qt.MouseButton.LeftButton:
            if self.eraser_mode:
                self.is_erasing = False
            else:
                self.end_stroke()

    def wheelEvent(self, e: QWheelEvent):
        # Ctrl+scroll (or pinch-zoom, which Qt reports as Ctrl+wheel on
        # trackpads) zooms centered on the cursor; plain scroll passes
        # through to the enclosing QScrollArea for panning.
        if e.modifiers() & Qt.KeyboardModifier.ControlModifier:
            anchor = e.position()
            factor = ZOOM_STEP if e.angleDelta().y() > 0 else 1.0 / ZOOM_STEP
            self.set_zoom(self.zoom * factor, anchor)
            e.accept()
        else:
            e.ignore()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Space and not e.isAutoRepeat():
            self.space_pan_mode = True
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().keyPressEvent(e)

    def keyReleaseEvent(self, e):
        if e.key() == Qt.Key.Key_Space and not e.isAutoRepeat():
            self.space_pan_mode = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().keyReleaseEvent(e)

    # --- Rendering ---

    def render_page(self, painter: QPainter, page_index, target_rect: QRectF, scale=1.0):
        """Render a specific page's strokes (which are stored in page-space)
        into an arbitrary painter/rect at the given scale."""
        page = self.pages[page_index]
        bg = QColor(page["background"]) if page["background"] else self.palette().color(QPalette.ColorRole.Base)
        painter.fillRect(target_rect, bg)

        painter.save()
        painter.translate(target_rect.topLeft())
        painter.scale(scale, scale)
        for stroke_data, path in zip(page["strokes"], self.page_paths[page_index]):
            pen = QPen(QColor(stroke_data["color"]))
            pen.setWidthF(stroke_data["width"])
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            pen.setCosmetic(False)
            painter.setPen(pen)
            painter.drawPath(path)
        painter.restore()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.render_page(painter, self.current_page_index, QRectF(self.rect()), scale=self.zoom)

        if self.is_drawing:
            painter.save()
            painter.scale(self.zoom, self.zoom)
            pen = QPen(QColor(self.get_current_color()))
            pen.setWidthF(self.active_width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawPath(self.current_path)
            painter.restore()

        painter.end()

    # --- Data Operations ---

    def to_document(self):
        return {"pages": self.pages}

    def load_document(self, data):
        if isinstance(data, list):
            pages = [{"strokes": data, "background": None}]
        else:
            pages = data.get("pages", [{"strokes": [], "background": None}])

        self.pages = pages
        self.page_paths = [self._rebuild_paths_for_page(p) for p in pages]
        self.current_page_index = 0
        self._reset_active_stroke()
        self.dirty = False
        self.update()

    def clear(self):
        self.pages[self.current_page_index]["strokes"] = []
        self.page_paths[self.current_page_index] = []
        self.dirty = True
        self.update()

    def export_pdf(self, filename):
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(filename)

        if BASE_PAGE_WIDTH >= BASE_PAGE_HEIGHT:
            printer.setPageOrientation(QPageLayout.Orientation.Landscape)
        else:
            printer.setPageOrientation(QPageLayout.Orientation.Portrait)

        painter = QPainter()
        painter.begin(printer)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        canvas_w = BASE_PAGE_WIDTH
        canvas_h = BASE_PAGE_HEIGHT

        for i in range(len(self.pages)):
            if i > 0:
                printer.newPage()

            page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
            scale = min(page_rect.width() / canvas_w, page_rect.height() / canvas_h)
            offset_x = (page_rect.width() - canvas_w * scale) / 2.0
            offset_y = (page_rect.height() - canvas_h * scale) / 2.0

            target = QRectF(offset_x, offset_y, canvas_w * scale, canvas_h * scale)
            self.render_page(painter, i, target, scale=scale)

        painter.end()

    def export_image(self, filename, page_index=None):
        if page_index is None:
            page_index = self.current_page_index
        pixmap = QPixmap(BASE_PAGE_WIDTH, BASE_PAGE_HEIGHT)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.render_page(painter, page_index, QRectF(0, 0, BASE_PAGE_WIDTH, BASE_PAGE_HEIGHT), scale=1.0)
        painter.end()
        pixmap.save(filename)


class ColorSwatchButton(QPushButton):
    """Small round button that shows a solid color and applies it on click."""
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


def _rgba(color: QColor, alpha=None):
    a = color.alpha() if alpha is None else alpha
    return f"rgba({color.red()}, {color.green()}, {color.blue()}, {a})"


def build_theme_stylesheet(palette: QPalette, base_point_size: float) -> str:
    """Builds the app's QSS purely from the active QPalette, so switching
    the OS between light/dark mode (or changing the system accent color)
    re-themes the whole UI with no hardcoded colors left behind."""

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
    icon_pt = pt + 3

    return f"""
QMainWindow {{
    background-color: {window.name()};
}}

QScrollArea {{
    border: none;
    background: {window.name()};
}}
QScrollArea > QWidget > QWidget {{
    background: {window.name()};
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

QPushButton#iconButton, QToolButton#iconButton {{
    font-size: {icon_pt}pt;
    padding: 0px;
    border-radius: 18px;
}}

QPushButton#navButton, QToolButton#navButton {{
    font-size: {icon_pt}pt;
    padding: 0px;
    border-radius: 15px;
}}

QPushButton#zoomButton {{
    font-size: {icon_pt}pt;
    padding: 0px;
    border-radius: 14px;
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

QFrame#toolbarDivider {{
    color: {border.name()};
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GoodNote")
        self.resize(1100, 800)
        # Allow free resizing of the window (no fixed/minimum size trap)
        self.setMinimumSize(480, 360)

        self.canvas = Canvas()
        self.pinned_colors = list(DEFAULT_PINNED_COLORS)
        self.current_file = None

        # Wrap the canvas in a scroll area so it can be panned/scrolled
        # when zoomed in, and so the window itself is freely resizable
        # without warping the page.
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidget(self.canvas)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.setCentralWidget(self.scroll_area)

        self.apply_theme()

        self._build_file_menu_actions()
        self._build_colors_menu()
        self._build_pages_menu()
        self._build_floating_toolbar()
        self._build_zoom_bar()
        self._build_shortcuts()

        self.update_page_label()
        self.update_zoom_label()
        self.position_overlays()

    # --- Floating toolbar ---

    def _build_floating_toolbar(self):
        self.toolbar = QWidget(self.scroll_area.viewport())
        self.toolbar.setObjectName("floatingToolbar")
        self.toolbar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        shadow = QGraphicsDropShadowEffect(self.toolbar)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 70))
        self.toolbar.setGraphicsEffect(shadow)

        row = QHBoxLayout(self.toolbar)
        row.setContentsMargins(10, 6, 10, 6)
        row.setSpacing(6)

        self.file_menu_button = QToolButton()
        self.file_menu_button.setObjectName("fileMenuButton")
        self.file_menu_button.setText("File")
        self.file_menu_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.file_menu_button.setMenu(self._file_menu)

        # Sleeker glyphs: filled pen nib, dedicated eraser block, filled
        # palette dot, and thin chevrons instead of the previous mixed set.
        self.btn_pen = QPushButton("🖊")
        self.btn_pen.setToolTip("Pen (P)")
        self.btn_pen.setCheckable(True)
        self.btn_pen.setChecked(True)
        self.btn_pen.clicked.connect(self.activate_pen)

        self.btn_eraser = QPushButton("⬜")
        self.btn_eraser.setToolTip("Eraser (E)")
        self.btn_eraser.setCheckable(True)
        self.btn_eraser.clicked.connect(self.activate_eraser)

        self.colors_button = QToolButton()
        self.colors_button.setObjectName("iconButton")
        self.colors_button.setText("●")
        self.colors_button.setToolTip("Colors")
        self.colors_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.colors_button.setMenu(self._colors_menu)
        self._recolor_colors_button()

        for b in (self.btn_pen, self.btn_eraser):
            b.setObjectName("iconButton")
            b.setFixedSize(36, 36)
        self.colors_button.setFixedSize(36, 36)

        btn_prev = QPushButton("◂")
        btn_prev.setObjectName("navButton")
        btn_prev.setFixedSize(30, 36)
        btn_prev.setToolTip("Previous page")
        btn_prev.clicked.connect(self.prev_page)

        self.page_label = QLabel()
        self.page_label.setObjectName("pageLabel")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_label.setMinimumWidth(56)

        btn_next = QPushButton("▸")
        btn_next.setObjectName("navButton")
        btn_next.setFixedSize(30, 36)
        btn_next.setToolTip("Next page")
        btn_next.clicked.connect(self.next_page)

        self.btn_add_page = QPushButton("+")
        self.btn_add_page.setObjectName("iconButton")
        self.btn_add_page.setToolTip("Add page")
        self.btn_add_page.setFixedSize(36, 36)
        self.btn_add_page.clicked.connect(self.add_page)

        self.pages_button = QToolButton()
        self.pages_button.setObjectName("iconButton")
        self.pages_button.setText("⋯")
        self.pages_button.setToolTip("More page options")
        self.pages_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.pages_button.setMenu(self._pages_menu)
        self.pages_button.setFixedSize(36, 36)

        row.addWidget(self.file_menu_button)
        row.addWidget(self._vline())
        row.addWidget(self.btn_pen)
        row.addWidget(self.btn_eraser)
        row.addWidget(self.colors_button)
        row.addWidget(self._vline())
        row.addWidget(btn_prev)
        row.addWidget(self.page_label)
        row.addWidget(btn_next)
        row.addWidget(self.btn_add_page)
        row.addWidget(self.pages_button)

        self.toolbar.adjustSize()

    def _build_zoom_bar(self):
        """Separate small pill, bottom-right, for zoom controls — kept apart
        from the main toolbar so it doesn't get crowded."""
        self.zoom_bar = QWidget(self.scroll_area.viewport())
        self.zoom_bar.setObjectName("zoomBar")
        self.zoom_bar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        shadow = QGraphicsDropShadowEffect(self.zoom_bar)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.zoom_bar.setGraphicsEffect(shadow)

        row = QHBoxLayout(self.zoom_bar)
        row.setContentsMargins(8, 5, 8, 5)
        row.setSpacing(4)

        btn_out = QPushButton("−")
        btn_out.setObjectName("zoomButton")
        btn_out.setFixedSize(28, 28)
        btn_out.setToolTip("Zoom out (Ctrl+−)")
        btn_out.clicked.connect(self.canvas.zoom_out)
        btn_out.clicked.connect(self.update_zoom_label)

        self.zoom_label = QLabel()
        self.zoom_label.setObjectName("zoomLabel")
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zoom_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.zoom_label.mousePressEvent = lambda e: self._reset_zoom_clicked()

        btn_in = QPushButton("+")
        btn_in.setObjectName("zoomButton")
        btn_in.setFixedSize(28, 28)
        btn_in.setToolTip("Zoom in (Ctrl++)")
        btn_in.clicked.connect(self.canvas.zoom_in)
        btn_in.clicked.connect(self.update_zoom_label)

        row.addWidget(btn_out)
        row.addWidget(self.zoom_label)
        row.addWidget(btn_in)

        self.zoom_bar.adjustSize()

    def _reset_zoom_clicked(self):
        self.canvas.zoom_reset()
        self.update_zoom_label()

    def update_zoom_label(self):
        self.zoom_label.setText(f"{round(self.canvas.zoom * 100)}%")

    def _build_shortcuts(self):
        act_zoom_in = QAction(self)
        act_zoom_in.setShortcuts([QKeySequence.StandardKey.ZoomIn, QKeySequence("Ctrl+=")])
        act_zoom_in.triggered.connect(lambda: (self.canvas.zoom_in(), self.update_zoom_label()))
        self.addAction(act_zoom_in)

        act_zoom_out = QAction(self)
        act_zoom_out.setShortcuts([QKeySequence.StandardKey.ZoomOut])
        act_zoom_out.triggered.connect(lambda: (self.canvas.zoom_out(), self.update_zoom_label()))
        self.addAction(act_zoom_out)

        act_zoom_reset = QAction(self)
        act_zoom_reset.setShortcut(QKeySequence("Ctrl+0"))
        act_zoom_reset.triggered.connect(self._reset_zoom_clicked)
        self.addAction(act_zoom_reset)

        act_pen = QAction(self)
        act_pen.setShortcut(QKeySequence("P"))
        act_pen.triggered.connect(self.activate_pen)
        self.addAction(act_pen)

        act_eraser = QAction(self)
        act_eraser.setShortcut(QKeySequence("E"))
        act_eraser.triggered.connect(self.activate_eraser)
        self.addAction(act_eraser)

    def position_overlays(self):
        """Keeps the floating toolbar centered near the top, and the zoom
        bar pinned to the bottom-right, of the scroll area's viewport —
        regardless of window size or scroll position."""
        viewport = self.scroll_area.viewport()
        self.toolbar.adjustSize()
        x = max(8, (viewport.width() - self.toolbar.width()) // 2)
        self.toolbar.move(x, 10)
        self.toolbar.raise_()

        self.zoom_bar.adjustSize()
        zx = max(8, viewport.width() - self.zoom_bar.width() - 14)
        zy = max(8, viewport.height() - self.zoom_bar.height() - 14)
        self.zoom_bar.move(zx, zy)
        self.zoom_bar.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.position_overlays()

    def showEvent(self, event):
        super().showEvent(event)
        self.position_overlays()

    # --- Theming: follow the OS light/dark mode, accent color, and font ---

    def apply_theme(self):
        # Guard against re-entrancy: on some platforms, setStyleSheet()
        # itself triggers another PaletteChange event, which would otherwise
        # recurse until Qt/Python's stack gives out.
        if getattr(self, "_applying_theme", False):
            return
        self._applying_theme = True
        try:
            base_pt = QApplication.font().pointSizeF()
            if base_pt <= 0:
                base_pt = 10.0
            self.setStyleSheet(build_theme_stylesheet(self.palette(), base_pt))
            if hasattr(self, "swatch_layout"):
                self.refresh_pinned_swatches()
            if hasattr(self, "colors_button"):
                self._recolor_colors_button()
        finally:
            self._applying_theme = False

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (
            QEvent.Type.PaletteChange,
            QEvent.Type.ApplicationPaletteChange,
            QEvent.Type.FontChange,
        ):
            self.apply_theme()
            self.canvas.update()

    def _vline(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Plain)
        line.setObjectName("toolbarDivider")
        return line

    def _style_popup_menu(self, menu):
        return menu

    def _recolor_colors_button(self):
        """Tints the palette-button glyph to match the currently active
        drawing color, so the icon itself previews the selection."""
        color = self.canvas.get_current_color() if hasattr(self, "canvas") else "#000000"
        self.colors_button.setStyleSheet(f"QToolButton#iconButton {{ color: {color}; }}")

    def _build_file_menu_actions(self):
        menu = self._style_popup_menu(QMenu(self))

        act_open = QAction("Open…", self)
        act_open.setShortcut(QKeySequence.StandardKey.Open)
        act_open.triggered.connect(self.load_file)
        menu.addAction(act_open)

        act_save = QAction("Save", self)
        act_save.setShortcut(QKeySequence.StandardKey.Save)
        act_save.triggered.connect(self.save_file)
        menu.addAction(act_save)

        act_save_as = QAction("Save As…", self)
        act_save_as.setShortcut(QKeySequence.StandardKey.SaveAs)
        act_save_as.triggered.connect(self.save_file_as)
        menu.addAction(act_save_as)

        menu.addSeparator()

        act_export_pdf = QAction("Export as PDF…", self)
        act_export_pdf.triggered.connect(self.export_pdf)
        menu.addAction(act_export_pdf)

        act_export_image = QAction("Export as Image…", self)
        act_export_image.triggered.connect(self.export_image)
        menu.addAction(act_export_image)

        menu.addSeparator()

        act_background = QAction("Page Background…", self)
        act_background.triggered.connect(self.choose_background)
        menu.addAction(act_background)

        self._file_menu = menu
        self.addActions(menu.actions())

    def _build_colors_menu(self):
        """A compact dropdown holding the pinned-color swatches (wrapped
        across multiple rows so any number can be pinned) plus
        'Custom Color…' and 'Pin Current Color'."""
        menu = self._style_popup_menu(QMenu(self))

        swatch_widget = QWidget()
        self.swatch_layout = _WrapLayout(swatch_widget, h_spacing=6, v_spacing=6)
        swatch_widget.setMinimumWidth(190)

        swatch_action = QWidgetAction(menu)
        swatch_action.setDefaultWidget(swatch_widget)
        menu.addAction(swatch_action)
        menu.addSeparator()

        act_custom = QAction("Custom Color…", self)
        act_custom.triggered.connect(self.choose_color)
        menu.addAction(act_custom)

        act_pin = QAction("Pin Current Color", self)
        act_pin.triggered.connect(self.pin_current_color)
        menu.addAction(act_pin)

        self._colors_menu = menu
        self.refresh_pinned_swatches()

    def _build_pages_menu(self):
        menu = self._style_popup_menu(QMenu(self))

        act_delete = QAction("Delete Page", self)
        act_delete.triggered.connect(self.delete_page)
        menu.addAction(act_delete)

        menu.addSeparator()

        act_clear = QAction("Clear Page", self)
        act_clear.triggered.connect(self.clear_page)
        menu.addAction(act_clear)

        self._pages_menu = menu

    # --- Tool switching ---

    def activate_pen(self):
        self.canvas.eraser_mode = False
        self.btn_pen.setChecked(True)
        self.btn_eraser.setChecked(False)

    def activate_eraser(self):
        self.canvas.eraser_mode = True
        self.btn_pen.setChecked(False)
        self.btn_eraser.setChecked(True)

    # --- Color handling ---

    def apply_color(self, hex_color):
        self.canvas.active_color = hex_color
        self._recolor_colors_button()
        self.activate_pen()

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.apply_color(color.name())

    def pin_current_color(self):
        color = self.canvas.get_current_color()
        if color not in self.pinned_colors:
            # No cap: any number of colors can be pinned; the swatch panel
            # wraps onto additional rows as needed.
            self.pinned_colors.append(color)
            self.refresh_pinned_swatches()

    def unpin_color(self, hex_color):
        if hex_color in self.pinned_colors and len(self.pinned_colors) > 1:
            self.pinned_colors.remove(hex_color)
            self.refresh_pinned_swatches()

    def refresh_pinned_swatches(self):
        self.swatch_layout.clear()
        for hex_color in self.pinned_colors:
            swatch = ColorSwatchButton(hex_color, self.apply_color, removable_cb=self.unpin_color)
            self.swatch_layout.addWidget(swatch)

    # --- Background ---

    def choose_background(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.set_page_background(color.name())

    def clear_page(self):
        self.canvas.clear()

    # --- Pages ---

    def update_page_label(self):
        total = len(self.canvas.pages)
        current = self.canvas.current_page_index + 1
        self.page_label.setText(f"{current} / {total}")

    def add_page(self):
        self.canvas.add_page()
        self.update_page_label()

    def delete_page(self):
        if len(self.canvas.pages) <= 1:
            QMessageBox.information(self, "Can't Delete", "A document needs at least one page.")
            return
        reply = QMessageBox.question(
            self, "Delete Page",
            "Delete the current page? This can't be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.canvas.delete_current_page()
            self.update_page_label()

    def prev_page(self):
        self.canvas.prev_page()
        self.update_page_label()

    def next_page(self):
        self.canvas.next_page()
        self.update_page_label()

    # --- File I/O ---

    def save_file(self):
        if self.current_file:
            self._write_json(self.current_file)
        else:
            self.save_file_as()

    def save_file_as(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Notes", "", "JSON Files (*.json)")
        if filename:
            self._write_json(filename)

    def _write_json(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.canvas.to_document(), f)
        self.current_file = filename
        self.canvas.dirty = False
        print(f"Saved {len(self.canvas.pages)} page(s) to {filename}")

    def load_file(self):
        if not self.confirm_discard_if_dirty():
            return
        filename, _ = QFileDialog.getOpenFileName(self, "Load Notes", "", "JSON Files (*.json)")
        if filename:
            with open(filename, 'r') as f:
                data = json.load(f)
            self.canvas.load_document(data)
            self.current_file = filename
            self.update_page_label()
            print(f"Loaded {len(self.canvas.pages)} page(s) from {filename}")

    def export_pdf(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export as PDF", "", "PDF Files (*.pdf)")
        if filename:
            self.canvas.export_pdf(filename)
            print(f"Exported {len(self.canvas.pages)} page(s) to {filename}")

    def export_image(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Current Page as Image", "", "PNG Files (*.png);;JPEG Files (*.jpg)"
        )
        if filename:
            self.canvas.export_image(filename)
            print(f"Exported current page to {filename}")

    # --- Unsaved-changes handling ---

    def confirm_discard_if_dirty(self):
        if not self.canvas.dirty:
            return True
        reply = QMessageBox.question(
            self, "Unsaved Changes",
            "You have unsaved changes. Do you want to save them first?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )
        if reply == QMessageBox.StandardButton.Save:
            self.save_file()
            return not self.canvas.dirty
        elif reply == QMessageBox.StandardButton.Discard:
            return True
        else:
            return False

    def closeEvent(self, event):
        if self.confirm_discard_if_dirty():
            event.accept()
        else:
            event.ignore()


class _WrapLayout(QWidget):
    """Minimal flow layout wrapper: lays child widgets left-to-right, wrapping
    to a new row when the current row runs out of width. Used for the pinned
    color swatches so an unlimited number of them can be pinned without the
    menu growing unusably wide."""

    def __init__(self, parent_widget, h_spacing=6, v_spacing=6, cols=8):
        self._container = parent_widget
        self._h_spacing = h_spacing
        self._v_spacing = v_spacing
        self._cols = cols
        self._grid = None
        super().__init__()
        from PySide6.QtWidgets import QGridLayout
        self._layout = QGridLayout(parent_widget)
        self._layout.setContentsMargins(10, 8, 10, 8)
        self._layout.setHorizontalSpacing(h_spacing)
        self._layout.setVerticalSpacing(v_spacing)
        self._widgets = []

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())