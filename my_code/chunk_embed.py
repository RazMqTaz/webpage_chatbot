import os
from pathlib import Path
from typing import List
import tiktoken
import chromadb
from openai import OpenAI
from tqdm import tqdm
import click

#Hardcoded defaults
DEFAULT_INPUT_DIR = "data/scraped_data"
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 100
DEFAULT_BATCH_SIZE = 100
DEFAULT_COLLECTION_NAME = "web_chunks"
DEFAULT_CHROMADB_PATH = "chromadb"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"

tokenizer = tiktoken.get_encoding("cl100k_base")
client = OpenAI()

#arg passing
@click.command()
@click.option("--input-dir", default=DEFAULT_INPUT_DIR, show_default=True, help="Directory with scraped text files")
@click.option("--chunk-size", default=DEFAULT_CHUNK_SIZE, show_default=True, type=int, help="Number of tokens per chunk")
@click.option("--chunk-overlap", default=DEFAULT_CHUNK_OVERLAP, show_default=True, type=int, help="Token overlap between chunks")
@click.option("--batch-size", default=DEFAULT_BATCH_SIZE, show_default=True, type=int, help="Batch size for embedding API calls")
@click.option("--collection-name", default=DEFAULT_COLLECTION_NAME, show_default=True, help="ChromaDB collection name")
@click.option("--chromadb-path", default=DEFAULT_CHROMADB_PATH, show_default=True, help="Path for ChromaDB persistence")
@click.option("--embedding-model", default=DEFAULT_EMBEDDING_MODEL, show_default=True, help="OpenAI embedding model")
@click.option("--verbose/--quiet", default=True, show_default=True, help="Toggle verbosity (displays debug info)")

def main(
    input_dir: str, 
    chunk_size: int, 
    chunk_overlap: int, 
    batch_size: int, 
    collection_name: str, 
    chromadb_path: str, 
    embedding_model: str, 
    verbose: bool) -> None:

    #validate chunk_overlap < chunk_size
    if chunk_overlap >= chunk_size:
        click.echo(click.style("Warning: chunk_overlap should be smaller than chunk_size. Adjusting chunk_overlap.", fg = "yellow"))
        chunk_overlap = chunk_size // 2
    
    if verbose:
        click.echo(f"Input directory: {input_dir}")
        click.echo(f"Chunk size: {chunk_size}")
        click.echo(f"Chunk overlap: {chunk_overlap}")
        click.echo(f"Batch size: {batch_size}")
        click.echo(f"ChromaDB collection: {collection_name}")
        click.echo(f"ChromaDB path: {chromadb_path}")
        click.echo(f"Embedding model: {embedding_model}")
    
    chroma_client = chromadb.PersistentClient(path = chromadb_path)
    collection = chroma_client.get_or_create_collection(name = collection_name)

    def split_into_chunks(text: str) -> List[str]:
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
            start += chunk_size - chunk_overlap
        return chunks
    
    def embed_texts(texts: List[str]) -> List[List[float]]:
        #call OpenAI embeddings endpoint
        #this batches texts for efficiency (max ~2048 tokens per request)
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            response = client.embeddings.create(
                input = batch,
                model = embedding_model
            )
            embeddings.extend([e.embedding for e in response.data])
        return embeddings
    
    all_texts = []
    all_ids = []

    files = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
    for filename in tqdm(files, desc = "Chunking files"):
        with open(os.path.join(input_dir, filename), "r", encoding = "utf-8") as f:
            text = f.read().strip()
        
        chunks = split_into_chunks(text)
        base_name = Path(filename).stem

        for i, chunk in enumerate(chunks):
            chunk_id = f"{base_name}_chunk{i}"
            all_ids.append(chunk_id)
            all_texts.append(chunk)
        
        if verbose:
            click.echo(f"Split {filename} into {len(chunks)} chunks")

    if verbose:
        click.echo("Embedding chunks...")

    embeddings = embed_texts(all_texts)

    collection.upsert(
        documents = all_texts,
        embeddings = embeddings,
        ids = all_ids
    )

    click.echo(click.style(f"Embedded and stored {len(all_texts)} chunks!", fg = "green"))

if __name__ == "__main__":
    main()
