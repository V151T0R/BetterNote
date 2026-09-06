from PySide6.QtWidgets import QWidget, QScrollArea
from PySide6.QtGui import QPainter, QPainterPath, QPen, QColor, QMouseEvent, QTabletEvent, QPalette, QWheelEvent, QPixmap, QPageLayout
from PySide6.QtCore import Qt, QPointF, QEvent, QRectF, QSizeF
from PySide6.QtPrintSupport import QPrinter

from core.drawing_engine import DrawingEngine
from core.tools.pen import Pen
from core.tools.highlighter import Highlighter
from core.tools.eraser import Eraser
from core.tools.selection import Selection
from app.config import BASE_PAGE_WIDTH, BASE_PAGE_HEIGHT, MIN_ZOOM, MAX_ZOOM, ZOOM_STEP

PAGE_MARGIN = 40

class CanvasWidget(QWidget):
    def __init__(self, engine: DrawingEngine):
        super().__init__()
        self.engine = engine
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.page_paths = [self._rebuild_paths_for_page(p) for p in self.engine.notebook.pages]

        # Zoom / pan state
        self.zoom = 1.0
        self._panning = False
        self._pan_last_pos = None
        self.space_pan_mode = False

        self.dirty = False
        self._update_widget_size()

    # --- Page geometry / zoom ---
    def page_size(self):
        w = (BASE_PAGE_WIDTH + 2 * PAGE_MARGIN) * self.zoom
        h = (BASE_PAGE_HEIGHT + 2 * PAGE_MARGIN) * self.zoom
        return QSizeF(w, h)

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
        self.set_zoom(self.zoom * ZOOM_STEP, QPointF(self.width() / 2, self.height() / 2))

    def zoom_out(self):
        self.set_zoom(self.zoom / ZOOM_STEP, QPointF(self.width() / 2, self.height() / 2))

    def zoom_reset(self):
        self.set_zoom(1.0, QPointF(self.width() / 2, self.height() / 2))

    def _find_scroll_area(self):
        parent = self.parent()
        while parent is not None:
            if isinstance(parent, QScrollArea):
                return parent
            parent = parent.parent()
        return None

    def widget_to_page(self, pos: QPointF) -> QPointF:
        x = pos.x() / self.zoom - PAGE_MARGIN
        y = pos.y() / self.zoom - PAGE_MARGIN
        return QPointF(x, y)

    # --- Syncing paths ---
    def _rebuild_paths_for_page(self, page):
        paths = []
        for stroke in page.strokes:
            path = QPainterPath()
            pts = stroke.points
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

    def rebuild_all_paths(self):
        self.page_paths = [self._rebuild_paths_for_page(p) for p in self.engine.notebook.pages]
        self.update()
        
    def refresh_current_page(self):
        idx = self.engine.current_page_index
        self.page_paths[idx] = self._rebuild_paths_for_page(self.engine.current_page)
        self.dirty = True
        self.update()

    # --- Events ---
    def tabletEvent(self, e: QTabletEvent):
        pos = self.widget_to_page(e.position())
        pressure = e.pressure()
        is_touching = pressure > 0.0

        if e.type() == QEvent.Type.TabletPress and is_touching:
            self.engine.handle_press(pos.x(), pos.y(), pressure)
        elif e.type() == QEvent.Type.TabletMove:
            if is_touching:
                self.engine.handle_move(pos.x(), pos.y(), pressure)
            else:
                self.engine.handle_release(pos.x(), pos.y(), pressure)
                self.refresh_current_page()
        elif e.type() == QEvent.Type.TabletRelease:
            self.engine.handle_release(pos.x(), pos.y(), pressure)
            self.refresh_current_page()
            
        self.update()
        e.accept()

    def mousePressEvent(self, e: QMouseEvent):
        if e.source() != Qt.MouseEventSource.MouseEventNotSynthesized:
            return
        if e.button() == Qt.MouseButton.MiddleButton or (e.button() == Qt.MouseButton.LeftButton and self.space_pan_mode):
            self._panning = True
            self._pan_last_pos = e.globalPosition()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            return
        if e.button() == Qt.MouseButton.LeftButton:
            pos = self.widget_to_page(e.position())
            self.engine.handle_press(pos.x(), pos.y(), 1.0)
            self.update()

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
            pos = self.widget_to_page(e.position())
            self.engine.handle_move(pos.x(), pos.y(), 1.0)
            self.update()

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.source() != Qt.MouseEventSource.MouseEventNotSynthesized:
            return
        if self._panning and e.button() in (Qt.MouseButton.MiddleButton, Qt.MouseButton.LeftButton):
            self._panning = False
            self._pan_last_pos = None
            self.setCursor(Qt.CursorShape.OpenHandCursor if self.space_pan_mode else Qt.CursorShape.ArrowCursor)
            return
        if e.button() == Qt.MouseButton.LeftButton:
            pos = self.widget_to_page(e.position())
            self.engine.handle_release(pos.x(), pos.y(), 1.0)
            self.refresh_current_page()

    def wheelEvent(self, e: QWheelEvent):
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
    def render_page(self, painter: QPainter, page_index, target_rect: QRectF, scale=1.0, exclude_strokes=None):
        page = self.engine.notebook.pages[page_index]
        if exclude_strokes is None:
            exclude_strokes = []
        
        # Draw shadow
        shadow_rect = QRectF(target_rect.x() + 4*scale, target_rect.y() + 4*scale, target_rect.width(), target_rect.height())
        painter.fillRect(shadow_rect, QColor(0, 0, 0, 30))
        
        # Draw paper background
        bg = QColor(page.background) if page.background else QColor("#ffffff") # Force white as default paper color
        painter.fillRect(target_rect, bg)
        
        # Draw thin border
        painter.setPen(QPen(QColor(0, 0, 0, 40), 1))
        painter.drawRect(target_rect)

        # Draw strokes
        painter.save()
        painter.translate(target_rect.topLeft())
        painter.scale(scale, scale)
        # Apply a clip rect so strokes don't bleed off the paper bounds
        painter.setClipRect(0, 0, BASE_PAGE_WIDTH, BASE_PAGE_HEIGHT)
        
        for i, (stroke, path) in enumerate(zip(page.strokes, self.page_paths[page_index])):
            if i in exclude_strokes:
                continue
            pen = QPen(QColor(stroke.color))
            pen.setWidthF(stroke.width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            pen.setCosmetic(False)
            painter.setPen(pen)
            painter.drawPath(path)
        painter.restore()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # The rect representing the physical page
        page_rect = QRectF(PAGE_MARGIN * self.zoom, PAGE_MARGIN * self.zoom, BASE_PAGE_WIDTH * self.zoom, BASE_PAGE_HEIGHT * self.zoom)
        
        selected_indices = []
        if isinstance(self.engine.active_tool, Selection):
            selected_indices = self.engine.active_tool.selected_indices
            
        self.render_page(painter, self.engine.current_page_index, page_rect, scale=self.zoom, exclude_strokes=selected_indices)

        # Draw active stroke if any
        if isinstance(self.engine.active_tool, (Pen, Highlighter)):
            stroke = self.engine.active_tool.current_stroke
            if stroke and stroke.points:
                painter.save()
                painter.translate(page_rect.topLeft())
                painter.scale(self.zoom, self.zoom)
                painter.setClipRect(0, 0, BASE_PAGE_WIDTH, BASE_PAGE_HEIGHT)
                pen = QPen(QColor(stroke.color))
                pen.setWidthF(stroke.width)
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                painter.setPen(pen)
                
                path = QPainterPath()
                pts = stroke.points
                path.moveTo(pts[0]["x"], pts[0]["y"])
                for i in range(1, len(pts)):
                    if i >= 2:
                        p1 = QPointF(pts[i - 1]["x"], pts[i - 1]["y"])
                        p2 = QPointF(pts[i]["x"], pts[i]["y"])
                        path.quadTo(p1, (p1 + p2) / 2.0)
                    else:
                        path.lineTo(pts[i]["x"], pts[i]["y"])
                painter.drawPath(path)
                painter.restore()
                
        elif isinstance(self.engine.active_tool, Selection):
            tool = self.engine.active_tool
            # Draw selection rect if actively dragging to select
            if tool.state == "SELECTING":
                rx, ry, rw, rh = tool.selection_rect
                if rw > 0 and rh > 0:
                    screen_x = page_rect.topLeft().x() + rx * self.zoom
                    screen_y = page_rect.topLeft().y() + ry * self.zoom
                    sel_rect = QRectF(screen_x, screen_y, rw * self.zoom, rh * self.zoom)
                    
                    painter.save()
                    pen = QPen(QColor(0, 120, 215))
                    pen.setStyle(Qt.PenStyle.DashLine)
                    pen.setWidth(2)
                    painter.setPen(pen)
                    painter.fillRect(sel_rect, QColor(0, 120, 215, 30))
                    painter.drawRect(sel_rect)
                    painter.restore()
            
            # Draw the actual selected strokes with the drag offset
            if tool.state in ("SELECTED", "MOVING") and tool.selected_indices:
                dx = tool.drag_offset_x
                dy = tool.drag_offset_y
                
                painter.save()
                painter.translate(page_rect.topLeft())
                painter.scale(self.zoom, self.zoom)
                painter.setClipRect(0, 0, BASE_PAGE_WIDTH, BASE_PAGE_HEIGHT)
                
                page = self.engine.current_page
                for idx in tool.selected_indices:
                    if 0 <= idx < len(page.strokes):
                        stroke = page.strokes[idx]
                        path = self.page_paths[self.engine.current_page_index][idx]
                        
                        t_path = path.translated(dx, dy)
                        
                        pen = QPen(QColor(stroke.color))
                        pen.setWidthF(stroke.width)
                        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                        pen.setCosmetic(False)
                        painter.setPen(pen)
                        painter.drawPath(t_path)
                        
                # Draw a bounding box around selected strokes
                bbox = tool._get_strokes_bounding_box(page, tool.selected_indices)
                if bbox:
                    bx, by, bw, bh = bbox
                    bx += dx
                    by += dy
                    painter.setPen(QPen(QColor(100, 100, 100, 200), 1, Qt.PenStyle.DashLine))
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    pen = painter.pen()
                    pen.setWidthF(1.0 / self.zoom)
                    painter.setPen(pen)
                    
                    # Pad box a bit
                    pad = 4.0 / self.zoom
                    painter.drawRect(QRectF(bx - pad, by - pad, bw + pad*2, bh + pad*2))
                    
                painter.restore()
            
        painter.end()

    # --- Page ops ---
    def set_page_background(self, hex_color):
        self.engine.current_page.background = hex_color
        self.dirty = True
        self.update()

    def add_page(self):
        bg = self.engine.current_page.background
        self.engine.notebook.add_page(self.engine.current_page_index + 1, bg)
        self.page_paths.insert(self.engine.current_page_index + 1, [])
        self.engine.current_page_index += 1
        self.dirty = True
        self.update()

    def delete_current_page(self) -> bool:
        if self.engine.notebook.delete_page(self.engine.current_page_index):
            del self.page_paths[self.engine.current_page_index]
            self.engine.current_page_index = max(0, self.engine.current_page_index - 1)
            self.dirty = True
            self.update()
            return True
        return False

    def go_to_page(self, index):
        if 0 <= index < len(self.engine.notebook.pages):
            self.engine.current_page_index = index
            self.update()

    def clear_page(self):
        self.engine.current_page.strokes = []
        self.page_paths[self.engine.current_page_index] = []
        self.dirty = True
        self.update()

    # --- Export ---
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

        for i in range(len(self.engine.notebook.pages)):
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
            page_index = self.engine.current_page_index
        pixmap = QPixmap(BASE_PAGE_WIDTH, BASE_PAGE_HEIGHT)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.render_page(painter, page_index, QRectF(0, 0, BASE_PAGE_WIDTH, BASE_PAGE_HEIGHT), scale=1.0)
        painter.end()
        pixmap.save(filename)
