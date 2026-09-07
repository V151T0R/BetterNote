from typing import Optional
from core.tools.tool import Tool
from core.stroke import Stroke
from core.page import Page
from core.commands.command import Command
from core.commands.add_stroke import AddStrokeCommand

class Pen(Tool):
    def __init__(self):
        self.color = "#000000"
        self.width = 3.0
        self.current_stroke: Optional[Stroke] = None

    def on_press(self, x: float, y: float, pressure: float, page: Page) -> None:
        self.current_stroke = Stroke(self.color, self.width)
        self.current_stroke.add_point(x, y, pressure)

    def on_move(self, x: float, y: float, pressure: float, page: Page) -> None:
        if self.current_stroke:
            self.current_stroke.add_point(x, y, pressure)

    def on_release(self, x: float, y: float, pressure: float, page: Page) -> Optional[Command]:
        if self.current_stroke and self.current_stroke.points:
            # We don't add the stroke to the page directly here, the command handles it
            cmd = AddStrokeCommand(page, self.current_stroke)
            self.current_stroke = None
            return cmd
        self.current_stroke = None
        return None
