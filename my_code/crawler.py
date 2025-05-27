import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import time
import os
from dotenv import load_dotenv
from tqdm import tqdm
#config
load_dotenv(override = True)
target_url = os.getenv("TARGET_URL")
#retrieves the domain name, urlparse splits up the url into different parts, .netloc returns the domain (eg: soniox.com) 
DOMAIN = urlparse(target_url).netloc
MAX_PAGES = 100
REQUEST_DELAY = 1
MAX_STATUS_WIDTH = 80
FILTER_MEDIA_TYPES = True
IGNORED_EXTENSIONS = [".mp3", ".mp4", ".avi", ".mov", ".wav", ".zip", ".rar", ".exe", ".doc", ".docx"]

#adds '/' to the end of websites so that they dont get crawled twice
def normalize_url(url):
    parsed = urlparse(url)
    path = parsed.path or "/"
    if "." not in path.split("/")[-1]:
        if not path.endswith("/"):
            path += "/"
    normalized = parsed.scheme + "://" + parsed.netloc + path
    return normalized

#decides if media type violates the filter or not
def should_ignore_url(url):
    if not FILTER_MEDIA_TYPES:
        return False
    parsed_path = urlparse(url).path.lower()
    return any(parsed_path.endswith(ext) for ext in IGNORED_EXTENSIONS)

#state
q = deque([target_url])
visited = set()

progress = tqdm(total = MAX_PAGES, position = 0, desc = "Crawling", dynamic_ncols = True, bar_format="{l_bar}{bar:80}{r_bar}")
status_bar = tqdm(total = 1, position = 1, bar_format = '{desc}', leave = True)

while q and len(visited) <= MAX_PAGES:
    current_url = q.popleft()
    if current_url in visited:
        continue
    if should_ignore_url(current_url):
        print(f"Skipping unsupported media type: {current_url}")
        continue
    
    #sets up the progress bar so it looks cool while its doing stuff :)
    visited.add(current_url)
    progress.update(1)
    msg = f"Visiting {current_url}"[:MAX_STATUS_WIDTH].ljust(MAX_STATUS_WIDTH)
    status_bar.set_description_str(msg)
    status_bar.refresh()
    progress.refresh()


    try:
        #checks each page, looking for errors
        response = requests.get(current_url, timeout = 5)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to retrieve {current_url} as {e}")
        continue

    #soup now holds all the HTML data for that page
    soup = BeautifulSoup(response.text, "html.parser")

    #<a> tags are HTML elements that create clickable links
    #The href attribute inside <a> contains the URL of the link
    for link_tag in soup.find_all("a", href = True):
        href = link_tag.get("href")
        full_url = urljoin(current_url, href)
        parsed_url = urlparse(full_url)

        if parsed_url.netloc == DOMAIN and parsed_url.scheme in {"http", "https"}:
            normalized_url = normalize_url(full_url)
            if normalized_url not in visited:
                q.append(normalized_url)

    #delay for 1 second so to not overload the server            
    time.sleep(REQUEST_DELAY)

with open("data/crawled_pages.txt", "w") as f:
    for url in visited:
        f.write(url + "\n")