from typing import List, Optional
from core.page import Page
from core.stroke import Stroke

class Notebook:
    def __init__(self):
        self.pages: List[Page] = [Page()]

    def add_page(self, index: int, background: Optional[str] = None):
        self.pages.insert(index, Page(background))

    def delete_page(self, index: int) -> bool:
        if len(self.pages) <= 1:
            return False
        if 0 <= index < len(self.pages):
            del self.pages[index]
            return True
        return False

    def get_page(self, index: int) -> Optional[Page]:
        if 0 <= index < len(self.pages):
            return self.pages[index]
        return None

    def to_dict(self) -> dict:
        return {
            "pages": [p.to_dict() for p in self.pages]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Notebook':
        nb = cls()
        if isinstance(data, list):
             # Legacy load support where data was just list of strokes
             page = Page()
             page.strokes = [Stroke.from_dict(s) for s in data]
             nb.pages = [page]
        else:
             pages_data = data.get("pages", [{"strokes": [], "background": None}])
             nb.pages = [Page.from_dict(p) for p in pages_data]
        return nb
