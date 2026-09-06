from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class Sidebar(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Sidebar Stub"))
        # Phase 4: Implement sidebar for page navigation
