from PySide6.QtWidgets import QMainWindow
from .prompt_bar import PromptBar

class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Chatbot")
        self.setCentralWidget(PromptBar())


