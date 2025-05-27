import requests
from bs4 import BeautifulSoup
import pdfplumber
import io
import os
import shutil
from tqdm import tqdm

SCRAPED_DATA_DIR = "data/scraped_data"
#to filter out media types that could break the script

MAX_STATUS_WIDTH = 80

#clears previously scraped data
if os.path.exists(SCRAPED_DATA_DIR):
    for filename in os.listdir(SCRAPED_DATA_DIR):
        file_path = os.path.join(SCRAPED_DATA_DIR, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")
else:os.makedirs(SCRAPED_DATA_DIR)

#load URLs
line_count = 0
with open("data/crawled_pages.txt", "r") as f:
    urls = [line.strip() for line in f if line.strip()]

progress = tqdm(total = len(urls), position = 0, desc = "Scraping", dynamic_ncols = True, bar_format="{l_bar}{bar:80}{r_bar}")
status_bar = tqdm(total = 1, position = 1, bar_format = '{desc}', leave = True)

for url in urls:
    try:
        #.lower() makes PDF to pdf so they all match
        if url.lower().endswith(".pdf"):
            #makes an HTML GET request to download the pdf, 10 second wait time to prevent hanging
            response = requests.get(url, timeout = 10) 
            #checks status of page, if 404 or some other error it wont process it
            response.raise_for_status()
            #response.content is the raw data in binary
            #io.BytesIO() wraps the raw binary data into a memory file like object
            #allows code to process data without actually needing to save it
            pdf_bytes = io.BytesIO(response.content)

            #opens pdf_bytes from memory
            with pdfplumber.open(pdf_bytes) as pdf:
                #extracts the text only from the pdf and turns it into one long string
                text = "\n".join(page.extract_text() or '' for page in pdf.pages)

        else:
            response = requests.get(url, timeout = 10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text(separator = "\n")

        #cleans up the scraped words, gets ride of whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        cleaned_text = "\n".join(lines)
        
        #sets up the progress bar so it looks cool while its doing stuff :)
        progress.update(1)
        msg = f"Scraping {url}"[:MAX_STATUS_WIDTH].ljust(MAX_STATUS_WIDTH)
        status_bar.set_description_str(msg)
        status_bar.refresh()
        progress.refresh()

        #cleans up the filename: https://example.com/docs/page -> example.com_docs_page
        filename = url.replace("https://", "").replace("http://", "").replace("/", "_")
        #creates a new filepath for each pages scraped data
        filepath = os.path.join("data/scraped_data", f"{filename}.txt")
        with open(filepath, "w", encoding = "utf-8") as out:
            out.write(cleaned_text)
        #ultimately we have a folder with x amount of txt files with all of the scraped text data
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")

