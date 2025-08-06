from PySide6.QtCore import Signal, QObject

from my_code.query_bot import query

class PromptWorker(QObject):
    finished = Signal()
    update_response = Signal(str)
    status_update = Signal(str)

    def __init__(self, prompt: str, history: str):
        super().__init__()
        self.prompt = prompt
        self.history = history

    def run(self):
        self.status_update.emit("Thinking...")

        try:
            for chunk in query(question=self.prompt, history=self.history):
                self.update_response.emit(chunk)
        except Exception as e:
            self.update_response.emit(f"\n[Error: {str(e)}]")

        self.finished.emit()
