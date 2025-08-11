from PySide6.QtCore import Signal, QObject, Slot

from my_code.query_bot import query
from my_code.generate_metadata import generate_metadata


class PromptWorker(QObject):
    finished = Signal()
    update_response = Signal(str)
    status_update = Signal(str)

    def __init__(self, session_id: str, prompt: str, history: str, system_prompt: str, model: str = "gpt-4o-mini", top_k: int = 10):
        super().__init__()
        self.session_id = session_id
        self.prompt = prompt
        self.history = history
        self.model = model
        self.top_k = top_k
        self.system_prompt = system_prompt

    def run(self):
        self.status_update.emit("Thinking...")
        try:
            for chunk in query(
                session_id=self.session_id, question=self.prompt, history=self.history, model=self.model, top_k=self.top_k, system_prompt=self.system_prompt
            ):
                self.update_response.emit(chunk)
            generate_metadata(session_id=self.session_id, history=self.history)
        except Exception as e:
            self.update_response.emit(f"\n[Error: {str(e)}]")

        self.finished.emit()
