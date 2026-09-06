from typing import List, Dict, Any

class Stroke:
    def __init__(self, color: str, width: float):
        self.color = color
        self.width = width
        self.points: List[Dict[str, float]] = []

    def add_point(self, x: float, y: float, pressure: float):
        self.points.append({"x": x, "y": y, "p": pressure})

    def to_dict(self) -> Dict[str, Any]:
        return {
            "color": self.color,
            "width": self.width,
            "points": self.points
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Stroke':
        stroke = cls(data.get("color", "#000000"), data.get("width", 3.0))
        stroke.points = data.get("points", [])
        return stroke
