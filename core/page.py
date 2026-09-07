from typing import List, Optional
from core.stroke import Stroke

class Page:
    def __init__(self, background: Optional[str] = None):
        self.background = background
        self.strokes: List[Stroke] = []

    def add_stroke(self, stroke: Stroke):
        self.strokes.append(stroke)

    def remove_stroke(self, index: int):
        if 0 <= index < len(self.strokes):
            del self.strokes[index]

    def to_dict(self) -> dict:
        return {
            "background": self.background,
            "strokes": [s.to_dict() for s in self.strokes]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Page':
        page = cls(data.get("background"))
        page.strokes = [Stroke.from_dict(s) for s in data.get("strokes", [])]
        return page
