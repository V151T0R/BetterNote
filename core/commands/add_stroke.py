from core.commands.command import Command
from core.stroke import Stroke
from core.page import Page

class AddStrokeCommand(Command):
    def __init__(self, page: Page, stroke: Stroke):
        self.page = page
        self.stroke = stroke

    def execute(self):
        self.page.add_stroke(self.stroke)

    def undo(self):
        # Remove the stroke we just added. 
        # Since we added it to the end, it should be the last one,
        # but to be safe we can just find it and remove it.
        if self.stroke in self.page.strokes:
            self.page.strokes.remove(self.stroke)
