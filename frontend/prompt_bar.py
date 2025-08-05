from PySide6.QtWidgets import (
    QWidget,
    QTextEdit,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QSizePolicy,
    QLabel,
    QTextBrowser
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from my_code.query_bot import query


class PromptBar(QWidget):
    def __init__(self):
        self.conversation_history = []
        super().__init__()

        self.setWindowTitle("QTextEdit Demo")

        self.chat_display = QTextBrowser()
        self.chat_display.setMaximumHeight(1000)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Say Anything...")
        self.text_edit.setFixedHeight(100)
        self.text_edit.keyPressEvent = self.handle_enter
        
        self.label = QLabel("Enter your prompt")
        self.label.setAlignment(Qt.AlignCenter)

        v_layout = QVBoxLayout()
        v_layout.addWidget(self.chat_display)
        v_layout.addWidget(self.label)
        v_layout.addWidget(self.text_edit)

        self.setLayout(v_layout)

    def handle_enter(self, event):
        if event.key() == Qt.Key_Return and (event.modifiers() & Qt.ShiftModifier):
            self.submit_prompt()
        else:
            QTextEdit.keyPressEvent(self.text_edit, event)

    def submit_prompt(self):
        user_input = self.text_edit.toPlainText()
        response = query(question=user_input, history=self.conversation_history)
        self.display_response(response)
        self.text_edit.clear()
    
    def display_response(self, text: str):
        self.chat_display.append(text)
        self.chat_display.append("\n\n")

