from typing import List, Dict
import chromadb
import tldextract
from openai import OpenAI
import click

client = OpenAI()

#initialize chroma persistent client (load existing DB)
chroma_client = chromadb.PersistentClient(path = "chromadb")
#load existing collection of text chunks
collection = chroma_client.get_collection(name = "web_chunks")

def get_domain_name(url: str) -> str:
    extracted = tldextract.extract(url)
    return extracted.domain
    
#this function exists as a bridge between natural language question and the vector database
def embed_text(text: str) -> str:
    #converts text into vector(embedding)
    response = client.embeddings.create(
        #wrap text into a list, API allows batching so even one item must be in a list
        input = [text],
        model = "text-embedding-3-small"
    )
    return response.data[0].embedding

def query_chroma(query_embedding: List[float], top_k: int = 5) -> Dict:
    #use the embedding search in ChromaDB 
    results = collection.query(
        #chroma expects a list of vectors, even for one query
        query_embeddings = [query_embedding],
        #want the top N most relevant document chunks based on vector similarity
        n_results = top_k,
        include = ["documents"]
    )
    #results is what will get fed into the build_prompt function
    return results

def chat_with_context(context_chunks: List[str], question: str, history: List[Dict[str, str]]) -> str:
    context_text = "\n\n---\n\n".join(context_chunks)
    system_prompt = (
        "You are a helpful assistant. Use the following extracted parts of documents to answer the user's questions. "
        "Do not make up answers. Stay grounded in the context provided.\n\n"
        f"{context_text}"
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": question})
    
    #sends chat-style request to OpenAI's API using the client previously created
    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = messages,
        #controls randomness of the output, 0.2 is good for factual summarization and QA (according to ChatGPT)
        temperature = 0.2
    )
    answer = response.choices[0].message.content
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": answer})
    #returns first (and usually only) response's text
    return answer + "\n"

@click.command()
@click.option("--domain", required=True, help="The root URL of the website used for document context (e.g. https://soniox.com)")
@click.option("--top-k", default=5, show_default=True, help="Number of top matching document chunks to retrieve from ChromaDB")

def main(domain: str, top_k: int):
    name = get_domain_name(domain)
    conversation_history = []

    while True:
        question = input(f"Ask a question about {name} or type 'exit' to end session: \n").strip()
        if not question:
            print("Please enter a valid question.")
            continue
        if question == "exit":
            print("Ending session")
            break
        
        print("Embedding your question...")
        question_embedding = embed_text(question)

        print("Searching for relevant document chunks...")
        results = query_chroma(question_embedding, top_k = 5)

        #list of matched chunks text
        docs = results['documents'][0]

        print("Querying ChatGPT for answer...")
        answer = chat_with_context(docs, question, conversation_history)
        print("\nAnswer:\n" + answer)

if __name__ == "__main__":
    main()


