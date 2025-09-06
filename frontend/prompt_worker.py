import json

from PySide6.QtCore import Signal, QObject, Slot

from my_code.query_bot import query
from my_code.generate_metadata import generate_metadata
from my_code.create_file import create_file

class PromptWorker(QObject):
    finished = Signal()
    update_response = Signal(str)
    status_update = Signal(str)
    file_created = Signal(str)

    def __init__(
        self,
        session_id: str,
        prompt: str,
        history: list,
        system_prompt: str,
        model: str = "gpt-4o-mini",
        top_k: int = 10,
    ):
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
            stream_generator = query(
                session_id=self.session_id,
                question=self.prompt,
                history=self.history,
                model=self.model,
                top_k=self.top_k,
                system_prompt=self.system_prompt,
            )

            full_response = ""
            for chunk in stream_generator:
                full_response += chunk
                self.update_response.emit(chunk)
            
            # After streaming finishes
            try:
                current_tool_path = f"data/sessions/{self.session_id}/current_tool_call.json"
                with open(current_tool_path, "r", encoding="utf-8") as f:
                    final_tool_call = json.load(f)
            except FileNotFoundError:
                final_tool_call = None

            if final_tool_call and final_tool_call.get("name") == "create_file":
                args = final_tool_call["arguments"]
                file_path = create_file(
                    session_id=self.session_id,
                    filename=args["filename"],
                    extension=args["extension"],
                    content=args["content"],
                )
                self.update_response.emit(f"\n[File created: {file_path}]")
                self.file_created.emit(file_path)

            generate_metadata(session_id=self.session_id, history=self.history)
        except Exception as e:
            self.update_response.emit(f"\n[Error: {str(e)}]")

        self.finished.emit()
