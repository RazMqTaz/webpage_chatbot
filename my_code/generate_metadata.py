import os, json

from datetime import datetime
from typing import Optional

SESSION_BASE_PATH = "data/sessions"

def generate_metadata(session_id: str, history: Optional[str] = None, docs_links: Optional[list[str]] = None, obsidian_filepaths: Optional[list[str]] = None):
    session_path = os.path.join(SESSION_BASE_PATH, session_id)
    metadata_path = os.path.join(session_path, "metadata.json")

    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
    else:
        metadata = {
            "session_id": session_id,
            #"timestamp": datetime.now(datetime.timezone.utc).isoformat() + "Z",
            "chat_history": [],
            "sources": {
                "google_docs": [],
                "webpages": [],
                "obsidian": [],
            }
        }

    # Overwrite chat history
    if history is not None:
        metadata["chat_history"] = history
    
    # Append new doc links if provided
    if docs_links:
        existing_docs = set(metadata["sources"]["google_docs"])
        for link in docs_links:
            if link not in existing_docs:
                metadata["sources"]["google_docs"].append(link)
    
    # Append websites if provided - links passed individually are automatically added to crawled_pages.txt by the aggregation worker
    crawled_pages_file = os.path.join(session_path, "crawled_pages.txt")
    if os.path.exists(crawled_pages_file):
        with open(crawled_pages_file, "r") as f:
            crawled_links = [line.strip() for line in f.readlines()]
            existing_webpages = set(metadata["sources"]["webpages"])
            for url in crawled_links:
                if url and url not in existing_webpages:
                    metadata["sources"]["webpages"].append(url)

    # Append obsidian filepaths if provided

    if obsidian_filepaths:
        exisisting_obsidian = set(set(metadata["sources"]["obsidian"]))
        for path in obsidian_filepaths:
            if path not in exisisting_obsidian:
                metadata["sources"]["obsidian"].append(path)
    
    print(metadata)
    # Write back updated metadata
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    
        
    
        
