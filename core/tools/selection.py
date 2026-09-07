from typing import Optional, List, Dict
from core.tools.tool import Tool
from core.page import Page
from core.commands.command import Command
from core.commands.move_stroke import MoveStrokeCommand

class Selection(Tool):
    def __init__(self):
        self.state = "IDLE" # IDLE, SELECTING, SELECTED, MOVING
        self.start_x = 0.0
        self.start_y = 0.0
        self.end_x = 0.0
        self.end_y = 0.0
        
        self.selected_indices: List[int] = []
        self.drag_offset_x = 0.0
        self.drag_offset_y = 0.0
        
        self.last_x = 0.0
        self.last_y = 0.0

    @property
    def selection_rect(self) -> tuple[float, float, float, float]:
        """Returns (x, y, width, height) of the current selection bounds."""
        min_x = min(self.start_x, self.end_x)
        min_y = min(self.start_y, self.end_y)
        w = abs(self.end_x - self.start_x)
        h = abs(self.end_y - self.start_y)
        return (min_x, min_y, w, h)

    def _get_strokes_bounding_box(self, page: Page, indices: List[int]) -> Optional[tuple[float, float, float, float]]:
        if not indices:
            return None
        min_x, min_y = float('inf'), float('inf')
        max_x, max_y = float('-inf'), float('-inf')
        for idx in indices:
            if 0 <= idx < len(page.strokes):
                for pt in page.strokes[idx].points:
                    min_x = min(min_x, pt["x"])
                    min_y = min(min_y, pt["y"])
                    max_x = max(max_x, pt["x"])
                    max_y = max(max_y, pt["y"])
        if min_x == float('inf'):
            return None
        return (min_x, min_y, max_x - min_x, max_y - min_y)

    def _is_point_in_rect(self, px: float, py: float, rect: tuple[float, float, float, float]) -> bool:
        x, y, w, h = rect
        return x <= px <= x + w and y <= py <= y + h

    def on_press(self, x: float, y: float, pressure: float, page: Page) -> None:
        self.last_x = x
        self.last_y = y
        
        if self.state == "SELECTED":
            # Check if clicked inside the bounding box of selected strokes
            bbox = self._get_strokes_bounding_box(page, self.selected_indices)
            if bbox and self._is_point_in_rect(x, y, bbox):
                self.state = "MOVING"
                self.drag_offset_x = 0.0
                self.drag_offset_y = 0.0
                return
            else:
                # Clicked outside, clear selection and start new selection
                self.selected_indices = []
                self.state = "SELECTING"
                self.start_x = x
                self.start_y = y
                self.end_x = x
                self.end_y = y
                return
                
        # If IDLE or somehow otherwise, start selecting
        self.state = "SELECTING"
        self.selected_indices = []
        self.start_x = x
        self.start_y = y
        self.end_x = x
        self.end_y = y

    def on_move(self, x: float, y: float, pressure: float, page: Page) -> None:
        if self.state == "SELECTING":
            self.end_x = x
            self.end_y = y
        elif self.state == "MOVING":
            self.drag_offset_x += (x - self.last_x)
            self.drag_offset_y += (y - self.last_y)
            self.last_x = x
            self.last_y = y

    def on_release(self, x: float, y: float, pressure: float, page: Page) -> Optional[Command]:
        if self.state == "SELECTING":
            self.end_x = x
            self.end_y = y
            rect = self.selection_rect
            
            # Find all strokes that have at least one point inside the selection rect
            self.selected_indices = []
            for i, stroke in enumerate(page.strokes):
                for pt in stroke.points:
                    if self._is_point_in_rect(pt["x"], pt["y"], rect):
                        self.selected_indices.append(i)
                        break
            
            if self.selected_indices:
                self.state = "SELECTED"
            else:
                self.state = "IDLE"
            return None
            
        elif self.state == "MOVING":
            dx = self.drag_offset_x
            dy = self.drag_offset_y
            self.drag_offset_x = 0.0
            self.drag_offset_y = 0.0
            
            if dx != 0.0 or dy != 0.0:
                cmd = MoveStrokeCommand(page, list(self.selected_indices), dx, dy)
                # the tool goes back to SELECTED so user can keep moving them
                self.state = "SELECTED"
                return cmd
            self.state = "SELECTED"
            return None
            
        return None
