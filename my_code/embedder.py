import os
import chromadb
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

load_dotenv()

client = OpenAI()

chroma_client = chromadb.PersistentClient(path = "chromadb")

collection = chroma_client.get_or_create_collection(name = "web_chunks")

INPUT_DIR = "data/chunks"

def read_text(filename):
    with open(filename, "r", encoding = "utf-8") as f:
        return f.read()

def embed_texts(texts, batch_size = 100):
    #call OpenAI embeddings endpoint
    #this batches texts for efficiency (max ~2048 tokens per request)
    embeddings = []

    for i in range(0, len(texts), batch_size):
         batch = texts[i : i + batch_size]
         response = client.embeddings.create(
              input = batch,
              model = "text-embedding-3-small"
         )
         embeddings.extend([e.embedding for e in response.data])
    return embeddings
         

def main():
    #os.listdir(INPUT_DIR) gets all filenames in data/chunks/
    #only includes ".txt"
    #os.path.join(INPUT_DIR, f) creates full file paths like data/chunks/page_1.txt
    files = [os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.endswith(".txt")]

    #will store text from each chunk file
    all_texts = []

    #will store a unique identifier for each chunk, which is just the filename
    all_ids = []

    #tqdm gives progress bar
    for file_path in tqdm(files):
        #reads the chunk file path (calls previously defined function)
        text = read_text(file_path)
        all_texts.append(text)
        #appends file basename (e.g. page_1.txt) to store as chunk ID
        all_ids.append(os.path.basename(file_path))
    
    #sends list of chunk texts to OpenAI's embedding API
    #returns a list of vectors - one for each chunk of text
    embeddings = embed_texts(all_texts)

    #adds all the data into Chroma vector database
    #each chunk is stored with:
        #raw text (documents)
        #vector (embeddings)
        #a unique ID (ids)
    collection.upsert(
        documents = all_texts,
        embeddings = embeddings,
        ids = all_ids,
    )
    
    print(f"Embedded and stored {len(all_texts)} chunks!")

if __name__ == "__main__":
        main()