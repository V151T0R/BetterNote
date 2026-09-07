from core.commands.command import Command
from core.page import Page

class MoveStrokeCommand(Command):
    def __init__(self, page: Page, stroke_indices: list[int], dx: float, dy: float):
        self.page = page
        self.stroke_indices = stroke_indices
        self.dx = dx
        self.dy = dy

    def execute(self):
        for idx in self.stroke_indices:
            if 0 <= idx < len(self.page.strokes):
                stroke = self.page.strokes[idx]
                for pt in stroke.points:
                    pt["x"] += self.dx
                    pt["y"] += self.dy

    def undo(self):
        for idx in self.stroke_indices:
            if 0 <= idx < len(self.page.strokes):
                stroke = self.page.strokes[idx]
                for pt in stroke.points:
                    pt["x"] -= self.dx
                    pt["y"] -= self.dy
