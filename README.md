# Webscraper Bot
A voice-enabled AI agent that scrapes websites, reads PDFs, and answers questions using ChatGPT.

## Quickstart

### Step 1: Clone this repository

```bash
git clone https://github.com/RazMqTaz/webpage_chatbot.git
cd webpage_chatbot
```

### Step 2: Install python 3.12+
- Linux/macOS: Use pyenv, apt, brew, or download manually
- Windows: Use the official Python installer.
### Step 3: Verify python installation
```
python3 --version
```
#### (Optional) Install UV
- Note: I used UV, a fast Python package manager that can replace pip and virtualenv, I will include the commands for that as well

    **macOS/Linux**
    ```
    curl -Ls https://astral.sh/uv/install.sh | sh
    ```
    **Windows**
    ```
    iwr https://astral.sh/uv/install.ps1 -useb | iex
    ```
### Step 4: Create virtual environment
**bash**
```bash
python3 -m venv .venv # Without UV
uv venv .venv # Using UV
source .venv/bin/activate  # Linux/macOS, for both UV and non-UV
```
**cmd**
```cmd
.venv\Scripts\activate.bat  # Windows cmd
```
**powershell**
```powershell
.venv\Scripts\Activate.ps1  # Windows PowerShell
```
### Step 5: Install dependencies
```
uv pip install -r requirements.txt # UV
pip install -r requirements.txt # non-UV
```

### Step 6: Set up environment variables
- Create a file named '.env' in your project root with your OpenAI api key
```
OPENAI_API_KEY=your_openai_key
```
- This is how my code accesses the api key, but it's not the only way to do it.

### Step 7: Run code
- Each script has Click commands, none of them are required except the `--domain` string in the `crawler.py`, the `query_bot.py`, and in the 'run_pipeline.py'. There are defaults for all other args, they are the recommended settings.
- The `run_pipeline.py` will run all the crawler, scraper, chunker/embedder, and then activate the query bot.
- Each of these files can be called independently, for example you could rechunk/embed your scraped data if you wanted to change the chunk size or overlap.
- Just make sure you've run the previous step or else it wont work, for example don't run the scraper before the crawler.
- To run any script:
```python
python3 my_code/filename.py # --domain "https://example.com" (for crawler.py, query_bot.py, and run_pipeline.py)
```
## Important Notes:
- The `compressor.py` is another way to run this, essentially it takes ALL of the scraped data and runs a chatgpt query to summarize that text down to more manageable context. For obvious reasons this is not as efficient, it simply exists as another method to show why the chunk/embed system is better. If you wanted to integrate this sort of query bot into a voice bot pipeline, perhaps through pipecat, you would probably have to use the `compressor.py`, as chromadb is not natively supported.
- I have included the old_functions folder, it holds seperated versions of the `chunk_embed.py`, allowing you to do those steps one by one
