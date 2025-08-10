import os, zipfile

from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget
from PySide6.QtCore import Signal


def save_session(parent, session_id: str):
    metadata_path = f"data/sessions/{session_id}/metadata.json"
    chromadb_path = f"chromadb/sessions"

    # Check metadata and chromadb exist
    if not os.path.exists(metadata_path):
        QMessageBox.critical(
            parent, "Error:", "No metadata found. Make sure context is aggregated."
        )
    if not os.path.exists(chromadb_path):
        QMessageBox.critical(
            parent, "Error:", "No embedded data found. Make sure context is aggregated."
        )

    # Ask user where to save
    save_path, _ = QFileDialog.getSaveFileName(
        parent, 
        "Save session", 
        f"session_{session_id}", 
        "Zip files (*.zip)"
    )
    # User canceled
    if not save_path:
        return
    
    # Create Zip file
    try:
        with zipfile.ZipFile(save_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(metadata_path, arcname="metadata.json")

            # Add chromadb file elements
            for root, _, files in os.walk(chromadb_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, chromadb_path)
                    zipf.write(full_path, arcname=os.path.join("sessions", rel_path))
        if hasattr(parent, "status_update"):
            parent.status_update.emit("Session saved successfully")
    except Exception as e:
        QMessageBox.critical(parent, "Error", f"Failed to save session:\n{e}")

    




