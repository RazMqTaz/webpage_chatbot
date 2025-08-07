import os
import shutil

from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStatusBar
from PySide6.QtCore import Qt

from .prompt_area import PromptArea
from .sidebar import Sidebar


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.session_saved = False
        self.session_path = app.session_path
        self.session_id = app.sessionId
        self.setWindowTitle("Chatbot")
        
        container = QWidget()
        h_layout = QHBoxLayout(container)
        h_layout.setContentsMargins(1, 1, 1, 1)
        h_layout.setSpacing(0)

        self.sidebar = Sidebar(parent=self, session_id=self.session_id)
        self.prompt_area = PromptArea(session_id=self.session_id)
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        v_layout = QVBoxLayout()
        v_layout.addWidget(self.sidebar)
        h_layout.addLayout(v_layout)
        h_layout.addWidget(self.prompt_area)
        self.setCentralWidget(container)

    def update_status(self, message: str) -> None:
        self.statusbar.showMessage(message)
    
    def closeEvent(self, event):
        if not self.session_saved:
            # Could add warning for not saved here !!
            try:
                if os.path.exists(self.session_path):
                    shutil.rmtree(self.session_path)
                    print(f"Deleted unsaved session at {self.session_path}")

                chromadb_session_path = f"chromadb/sessions/{self.session_id}"
                if os.path.exists(chromadb_session_path):
                    shutil.rmtree(chromadb_session_path)
            except Exception as e:
                print(f"Failed to delete session: {e}")
        event.accept()


