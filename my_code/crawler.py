import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import time
from dotenv import load_dotenv
from tqdm import tqdm
import click

# config

# retrieves the domain name, urlparse splits up the url into different parts, .netloc returns the domain (eg: soniox.com)
DOMAIN = "https://soniox.com/"
MAX_PAGES = 10
REQUEST_DELAY_SEC = 1
FILTER_MEDIA_TYPES = True
MAX_STATUS_WIDTH = 80
IGNORED_EXTENSIONS = [
    ".mp3",
    ".mp4",
    ".avi",
    ".mov",
    ".wav",
    ".zip",
    ".rar",
    ".exe",
    ".doc",
    ".docx",
]


# adds '/' to the end of websites so that they dont get crawled twice
def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path or "/"
    if "." not in path.split("/")[-1]:
        if not path.endswith("/"):
            path += "/"
    normalized = parsed.scheme + "://" + parsed.netloc + path
    return normalized


# decides if media type violates the filter or not
def should_ignore_url(url: str, filter_media_types: bool) -> bool:
    if not filter_media_types:
        return False
    parsed_path = urlparse(url).path.lower()
    return any(parsed_path.endswith(ext) for ext in IGNORED_EXTENSIONS)

def crawl(
    domain: str, session_id: str, max_pages: int = MAX_PAGES, delay: float = REQUEST_DELAY_SEC, filter_media_types: bool = FILTER_MEDIA_TYPES, base_output_dir: str = "data/sessions"
) -> None:

    parsed = urlparse(domain)
    target_domain = parsed.netloc
    target_url = domain if domain.endswith("/") else domain + "/"

    output_dir = os.path.join(base_output_dir, session_id)
    os.makedirs(os.path.dirname(output_dir), exist_ok=True)
    output_file = os.path.join(output_dir, "crawled_pages.txt")

    # state
    q = deque([target_url])
    visited = set()

    progress = tqdm(
        total=max_pages,
        position=0,
        desc="Crawling",
        dynamic_ncols=True,
        bar_format="{l_bar}{bar:80}{r_bar}",
    )
    status_bar = tqdm(total=1, position=1, bar_format="{desc}", leave=True)

    while q and len(visited) <= MAX_PAGES:
        current_url = q.popleft()
        if current_url in visited:
            continue
        if should_ignore_url(current_url, filter_media_types):
            print(f"Skipping unsupported media type: {current_url}")
            continue

        # sets up the progress bar so it looks cool while its doing stuff :)
        visited.add(current_url)
        progress.update(1)
        msg = f"Visiting {current_url}"[:MAX_STATUS_WIDTH].ljust(MAX_STATUS_WIDTH)
        status_bar.set_description_str(msg)
        status_bar.refresh()
        progress.refresh()

        try:
            # checks each page, looking for errors
            response = requests.get(current_url, timeout=5)
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to retrieve {current_url} as {e}")
            continue

        # soup now holds all the HTML data for that page
        soup = BeautifulSoup(response.text, "html.parser")

        # <a> tags are HTML elements that create clickable links
        # The href attribute inside <a> contains the URL of the link
        for link_tag in soup.find_all("a", href=True):
            href = link_tag.get("href")
            full_url = urljoin(current_url, href)
            parsed_url = urlparse(full_url)

            if parsed_url.netloc == target_domain and parsed_url.scheme in {
                "http",
                "https",
            }:
                normalized_url = normalize_url(full_url)
                if normalized_url not in visited:
                    q.append(normalized_url)

        # delay for 1 second so to not overload the server
        time.sleep(delay)

    with open(output_file, "a") as f:
        for url in visited:
            f.write(url + "\n")

    click.echo(
        click.style(f"\nCrawling complete. {len(visited)} pages saved to {output_file}")
    )


if __name__ == "__main__":
    crawl()
