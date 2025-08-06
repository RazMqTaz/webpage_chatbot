from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStatusBar
from PySide6.QtCore import Qt

from .prompt_area import PromptArea
from .sidebar import Sidebar


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Chatbot")
        
        container = QWidget()
        h_layout = QHBoxLayout(container)
        h_layout.setContentsMargins(1, 1, 1, 1)
        h_layout.setSpacing(0)

        self.sidebar = Sidebar(parent=self)
        self.prompt_area = PromptArea()
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        v_layout = QVBoxLayout()
        v_layout.addWidget(self.sidebar)
        h_layout.addLayout(v_layout)
        h_layout.addWidget(self.prompt_area)
        self.setCentralWidget(container)
    def update_status(self, message: str) -> None:
        self.statusbar.showMessage(message)


