import os

from typing import List

from PySide6.QtCore import QObject, Signal

from my_code.crawler import crawl
from my_code.scraper import scrape
from my_code.chunk_embed import chunk_embed
from my_code.google.doc_pipeline import scrape_doc
from my_code.obsidian.extract_obsidian_notes import walk_convert
from my_code.generate_metadata import generate_metadata


class AggregateWorker(QObject):
    finished = Signal()
    status_update = Signal(str)

    def __init__(
        self,
        session_id: str,
        doc_urls: str,
        domain_url: str,
        website_url: str,
        obsidian_files: List[str],
    ):
        super().__init__()
        self.session_id = session_id
        self.doc_urls = doc_urls
        self.domain_url = domain_url
        self.website_url = website_url
        self.obsidian_files = obsidian_files

    def run(self):
        self.status_update.emit("Aggregating Context...")
        try:
            if self.doc_urls:
                self.status_update.emit("Scraping Google Doc...")
                for doc in self.doc_urls:
                    scrape_doc(doc, session_id=self.session_id)

            if self.domain_url:
                for domain in self.domain_url:
                    self.status_update.emit(
                        "Crawling Webpage... (This may take a while)"
                    )
                    crawl(domain, session_id=self.session_id)
                self.status_update.emit("Scraping Webpages... (This may take a while)")
                scrape(session_id=self.session_id)

            if self.website_url:
                self.status_update.emit("Scraping Website...")
                # os.makedirs(f"data/sessions/{self.session_id}", exist_ok=True)
                for url in self.website_url:
                    with open(
                        f"data/sessions/{self.session_id}/crawled_pages.txt", "a"
                    ) as f:
                        f.write(url + "\n")
                scrape(session_id=self.session_id)

            if self.obsidian_files:
                self.status_update.emit("Scraping Obsidian Note...")
                for note in self.obsidian_files:
                    walk_convert(session_id=self.session_id, src_dir=note)

            if (
                self.doc_urls
                or self.domain_url
                or self.website_url
                or self.obsidian_files
            ):
                self.status_update.emit("Chunking and Embedding data...")
                chunk_embed(session_id=self.session_id)
                generate_metadata(
                    session_id=self.session_id,
                    docs_links=self.doc_urls,
                    obsidian_filepaths=self.obsidian_files,
                )

            self.status_update.emit("Aggregation Complete!")
        except Exception as e:
            self.status_update.emit(f"Error: {str(e)}")
            print(e)
        finally:
            self.finished.emit()
