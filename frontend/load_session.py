import os, zipfile, json, shutil

from typing import List, Optional

from PySide6.QtWidgets import QFileDialog, QWidget, QMessageBox


def select_and_unzip_session(
    parent: Optional[QWidget] = None,
    extract_to: str = "temp_session",
    chromadb_target: str = "chromadb/sessions",
) -> Optional[str]:
    # Will unzip session save and store metadata to a temp location
    zip_path, _ = QFileDialog.getOpenFileName(
        parent, "Load Session", "", "Zip files (*.zip)"
    )
    if not zip_path:
        return None

    if os.path.exists(extract_to):
        shutil.rmtree(extract_to)

    try:
        with zipfile.ZipFile(zip_path, "r") as zipf:
            zipf.extractall(extract_to)
    except Exception as e:
        if parent:
            QMessageBox.critical(parent, "Error:", f"Failed to extract session:\n{e}")
        else:
            print(f"Failed to extract session:\n{e}")
        return None

    # Replace chromadb session
    new_chroma_path = os.path.join(extract_to, "sessions")
    if os.path.exists(new_chroma_path):
        try:
            if os.path.exists(chromadb_target):
                print(chromadb_target, new_chroma_path)
                shutil.rmtree(chromadb_target)
            shutil.copytree(new_chroma_path, chromadb_target)
            print("replaced chromadb session")
        except Exception as e:
            if parent:
                QMessageBox.warning(
                    parent,
                    "Error:",
                    "Failed to replace chromadb session. Re-aggregate context to rebuild the embedded context.",
                )
            else:
                print(f"Failed to replace chromadb:\n{e}")
            return None
    else:
        if parent:
            QMessageBox.warning(
                parent,
                "Error",
                "No embedded context found in this session. Re-aggregate context to build embedded context.",
            )
    return extract_to


def load_metadata(session_folder: str) -> Optional[dict]:
    metadata_path = os.path.join(session_folder, "metadata.json")
    if not os.path.exists(metadata_path):
        print("metadata.json not found in the session folder.")
        return None

    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        return metadata
    except Exception as e:
        print(f"Error reading metadata.json: {e}")
        return None


def return_chat_history(metadata: dict) -> str:
    return metadata["chat_history", ""]


def return_google_sources(metadata: dict) -> List[str]:
    return metadata.get("docs_links", [])


def return_obsidian_filepaths(metadata: dict) -> List[str]:
    return metadata.get("obsidian_filepaths", [])


def return_websites(metadata: dict) -> List[str]:
    return metadata.get("websites", [])
