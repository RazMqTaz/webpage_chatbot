import os
import json
from typing import List, Dict
import chromadb
import tldextract
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

DEFAULT_SYSTEM_PROMPT = ("You are a helpful assistant. Use the following extracted parts of documents to answer the user's questions. " +
                        "Do not make up answers. Stay grounded in the context provided. Do not create files unless instructed to.\n\n")
TOOLS_JSON_PATH = "my_code/tools.json"

with open(TOOLS_JSON_PATH, "r", encoding="utf-8") as f:
    tools = json.load(f)

def get_chroma_collection(session_id: str):
    # initialize chroma persistent client (load existing DB)
    chroma_client = chromadb.PersistentClient(path=f"chromadb/sessions/{session_id}")
    # load existing collection of text chunks
    collection = chroma_client.get_collection(name="chunks")
    return collection


def get_domain_name(url: str) -> str:
    extracted = tldextract.extract(url)
    return extracted.domain


# this function exists as a bridge between natural language question and the vector database
def embed_text(text: str) -> str:
    # converts text into vector(embedding)
    response = client.embeddings.create(
        # wrap text into a list, API allows batching so even one item must be in a list
        input=[text],
        model="text-embedding-3-small",
    )
    return response.data[0].embedding


def chat_with_context_stream(
    context_chunks: List[str],
    question: str,
    history: List[Dict[str, str]],
    tool_call_src: str,
    model: str = "gpt-4o-mini",
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
):
    context_text = "\n\n---\n\n".join(context_chunks)
    system_prompt = (
        system_prompt +
        f"{context_text}"
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": question})

    # sends chat-style request to OpenAI's API using the client previously created
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        # controls randomness of the output, 0.2 is good for factual summarization and QA (according to ChatGPT)
        temperature=0.2,
        stream=True,
        tools=tools,
        tool_choice="auto"
    )
    full_response = ""
    tool_call_accum = ""
    tool_name = None
    for chunk in response:
        # chunk is a dict-like object with 'choices' and delta content
        delta = chunk.choices[0].delta
        if hasattr(delta, "content") and delta.content:
            text = delta.content
            full_response += text
            # Emit partial chunks as they arrive
            yield text
        
        # Accumulate tool call fragments
        if getattr(delta, "tool_calls", None):
            for tc in delta.tool_calls:
                if tc.function.name and not tool_name:
                    tool_name = tc.function.name
                if tc.function.arguments:
                    tool_call_accum += tc.function.arguments

                # Write to JSON in real time
                if tool_name:
                    try:
                        args_dict = json.loads(tool_call_accum) if tool_call_accum else {}
                        with open(tool_call_src, "w", encoding="utf-8") as f:
                            json.dump({"name": tool_name, "arguments": args_dict}, f)
                    except json.JSONDecodeError:
                        # JSON is incomplete — just skip for now, next delta will add more
                        pass

    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": full_response})


def query(
    session_id: str,
    question: str,
    history: List[Dict[str, str]],
    top_k: int = 10,
    model: str = "gpt-4o-mini",
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
) -> str:
    question_embedding = embed_text(question)
    collection = get_chroma_collection(session_id=session_id)
    results = collection.query(
        [question_embedding], n_results=top_k, include=["documents"]
    )
    context_chunks = results["documents"][0]
    tool_call_src = f"data/sessions/{session_id}/current_tool_call.json"
    answer = chat_with_context_stream(
        context_chunks=context_chunks, question=question, history=history, model=model, system_prompt=system_prompt, tool_call_src=tool_call_src
    )
    return answer
