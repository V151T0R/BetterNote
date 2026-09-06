from typing import Optional
from core.tools.tool import Tool
from core.stroke import Stroke
from core.page import Page
from core.commands.command import Command
from core.commands.add_stroke import AddStrokeCommand

class Highlighter(Tool):
    def __init__(self):
        self.color = "#ffff00"
        self.width = 20.0
        self.alpha = 100 # Translucency
        self.current_stroke: Optional[Stroke] = None

    def _get_rgba(self) -> str:
        # Qt supports #AARRGGBB natively in QColor(str)
        if len(self.color) == 7 and self.color.startswith("#"):
            return f"#{self.alpha:02x}{self.color[1:]}"
        elif len(self.color) == 9 and self.color.startswith("#"):
            # already has alpha
            return f"#{self.alpha:02x}{self.color[3:]}"
        return self.color

    def on_press(self, x: float, y: float, pressure: float, page: Page) -> None:
        self.current_stroke = Stroke(self._get_rgba(), self.width)
        self.current_stroke.add_point(x, y, pressure)

    def on_move(self, x: float, y: float, pressure: float, page: Page) -> None:
        if self.current_stroke:
            self.current_stroke.add_point(x, y, pressure)

    def on_release(self, x: float, y: float, pressure: float, page: Page) -> Optional[Command]:
        if self.current_stroke and self.current_stroke.points:
            cmd = AddStrokeCommand(page, self.current_stroke)
            self.current_stroke = None
            return cmd
        self.current_stroke = None
        return None
