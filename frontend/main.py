import sys, uuid, os

from PySide6.QtWidgets import QApplication
from .main_window import MainWindow

# Create session ID
session_id = str(uuid.uuid4())
session_path = f"data/sessions/{session_id}"
os.makedirs(session_path, exist_ok=True)

app = QApplication(sys.argv)
app.sessionId = session_id
app.session_path = session_path

window = MainWindow(app)
window.show()

app.exec()
