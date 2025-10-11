import time

from typing import List

from my_code.crawler import crawl
from my_code.google.doc_pipeline import scrape_doc

from frontend.aggregation_worker import AggregateWorker
from frontend.file_selector import FileSelectorWidget
from frontend.multi_string_input_widget import MultiStringInputWidget
from frontend.save_session import save_session
from frontend.load_session import (
    select_and_unzip_session,
    load_metadata,
    return_chat_history,
    return_google_sources,
    return_obsidian_filepaths,
    return_websites,
)
from frontend.download_button import DownloadButton

from PySide6.QtWidgets import (
    QLineEdit,
    QVBoxLayout,
    QApplication,
    QLabel,
    QPushButton,
    QSizePolicy,
    QWidget,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QSize, QThread, Signal, Slot


class Sidebar(QWidget):
    session_saved = Signal(str)
    session_loaded = Signal(dict)

    def __init__(self, session_id: str, parent=None):
        super().__init__(parent)
        self.openai_api_key = None
        self.session_id = session_id
        self.main_window = parent
        self.files = []
        # Define available widgets
        self.docs_links = MultiStringInputWidget(
            label_text="Google Doc to Scrape",
            placeholder_text="https://docs.google.com/document/d/example",
        )

        self.domain_widget = MultiStringInputWidget(
            label_text="Domains to crawl", placeholder_text="soniox.com"
        )

        self.website_widget = MultiStringInputWidget(
            label_text="Links to websites to scrape",
            placeholder_text="https://example.com",
        )

        self.file_selector = FileSelectorWidget()

        self.aggregate_button = QPushButton("Aggregate Context")
        self.aggregate_button.clicked.connect(self.aggregate_data)

        self.save_button = QPushButton("Save session")
        self.save_button.clicked.connect(self.save_session_clicked)

        self.load_button = QPushButton("Load session")
        self.load_button.clicked.connect(self.load_session_clicked)

        self.download_button = DownloadButton(parent=self, session_id=self.session_id)

        v_layout = QVBoxLayout()

        v_layout.addWidget(self.docs_links)
        v_layout.addSpacing(10)
        v_layout.addWidget(self.domain_widget)
        v_layout.addSpacing(10)
        v_layout.addWidget(self.website_widget)
        v_layout.addSpacing(10)
        v_layout.addWidget(self.file_selector)
        v_layout.addSpacing(10)
        v_layout.addWidget(self.aggregate_button)
        v_layout.addSpacing(10)
        v_layout.addWidget(self.save_button)
        v_layout.addSpacing(10)
        v_layout.addWidget(self.load_button)
        v_layout.addSpacing(10)
        v_layout.addWidget(self.download_button)
        v_layout.addStretch(10)

        self.setLayout(v_layout)
        self.setMinimumHeight(750)
        self.setMaximumWidth(200)

    def aggregate_data(self):
        doc_urls = self.docs_links.get_strings()
        domain_url = self.domain_widget.get_strings()
        website_url = self.website_widget.get_strings()
        uploaded_files = self.file_selector.get_files()

        # Create Thread and Worker:
        self.thread = QThread()
        self.worker = AggregateWorker(
            openai_api_key=self.openai_api_key,
            doc_urls=doc_urls,
            session_id=self.session_id,
            domain_url=domain_url,
            website_url=website_url,
            uploaded_files=uploaded_files,
        )
        self.worker.moveToThread(self.thread)

        # Connect to signals:
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.status_update.connect(self.main_window.update_status)

        self.thread.start()

        self.aggregate_button.setEnabled(False)

        self.thread.finished.connect(lambda: self.aggregate_button.setEnabled(True))

    def save_session_clicked(self):
        try:
            save_session(self.main_window, self.session_id)
            self.session_saved.emit("Session saved successfully!")
        except:
            pass

    def load_session_clicked(self):

        # Warns user before overwritting unsaved session
        if not getattr(self.main_window, "session_saved", True):
            reply = QMessageBox.question(
                self,
                "Unsaved Session",
                "Your current session is not saved. Loading a new session will overwrite it. Continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return

        extracted_folder = select_and_unzip_session(parent=self)
        if not extracted_folder:
            return

        metadata = load_metadata(extracted_folder)
        if not metadata:
            QMessageBox.warning(self, "Warning", "Failed to load session metadata.")
            return

        if metadata["sources"]["google_docs"] is not None:
            self.docs_links.set_strings(metadata["sources"]["google_docs"])
        if metadata["sources"]["webpages"] is not None:
            self.website_widget.set_strings(metadata["sources"]["webpages"])
        if metadata["sources"]["obsidian"] is not None:
            self.file_selector.set_files(metadata["sources"]["obsidian"])
        if "session_id" in metadata:
            self.session_id = metadata["session_id"]

        chat_history = metadata.get("chat_history", [])
        self.session_loaded.emit(
            {"chat_history": chat_history, "session_id": self.session_id}
        )

    # A bit redundant, but doesnt hurt
    @Slot(str)
    def set_session_id(self, session_id: str) -> None:
        self.session_id = session_id
    
    @Slot(str)
    def set_openai_api(self, api: str) -> None:
        self.openai_api_key = api
