import json
import os
import pdb
import re

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]
SERVICE_ACCOUNT_FILE = "my_code/google/credentials.json"


def get_google_docs_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("docs", "v1", credentials=credentials)


# Extracts doc id from url
def extract_doc_id(url: str) -> str:
    match = re.search(r"/document/d/([a-zA-Z0-9-_]+)", url)
    if not match:
        raise ValueError("Invalid Google Docs URL")
    return match.group(1)


# Returns full doc info
def get_doc_content(doc_id: str) -> dict:
    service = get_google_docs_service()
    doc = service.documents().get(documentId=doc_id, includeTabsContent=True).execute()

    return doc


class DocFormatter:
    def __init__(self, full_doc_json: dict):
        self.doc = full_doc_json
        self.chunks = []

    def format_tabs(self, max_chunk_size=1500):
        # Parses doc and creates text chunks for chroma
        # Includes hierarchy like tabs, chapters, etc
        tabs = self.doc.get("tabs", [])
        all_tabs = []
        for tab in tabs:
            self._add_current_and_child_tabs(tab, all_tabs)

        tab_texts = []
        for idx, tab in enumerate(all_tabs, start=1):
            tab_title = tab.get("tabProperties", {}).get("title", "Untitled Tab")
            document_tab = tab.get("documentTab", {})
            content = document_tab.get("body", {}).get("content", [])

            # Extract text with style markers
            text = self._read_structural_elements(content)

            if text.strip():
                full_text = (
                    f"Document ID: {self.doc.get('documentId', '')}\n"
                    f"Document Title: {self.doc.get('title', '')}\n"
                    f"Tab Title: {tab_title}\n"
                    f"Tab Number: {idx}\n\n"
                    + text.strip()
                )
                tab_texts.append((idx, full_text))
        self.tab_texts = tab_texts
        return tab_texts
    
    def save_tabs_as_txt(self, out_dir="document_tabs"):
        os.makedirs(out_dir, exist_ok=True)
        base_doc_name = self.doc.get("title", "doc").replace(" ", "_")

        # Write/overwrite current tab files
        for idx, tab_text in self.tab_texts:
            filename = f"{base_doc_name}_tab{idx}.txt"
            filepath = os.path.join(out_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(tab_text)

        # Clean up leftover tab files with index > highest current index
        max_idx = max(idx for idx, _ in self.tab_texts) if self.tab_texts else 0
        i = max_idx + 1
        while True:
            leftover_file = os.path.join(out_dir, f"{base_doc_name}_tab{i}.txt")
            if os.path.exists(leftover_file):
                try:
                    os.remove(leftover_file)
                    print(f"Deleted leftover tab file: {leftover_file}")
                except Exception as e:
                    print(f"Failed to delete {leftover_file}: {e}")
                i += 1
            else:
                break


    def _add_current_and_child_tabs(self, tab, all_tabs) -> None:
        all_tabs.append(tab)
        for child_tab in tab.get("childTabs", []):
            self._add_current_and_child_tabs(child_tab, all_tabs)

    def _read_structural_elements(self, elements, indent_level=1) -> str:
        text = ""
        indent_str = "  " * indent_level  # 2 spaces per indent level in the txt file
        for el in elements:
            if "paragraph" in el:
                # Add heading/type markers if available
                para = el["paragraph"]
                style = para.get("paragraphStyle", {})
                named_style = style.get("namedStyleType")

                bullet = para.get("bullet")
                is_bullet = bullet is not None
                # For bullet nesting level, Google Docs API uses listId + nesting level index, so I just use that to decide hopw indented the bullet point is
                bullet_indent_level = bullet.get("nestingLevel", 0) if is_bullet else 0
                bullet_prefix = ""
                if is_bullet:
                    indent_str = "  " * bullet_indent_level
                    bullet_prefix = indent_str + "- "  # Use given bullet indent depth
                else:
                    indent_str = "  " * indent_level  # Base indent level

                # Normalize named_style to a readable form
                if named_style != "NORMAL_TEXT":
                    # Heading
                    named_style_text = named_style.replace("_", " ")
                    heading_text = ""
                    for pe in para.get("elements", []):
                        tr = pe.get("textRun")
                        if tr:
                            heading_text += tr.get("content", "")
                    heading_text = heading_text.strip()
                    text += f"\n=== {named_style_text}: {heading_text} ===\n"

                else:
                    # Normal paragraph text
                    para_text = ""
                    for pe in para.get("elements", []):
                        tr = pe.get("textRun")
                        if tr:
                            para_text += tr.get("content", "")
                    para_text = para_text.strip()
                    if para_text:
                        if is_bullet:
                            text += f"{bullet_prefix}{para_text}\n"
                        else:
                            text += indent_str + para_text + "\n"

            elif "table" in el:
                table = el["table"]
                for row in table.get("tableRows", []):
                    for cell in row.get("tableCells", []):
                        # luh recursion????
                        text += self._read_structural_elements(cell.get("content", []))
            elif "tableOfContents" in el:
                toc = el["tableOfContents"]
                text += self._read_structural_elements(toc.get("content", []))
        return text
