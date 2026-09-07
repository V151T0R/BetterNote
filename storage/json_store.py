import json
from core.notebook import Notebook
from storage.document_store import DocumentStore

class JSONStore(DocumentStore):
    @staticmethod
    def save(notebook: Notebook, filename: str) -> None:
        with open(filename, 'w') as f:
            json.dump(notebook.to_dict(), f)

    @staticmethod
    def load(filename: str) -> Notebook:
        with open(filename, 'r') as f:
            data = json.load(f)
        return Notebook.from_dict(data)
