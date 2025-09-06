# Webpage Chatbot Frontend

This project provides a frontend for the chatbot application.  
Follow the steps below to set up a working development environment and run the app.

---

## 🚀 Getting Started

### 1) Go to the project folder
**Windows (PowerShell)**
```powershell
cd C:\Users\<you>\OneDrive\Desktop\VSCode_Projects\webpage_chatbot
```

**macOS / Linux (bash/zsh)**
```bash
cd ~/path/to/VSCode_Projects/webpage_chatbot
```

---

### 2) Create & activate a virtual environment

> Use Python 3.13 if possible. If your project’s `requirements.txt` demands older pins (e.g., NumPy 2.0.x), Python 3.11 is a safe fallback.

**Windows (PowerShell)**
```powershell
# Create
py -3.13 -m venv .venv

# Activate
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux (bash/zsh)**
```bash
# Create
python3 -m venv .venv

# Activate
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt.

---

### 3) Upgrade packaging tools

**Windows**
```powershell
python -m pip install --upgrade pip setuptools wheel
```

**macOS / Linux**
```bash
python3 -m pip install --upgrade pip setuptools wheel
```

---

### 4) Install dependencies

Make sure `requirements.txt` is compatible across platforms:

- **NumPy** → `numpy>=2.1,<3.0`  (Py 3.13-compatible wheels)
- **ONNX Runtime** →  
  - If CPU only: `onnxruntime==1.22.1`  
  - If using Windows DirectML GPU: `onnxruntime-directml==1.22.1; sys_platform == "win32"`
- **uvloop** (non-Windows only):  
  `uvloop==0.21.0; sys_platform != "win32"`

> If you previously used `uvicorn[standard]`, consider:
> ```
> uvicorn[standard]==0.34.2; sys_platform != "win32"
> uvicorn==0.34.2; sys_platform == "win32"
> ```

**Windows**
```powershell
python -m pip install -r requirements.txt
```

**macOS / Linux**
```bash
python3 -m pip install -r requirements.txt
```

---

### 5) Verify package structure

Ensure these files exist (empty `__init__.py` is OK):

```
webpage_chatbot/
│
├── frontend/
│   ├── __init__.py
│   ├── main.py
│   ├── main_window.py
│   └── prompt_area.py
│
├── my_code/
│   ├── __init__.py
│   └── query_bot.py
│
├── requirements.txt
└── run_app.py   (optional launcher)
```

No platform-specific commands for this step—just check your tree.

---

### 6) Run the frontend

> Always run **from the project root** so package imports resolve.

**Windows**
```powershell
# Preferred (module execution keeps project root on sys.path)
python -m frontend.main

# Optional: use a tiny launcher
# run_app.py
# from frontend.main import main
# if __name__ == "__main__":
#     main()
python run_app.py
```

**macOS / Linux**
```bash
python3 -m frontend.main

# Optional launcher
python3 run_app.py
```

---

### 7) VS Code setup (optional but recommended)

**Windows / macOS / Linux**

- **Select interpreter**
  - `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS) → **Python: Select Interpreter**
  - Choose:
    - Windows: `.venv\Scripts\python.exe`
    - macOS/Linux: `.venv/bin/python`

- **Configure launch** (`.vscode/launch.json`)
```json
{
  "name": "Run frontend",
  "type": "python",
  "request": "launch",
  "module": "frontend.main",
  "justMyCode": true
}
```

---

## 🧰 Troubleshooting

- **`ModuleNotFoundError` for a dependency you installed**
  - Ensure you’re using the **same interpreter** for install and run:
    - Windows:
      ```powershell
      python -c "import sys; print(sys.executable)"
      python -m pip show <package>
      ```
    - macOS/Linux:
      ```bash
      python3 -c "import sys; print(sys.executable)"
      python3 -m pip show <package>
      ```
  - Always prefer `python -m pip install ...` or `python3 -m pip install ...`.

- **`uvloop` error on Windows**
  - Make sure the `uvloop` line has a platform marker:
    ```
    uvloop==0.21.0; sys_platform != "win32"
    ```

- **NumPy tries to compile from source**
  - You’re likely on Python 3.13 with an older NumPy pin. Use:
    ```
    numpy>=2.1,<3.0
    ```

- **ONNX Runtime not found for your Python version**
  - Use `onnxruntime==1.22.1` for Python 3.13.
  - On Windows w/ DirectML GPU: `onnxruntime-directml==1.22.1; sys_platform == "win32"`

- **Running scripts directly (`python frontend/main.py`) fails to import `frontend`**
  - Use module execution from project root:
    - Windows: `python -m frontend.main`
    - macOS/Linux: `python3 -m frontend.main`
  - Ensure `frontend/__init__.py` and `my_code/__init__.py` exist.

---

## ✅ Summary

1. Create & activate venv  
   - Windows: `py -3.13 -m venv .venv && .\.venv\Scripts\Activate.ps1`  
   - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`  
2. Upgrade pip/setuptools/wheel  
3. Install requirements (with cross-platform pins)  
4. Run with `python -m frontend.main` (Windows) or `python3 -m frontend.main` (macOS/Linux)

That’s it—your frontend should be up and running!
