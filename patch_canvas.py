import sys

with open('ui/canvas_widget.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'from core.tools.eraser import Eraser',
    'from core.tools.eraser import Eraser\nfrom core.tools.selection import Selection'
)

old_render = '''    def render_page(self, painter: QPainter, page_index, target_rect: QRectF, scale=1.0):
        page = self.engine.notebook.pages[page_index]
        
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
        
        for stroke, path in zip(page.strokes, self.page_paths[page_index]):
            pen = QPen(QColor(stroke.color))
            pen.setWidthF(stroke.width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            pen.setCosmetic(False)
            painter.setPen(pen)
            painter.drawPath(path)
        painter.restore()'''

new_render = '''    def render_page(self, painter: QPainter, page_index, target_rect: QRectF, scale=1.0, exclude_strokes=None):
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
        painter.restore()'''

content = content.replace(old_render, new_render)


old_paint = '''    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # The rect representing the physical page
        page_rect = QRectF(PAGE_MARGIN * self.zoom, PAGE_MARGIN * self.zoom, BASE_PAGE_WIDTH * self.zoom, BASE_PAGE_HEIGHT * self.zoom)
        self.render_page(painter, self.engine.current_page_index, page_rect, scale=self.zoom)

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
            
        painter.end()'''

new_paint = '''    def paintEvent(self, event):
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
            
        painter.end()'''

content = content.replace(old_paint, new_paint)

with open('ui/canvas_widget.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Canvas widget updated!")
