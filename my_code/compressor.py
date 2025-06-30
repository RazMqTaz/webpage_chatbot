from openai import OpenAI
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INPUT_DIR = "data/scraped_data"
OUTPUT_FILE = "summaries.txt"
USER_PROMPT_TEMPLATE = (
    "Create a distilled version of input website data."
    "Create sections that keep the same page title as in input with rest of content shortened in a precise and concise way."
    "Be completely exhaustive and don't omit to much when parsing API endpoints and their input/output params."
    "A support chatbot will use distilled version as context. Output just summary and nothing else."
)
client = OpenAI()


# return URL (first line in scraped_data.txt files and the content as one string)
def get_url_and_content(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    url = lines[0].strip()
    content = "".join(lines[1:]).strip()
    return url, content


def summarize_with_chatgpt(content: str) -> str:

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": USER_PROMPT_TEMPLATE},
            {"role": "user", "content": content},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


def main():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for filename in os.listdir(INPUT_DIR):
            if filename.endswith(".txt"):
                file_path = os.path.join(INPUT_DIR, filename)
                try:
                    url, content = get_url_and_content(file_path)
                    print(f"Summarizing {url}...")
                    summary = summarize_with_chatgpt(content)
                    out.write(f"{{link: {url}, summary: \n{summary}}}\n\n\n")
                except Exception as e:
                    print(f"Failed to summarize {filename}: {e}")
    print(f"Summaries saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
