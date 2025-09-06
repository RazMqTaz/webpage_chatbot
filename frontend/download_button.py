import os, shutil

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize



class DownloadButton(QPushButton):
    def __init__(self, session_id: str, parent=None):
        super().__init__(parent)
        self.CREATED_FILES_SRC = f"data/sessions/{session_id}/created_files"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.save_button = QPushButton()
        self.save_button.setIcon(QIcon("frontend/download.png"))
        self.save_button.setToolTip("Download Files")
        self.save_button.clicked.connect(self.download_button_clicked)

        layout.addWidget(self.save_button)
        layout.addStretch()
    
    def download_button_clicked(self):
        if not os.path.exists(self.CREATED_FILES_SRC):
            QMessageBox.critical(title="Error:", text="No files have been created")
        target_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Destination",
        )
        if target_dir:
            for item in os.listdir(self.CREATED_FILES_SRC):
                src_path = os.path.join(self.CREATED_FILES_SRC, item)
                dest_path = os.path.join(target_dir, item)

                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(src_path, dest_path)



