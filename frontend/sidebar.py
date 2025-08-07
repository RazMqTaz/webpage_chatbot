import time

from typing import List

from my_code.crawler import crawl
from my_code.google.doc_pipeline import scrape_doc
from frontend.aggregation_worker import AggregateWorker
from frontend.file_selector import FileSelectorWidget
from frontend.multi_string_input_widget import MultiStringInputWidget

from PySide6.QtWidgets import QLineEdit, QVBoxLayout, QApplication, QLabel, QPushButton, QSizePolicy, QWidget, QFileDialog
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QSize, QThread

class Sidebar(QWidget):
    def __init__(self, session_id: str, parent = None):
        super().__init__(parent)
        self.session_id = session_id
        self.main_window = parent
        self.files = []
        # Define available widgets
        self.docs_links = MultiStringInputWidget(
            label_text="Google Doc to Scrape",
            placeholder_text="https://docs.google.com/document/d/example"
        )

        self.domain_widget = MultiStringInputWidget(
            label_text="Domains to crawl",
            placeholder_text="soniox.com"
        )

        self.website_widget = MultiStringInputWidget(
            label_text="Links to websites to scrape",
            placeholder_text="https://example.com"
        )

        self.file_selector = FileSelectorWidget()

        self.aggregate_button = QPushButton("Aggregate Context")
        self.aggregate_button.clicked.connect(self.aggregate_data)
        
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
        v_layout.addStretch(10)

        self.setLayout(v_layout)
        self.setMinimumHeight(750)
        self.setMaximumWidth(200)

    def aggregate_data(self):
        doc_urls = self.docs_links.get_strings()
        domain_url = self.domain_widget.get_strings()
        website_url = self.website_widget.get_strings()
        obsidian_files = self.file_selector.get_files()

        # Create Thread and Worker:
        self.thread = QThread()
        self.worker = AggregateWorker(doc_urls=doc_urls, session_id=self.session_id, domain_url=domain_url, website_url=website_url, obsidian_files=obsidian_files)
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
        



        