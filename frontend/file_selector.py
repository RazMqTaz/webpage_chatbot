import os

from typing import List

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QMessageBox,
)


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
        # layout.addStretch(10)

        self.setLayout(layout)

    def file_browser(self):
        new_files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Markdown Files (.md)",
            "",
            "All Files (*)",
        )
        if new_files:
            # Append only unique files
            self.files.extend(f for f in new_files if f not in self.files)

            self.update_ui()

    def clear_files(self):
        self.files = []
        self.update_ui()

    def update_ui(self) -> None:
        count = len(self.files)
        self.status_label.setText(f"{count} files selected")
        self.file_button.setText("Add More Files" if count > 0 else "Select Files")
        # Show last 5 files on hover
        self.file_button.setToolTip("\n".join(self.files[-5:]))

    def get_files(self) -> List[str]:
        return self.files

    def set_files(self, file_paths: List[str]) -> None:
        if not file_paths:
            self.files = []
            self.update_ui()

        missing_files = [path for path in file_paths if not os.path.exists(path)]
        valid_files = [path for path in file_paths if os.path.exists(path)]

        # Show warning for non-existant filepaths
        if missing_files:
            QMessageBox.warning(
                self,
                "Missing Files",
                "The following files could not be found and were skipped:\n"
                + "\n".join(missing_files),
            )

        self.files = valid_files
        self.update_ui()
