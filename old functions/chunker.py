import os
import tiktoken #used for accurate token counting
from pathlib import Path

#config
INPUT_DIR = "data/scraped_data"
OUTPUT_DIR = "data/chunks"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

#create output folder
os.makedirs(OUTPUT_DIR, exist_ok = True)

#load tokenizer
tokenizer = tiktoken.get_encoding("cl100k_base")

def split_into_chunks(text: str, chunk_size = CHUNK_SIZE, overlap = CHUNK_OVERLAP):
    #converts full text into list of tokens
    tokens = tokenizer.encode(text)
    chunks = []

    start = 0
    while start < len(tokens):

        #goes through token list and slices out chunk_size tokens at a time
        end = start + chunk_size
        chunk_tokens = tokens[start : end]

        #converts the tokens back into readable text using .decode()
        chunk_text = tokenizer.decode(chunk_tokens)
        chunks.append(chunk_text)

        #start moves up through the full tokenized text
        #overlap is maintained to preserve context between chunks
        start += chunk_size - overlap
    
    return chunks

#process text files
for filename in os.listdir(INPUT_DIR):

    #skips any non-txt files (there shouldn't be any)
    if not filename.endswith(".txt"):
        continue
    
    #reads in scraped data to be chunked
    with open(os.path.join(INPUT_DIR, filename), "r", encoding = "utf-8")as f:
        #reads in current .txt file and then strips whitespace
        text = f.read().strip()
    
    chunks = split_into_chunks(text)

    #iterates through all the chunks, gives the text of the chunk and the corresponding index [i]
    for i, chunk in enumerate(chunks):

        #creates new name for current chunk
        #Path(filename).stem gets base name without the ".txt"
        #appends _chunk[i]
        chunk_filename = f"{Path(filename).stem}_chunk{i}.txt"

        #builds full path to where this chunk will be saved
        chunk_path = os.path.join(OUTPUT_DIR, chunk_filename)
        with open(chunk_path, "w", encoding = "utf-8") as out:
            out.write(chunk)
    
    print(f"split {filename} into {len(chunks)} chunks")