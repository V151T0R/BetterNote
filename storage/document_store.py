from abc import ABC, abstractmethod
from core.notebook import Notebook

class DocumentStore(ABC):
    @staticmethod
    @abstractmethod
    def save(notebook: Notebook, filename: str) -> None:
        pass

    @staticmethod
    @abstractmethod
    def load(filename: str) -> Notebook:
        pass
