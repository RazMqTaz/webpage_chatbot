import time

from typing import List

from my_code.crawler import crawl
from my_code.google.doc_pipeline import scrape_doc
from frontend.aggregation_worker import AggregateWorker
from frontend.file_selector import FileSelectorWidget

from PySide6.QtWidgets import QLineEdit, QVBoxLayout, QApplication, QLabel, QPushButton, QSizePolicy, QWidget, QFileDialog
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QSize, QThread

class Sidebar(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.main_window = parent
        self.files = []
        # Define available widgets
        docs_label = QLabel("Link to Google Doc: ")
        self.docs_link = QLineEdit()

        webpage_label = QLabel("Link to domain to crawl")
        self.webpage_link = QLineEdit()

        website_label = QLabel("Link to website to scrape")
        self.website_link = QLineEdit()

        self.file_selector = FileSelectorWidget()

        self.aggregate_button = QPushButton("Aggregate Context")
        self.aggregate_button.clicked.connect(self.aggregate_data)
        
        v_layout = QVBoxLayout()

        v_layout.addWidget(docs_label)
        v_layout.addWidget(self.docs_link)
        v_layout.addSpacing(10)
        v_layout.addWidget(webpage_label)
        v_layout.addWidget(self.webpage_link)
        v_layout.addSpacing(10)
        v_layout.addWidget(website_label)
        v_layout.addWidget(self.website_link)
        v_layout.addSpacing(10)
        v_layout.addWidget(self.file_selector)
        v_layout.addSpacing(10)
        v_layout.addWidget(self.aggregate_button)
        v_layout.addStretch(10)

        self.setLayout(v_layout)
        self.setMinimumHeight(750)
        self.setMaximumWidth(200)

    def aggregate_data(self):
        doc_url = self.docs_link.text().strip()
        webpage_url = self.webpage_link.text().strip()
        website_url = self.website_link.text().strip()
        obsidian_files = self.file_selector.get_files()

        # Create Thread and Worker:
        self.thread = QThread()
        self.worker = AggregateWorker(doc_url=doc_url, webpage_url=webpage_url, website_url=website_url, obsidian_files=obsidian_files)
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
        



        