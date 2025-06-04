# Webscraper Bot
A voice-enabled AI agent that scrapes websites, reads PDFs, and answers questions using ChatGPT.

## Quickstart

### Step 1: Clone this repository

```bash
git clone https://github.com/RazMqTaz/webscrapper-bot.git
cd webscrapper-bot
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

