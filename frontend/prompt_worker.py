from PySide6.QtCore import Signal, QObject

from my_code.query_bot import query
from my_code.generate_metadata import generate_metadata

class PromptWorker(QObject):
    finished = Signal()
    update_response = Signal(str)
    status_update = Signal(str)

    def __init__(self, session_id: str, prompt: str, history: str):
        super().__init__()
        self.session_id = session_id
        self.prompt = prompt
        self.history = history
        print(self.history)

    def run(self):
        self.status_update.emit("Thinking...")
        try:
            for chunk in query(session_id=self.session_id, question=self.prompt, history=self.history):
                self.update_response.emit(chunk)
            generate_metadata(session_id=self.session_id, history=self.history)
        except Exception as e:
            self.update_response.emit(f"\n[Error: {str(e)}]")

        self.finished.emit()
