from core.commands.command import Command
from core.page import Page

class DeleteStrokeCommand(Command):
    def __init__(self, page: Page, stroke_indices: list[int]):
        self.page = page
        # Sort indices in descending order so deleting them doesn't shift prior indices
        self.stroke_indices = sorted(stroke_indices, reverse=True)
        self.deleted_strokes = []

    def execute(self):
        self.deleted_strokes = []
        for idx in self.stroke_indices:
            if 0 <= idx < len(self.page.strokes):
                self.deleted_strokes.append((idx, self.page.strokes[idx]))
                self.page.remove_stroke(idx)

    def undo(self):
        # Insert back in the original positions (requires inserting from smallest to largest index)
        # So we reverse our list of deleted strokes
        for idx, stroke in reversed(self.deleted_strokes):
            self.page.strokes.insert(idx, stroke)
