from typing import List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PySide6.QtCore import Qt

class MultiStringInputWidget(QWidget):
    def __init__(self, label_text: str = "Enter value", placeholder_text: str = "https://example.com", parent = None):
        super().__init__(parent)

        self.inputs = []
        self.placeholder_text = placeholder_text

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.label = QLabel(label_text)
        self.layout.addWidget(self.label)

        self.clear_add_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Entry")
        self.add_button.clicked.connect(lambda: self.add_input())
        self.clear_button = QPushButton("Clear All")
        self.clear_button.clicked.connect(self.clear_all)
        self.clear_add_layout.addWidget(self.add_button)
        self.clear_add_layout.addWidget(self.clear_button)



        self.layout.addLayout(self.clear_add_layout)

        self.add_input()
    
    def add_input(self, text: str = "") -> None:
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(self.placeholder_text)
        line_edit.setText(text)
        self.inputs.append(line_edit)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(4)

        row.addWidget(line_edit)

        remove_button = QPushButton("X")
        remove_button.setFixedSize(24, 24)
        remove_button.clicked.connect(lambda: self.remove_input(row, line_edit))
        row.addWidget(remove_button)

        container = QWidget()
        container.setLayout(row)

        self.layout.insertWidget(self.layout.count() - 1, container)

    def remove_input(self, row_layout, line_edit) -> None:
        self.inputs.remove(line_edit)
        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            if item and item.widget() and item.widget().layout() == row_layout:
                widget_to_remove = item.widget()
                self.layout.removeWidget(widget_to_remove)
                widget_to_remove.deleteLater()
                break
    
    def get_strings(self) -> List[str]:
        return [edit.text().strip() for edit in self.inputs if edit.text().strip()]
    
    def clear_all(self):
        for edit in self.inputs:
            edit.parentWidget().deleteLater()
        self.inputs.clear()
    
        
        





