from abc import ABC, abstractmethod
from typing import Optional
from core.commands.command import Command
from core.page import Page

class Tool(ABC):
    @abstractmethod
    def on_press(self, x: float, y: float, pressure: float, page: Page) -> None:
        pass

    @abstractmethod
    def on_move(self, x: float, y: float, pressure: float, page: Page) -> None:
        pass

    @abstractmethod
    def on_release(self, x: float, y: float, pressure: float, page: Page) -> Optional[Command]:
        pass
