import math
from typing import Optional
from core.tools.tool import Tool
from core.page import Page
from core.commands.command import Command
from core.commands.delete_stroke import DeleteStrokeCommand

class Eraser(Tool):
    def __init__(self):
        self.radius = 12.0
        self.strokes_to_delete = set()
        self.is_erasing = False

    def _check_intersection(self, x: float, y: float, page: Page):
        # Very simple point-based distance check for intersection
        # Real apps might use line-segment distance for better precision
        for idx, stroke in enumerate(page.strokes):
            if idx in self.strokes_to_delete:
                continue
            for pt in stroke.points:
                dist = math.hypot(pt["x"] - x, pt["y"] - y)
                if dist <= self.radius + (stroke.width / 2.0):
                    self.strokes_to_delete.add(idx)
                    break

    def on_press(self, x: float, y: float, pressure: float, page: Page) -> None:
        self.is_erasing = True
        self.strokes_to_delete.clear()
        self._check_intersection(x, y, page)

    def on_move(self, x: float, y: float, pressure: float, page: Page) -> None:
        if self.is_erasing:
            self._check_intersection(x, y, page)

    def on_release(self, x: float, y: float, pressure: float, page: Page) -> Optional[Command]:
        self.is_erasing = False
        if self.strokes_to_delete:
            cmd = DeleteStrokeCommand(page, list(self.strokes_to_delete))
            self.strokes_to_delete.clear()
            return cmd
        return None
