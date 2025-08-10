from PySide6.QtWidgets import QWidget, QLineEdit, QLabel, QVBoxLayout, QHBoxLayout, QComboBox
from PySide6.QtCore import Signal

class Settings(QWidget):
    model_changed = Signal(str)
    def __init__(self):
        super().__init__()

        self.model_label = QLabel("Select GPT Model:")
        self.model_combo = QComboBox()

        self.model_combo.addItems([
            "gpt-4o-mini",
            "gpt-3.5-turbo",
            "gpt-4-1-mini",
            "gpt-4o",
        ])

        self.model_combo.currentTextChanged.connect(self.model_changed.emit)

        layout = QVBoxLayout()
        layout.addWidget(self.model_label)
        layout.addWidget(self.model_combo)
        self.setLayout(layout)

