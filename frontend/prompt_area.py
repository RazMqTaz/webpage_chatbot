from markdown import markdown

from PySide6.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QLabel, QTextBrowser
from PySide6.QtCore import Qt, QThread, QTimer, Slot
from PySide6.QtGui import QKeyEvent, QTextCursor

from my_code.query_bot import query
from frontend.prompt_worker import PromptWorker


class PromptArea(QWidget):
    def __init__(self, session_id: str):
        super().__init__()
        self.session_id = session_id
        self.thinking_cursor = None
        self.conversation_history = []
        self.model = "gpt-4o-mini"

        self.setWindowTitle("Chatbot")

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

        self.thread = None
        self.worker = None

        # Chunk accumulation:
        self.chunk_buffer = ""
        self.flush_timer = QTimer()
        self.flush_timer.setInterval(100)
        self.flush_timer.timeout.connect(self.flush_buffer)

    def handle_enter(self, event):
        if event.key() == Qt.Key_Return and (event.modifiers() & Qt.ShiftModifier):
            self.submit_prompt()
        else:
            QTextEdit.keyPressEvent(self.text_edit, event)

    def submit_prompt(self):
        user_input = self.text_edit.toPlainText().strip()
        if not user_input:
            return

        self.chat_display.append(f"<b>You:</b> {user_input}")
        self.text_edit.setEnabled(False)

        # Create worker and thread:
        self.thread = QThread()
        self.worker = PromptWorker(
            session_id=self.session_id,
            prompt=user_input,
            history=self.conversation_history,
            model=self.model,
        )
        self.worker.moveToThread(self.thread)

        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.update_response.connect(self.handle_response_chunk)
        self.worker.status_update.connect(self.handle_status_update)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(lambda: self.text_edit.setEnabled(True))

        self.thread.start()

        self.text_edit.clear()

        self.chunk_buffer = ""
        self.flush_timer.start()

    def handle_response_chunk(self, text: str):
        if self.thinking_cursor is not None:
            cursor = self.chat_display.textCursor()
            cursor.setPosition(self.thinking_cursor)
            cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            cursor.deletePreviousChar()

            self.chat_display.setTextCursor(cursor)

            self.chat_display.append(f"\n\n<b>Bot:</b> ")
            self.thinking_cursor = None
        self.chunk_buffer += text

    def flush_buffer(self):
        if self.chunk_buffer:
            cursor = self.chat_display.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertText(self.chunk_buffer)
            self.chat_display.setTextCursor(cursor)
            self.chunk_buffer = ""

    def on_stream_finished(self):
        self.flush_timer.stop()
        self.text_edit.setEnabled(True)
        # Store last assistant message in history
        last_response = self.chat_display.toPlainText().split("Bot:")[-1].strip()
        self.conversation_history.append(
            {"role": "assistant", "content": last_response}
        )

    def handle_status_update(self, status):
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.thinking_cursor = cursor.position()
        self.chat_display.append(f"<i>{status}</i>")

    def load_chat_history(self, chat_history: list[dict]):
        self.chat_display.clear()
        self.conversation_history = []

        # Populate text browser with chat history
        for message in chat_history:
            role = message.get("role")
            content = message.get("content")

            html_content = markdown(content)

            if role == "user":
                self.chat_display.append(f"<b>You:</b><br>{html_content}")
            elif role == "assistant":
                self.chat_display.append(f"<b>Bot:</b><br>{html_content}")
            else:
                # In case of weird role, not really possible but still handled:
                self.chat_display.append(
                    f"<b>{role.capitalize()}:</b><br>{html_content}"
                )

            self.conversation_history.append({"role": role, "content": content})

        # Move display to bottom
        self.chat_display.moveCursor(QTextCursor.End)

    # @Slot defines this function as a slot, i think it makes it go faster? bit confusing tbh
    @Slot(str)
    def set_session_id(self, session_id: str):
        self.session_id = session_id

    @Slot(str)
    def set_model(self, model: str):
        self.model = model
        print("model changed to: " + self.model)
