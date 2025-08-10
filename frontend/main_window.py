import os
import shutil

from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStatusBar, QStackedWidget
from PySide6.QtCore import Qt, Signal

from .prompt_area import PromptArea
from .sidebar import Sidebar
from .tab_bar import TabBar
from .settings_page import Settings


class MainWindow(QMainWindow):
    session_id_changed = Signal(str)
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.session_saved = False
        self.session_path = app.session_path
        self.session_id = app.sessionId
        self.setWindowTitle("Chatbot")

        # Create widgets for main window
        self.sidebar = Sidebar(parent=self, session_id=self.session_id)
        self.sidebar.session_saved.connect(self.update_status)
        self.sidebar.session_loaded.connect(self.on_session_loaded)
        self.prompt_area = PromptArea(session_id=self.session_id)
        self.settings_page = Settings()
        self.tab_bar = TabBar()

        # sidebar and prompting page container
        sidebar_prompting_container = QWidget()
        h_layout = QHBoxLayout(sidebar_prompting_container)
        h_layout.setContentsMargins(1, 1, 1, 1)
        h_layout.setSpacing(0)
        h_layout.addWidget(self.sidebar)
        h_layout.addWidget(self.prompt_area)
        
        # Create stacked widget for view switching     
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(sidebar_prompting_container)
        self.stacked_widget.addWidget(self.settings_page)      

        main_container = QWidget()
        v_layout = QVBoxLayout(main_container)
        v_layout.setContentsMargins(1, 1, 1, 1)
        v_layout.addWidget(self.tab_bar)
        v_layout.addWidget(self.stacked_widget)
        self.setCentralWidget(main_container)

        # Connecting signals
        self.tab_bar.tab_switched.connect(self.stacked_widget.setCurrentIndex)
        self.session_id_changed.connect(self.prompt_area.set_session_id)
        self.session_id_changed.connect(self.sidebar.set_session_id)
        self.session_id_changed.connect(lambda s_id: setattr(self.app, "sessionId", s_id))
        self.settings_page.model_changed.connect(self.prompt_area.set_model)

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        

    def update_status(self, message: str) -> None:
        print(message)
        self.statusbar.showMessage(message, 2000)

    def on_session_loaded(self, data: dict):
        chat_history = data.get("chat_history", [])
        session_id = data.get("session_id", None)

        if session_id:
            self.session_id = session_id
            self.app.sessionId = session_id
            self.session_id_changed.emit(session_id)

        self.prompt_area.load_chat_history(chat_history)
        self.update_status("Session loaded successfully!")

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
        if os.path.exists("data/sessions"):
            shutil.rmtree("data/sessions")
        if os.path.exists("chromadb/sessions"):
            shutil.rmtree("chromadb/sessions")
        if os.path.exists("temp_session"):
            shutil.rmtree("temp_session")
        event.accept()
