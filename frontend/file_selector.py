from typing import List

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog

class FileSelectorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.files: List[str] = []

        # Widget setup
        self.file_button = QPushButton("Select Files")
        self.file_button.clicked.connect(self.file_browser)

        self.clear_button = QPushButton("X")
        self.clear_button.setToolTip("Clear all selected files")
        self.clear_button.clicked.connect(self.clear_files)

        self.status_label = QLabel("0 files selected")

        # Layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.file_button)
        button_layout.addWidget(self.clear_button)

        layout = QVBoxLayout()
        layout.addLayout(button_layout)
        layout.addWidget(self.status_label)
        #layout.addStretch(10)

        self.setLayout(layout)
        

    def file_browser(self):
        new_files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Markdown Files (.md)",
            "",
            "Markdown Files (*.md);;All Files (*)"
        )
        if new_files:
            # Append only unique files
            self.files.extend(f for f in new_files if f not in self.files)

            self.update_ui()
    
    def clear_files(self):
        self.files = []
        self.update_ui()
    
    def update_ui(self):
        count = len(self.files)
        self.status_label.setText(f"{count} files selected")
        self.file_button.setText("Add More Files" if count > 0 else "Select Files")
        # Show last 5 files on hover
        self.file_button.setToolTip("\n".join(self.files[-5:])) 

    def get_files(self) -> List[str]:
        return self.files


        


