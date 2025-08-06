import os

from typing import List

from PySide6.QtCore import QObject, Signal

from my_code.crawler import crawl
from my_code.scraper import scrape
from my_code.chunk_embed import chunk_embed
from my_code.google.doc_pipeline import scrape_doc
from my_code.obsidian.extract_obsidian_notes import walk_convert


class AggregateWorker(QObject):
    finished = Signal()
    status_update = Signal(str)

    def __init__(
        self,
        doc_url: str,
        webpage_url: str,
        website_url: str,
        obsidian_files: List[str],
    ):
        super().__init__()
        self.doc_url = doc_url
        self.webpage_url = webpage_url
        self.website_url = website_url
        self.obsidian_files = obsidian_files

    def run(self):
        self.status_update.emit("Aggregating Context...")
        try:
            if self.doc_url:
                self.status_update.emit("Scraping Google Doc...")
                scrape_doc(self.doc_url)
            if self.webpage_url:
                self.status_update.emit("Crawling Webpage... (This may take a while)")
                crawl(self.webpage_url)
                self.status_update.emit("Scraping Webpages... (This may take a while)")
                scrape()
            if self.website_url:
                self.status_update.emit("Scraping Website...")
                with open("data/crawled_pages.txt", "a") as f:
                    f.write(self.website_url + "\n")
                scrape()
            if self.obsidian_files:
                self.status_update.emit("Scraping Obsidian Note...")
                for note in self.obsidian_files:
                    print(note)
                    walk_convert(src_dir=note)
            if self.doc_url or self.webpage_url or self.obsidian_files:
                self.status_update.emit("Chunking and Embedding data...")
                chunk_embed()

            self.status_update.emit("Aggregation Complete!")
        except Exception as e:
            self.status_update.emit(f"<span style='color:red'>Error: {str(e)}</span>")
            print(e)
        finally:
            self.finished.emit()
