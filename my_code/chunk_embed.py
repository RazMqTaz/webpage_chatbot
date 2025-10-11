import os
from pathlib import Path
from typing import List
import tiktoken
import chromadb
from openai import OpenAI
from tqdm import tqdm
import click

# Hardcoded defaults
DEFAULT_INPUT_DIR = "data"
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 100
DEFAULT_BATCH_SIZE = 100
DEFAULT_COLLECTION_NAME = "chunks"
DEFAULT_CHROMADB_PATH = "chromadb"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"

tokenizer = tiktoken.get_encoding("cl100k_base")


def chunk_embed(
    openai_spi_key: str,
    session_id: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    batch_size: int = DEFAULT_BATCH_SIZE,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
) -> None:

    client = OpenAI(api_key=openai_spi_key)
    input_dir = f"data/sessions/{session_id}/"

    # validate chunk_overlap < chunk_size
    while chunk_overlap >= chunk_size:
        click.echo(
            click.style(
                "Warning: chunk_overlap should be smaller than chunk_size. Adjusting chunk_overlap.",
                fg="yellow",
            )
        )
        chunk_overlap = chunk_size // 2

    chromadb_path = f"chromadb/sessions/{session_id}"
    chroma_client = chromadb.PersistentClient(path=chromadb_path)
    collection = chroma_client.get_or_create_collection(name=collection_name)

    def split_into_chunks(text: str) -> List[str]:
        tokens = tokenizer.encode(text)
        chunks = []
        start = 0
        while start < len(tokens):
            # goes through token list and slices out chunk_size tokens at a time
            end = start + chunk_size
            chunk_tokens = tokens[start:end]

            # converts the tokens back into readable text using .decode()
            chunk_text = tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)

            # start moves up through the full tokenized text
            # overlap is maintained to preserve context between chunks
            start += chunk_size - chunk_overlap
        return chunks

    def embed_texts(texts: List[str]) -> List[List[float]]:
        # call OpenAI embeddings endpoint
        # this batches texts for efficiency (max ~2048 tokens per request)
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            response = client.embeddings.create(input=batch, model=embedding_model)
            embeddings.extend([e.embedding for e in response.data])
        return embeddings

    all_texts = []
    all_ids = []

    # Walk through all dirs and find .txt files
    for root, _, files in os.walk(input_dir):
        for filename in files:
            # Skip crawled pages and files that don't end with .txt
            if filename == "crawled_pages.txt" or not filename.endswith(".txt"):
                continue
            if filename.endswith(".txt"):
                filepath = os.path.join(root, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read().strip()

                chunks = split_into_chunks(text)

                # Naming stuff, ultimately:
                # base_name holds filename with the stem ('.txt')
                # relative_root will change data/google/documents to google_documents
                # base_prefix will ensure unique ID's, even if files have same name in different data/ folders:
                #       e.g. "google_notes", "obsidian_notes"
                base_name = Path(filename).stem
                relative_root = (
                    Path(root).relative_to(input_dir).as_posix().replace("/", "_")
                )
                base_prefix = (
                    f"{relative_root}_{base_name}" if relative_root else base_name
                )

                for i, chunk in enumerate(chunks):
                    # Assigns id to each chunk
                    chunk_id = f"{base_prefix}_chunk{i}"
                    all_ids.append(chunk_id)
                    all_texts.append(chunk)

    # Embeds chunks
    embeddings = embed_texts(all_texts)
    # Sends embeddings to chromadb
    collection.upsert(documents=all_texts, embeddings=embeddings, ids=all_ids)

    click.echo(click.style(f"Embedded and stored {len(all_texts)} chunks!", fg="green"))


if __name__ == "__main__":
    chunk_embed()
