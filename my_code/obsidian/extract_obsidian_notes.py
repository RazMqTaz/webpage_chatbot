import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import List

TEXT_EXTS = {
    ".md", ".py", ".java", ".txt", ".c", ".cpp", ".js", ".ts",
    ".html", ".css", ".json", ".xml", ".yaml", ".yml", ".sh"
}


def extract_text(path: Path) -> str:
    # Returns contents of markdown file as-is
    with path.open("r", encoding="utf-8") as f:
        return f.read()
    
def convert_to_txt(src_path: Path, base_src: Path, base_dest: Path) -> None:
    relative_path = src_path.relative_to(base_src)
    output_txt_path = base_dest / f"{relative_path}.txt"

    os.makedirs(output_txt_path.parent, exist_ok=True)

    content = extract_text(path=src_path)
    with open(output_txt_path, "w", encoding="utf-8") as out_file:
        out_file.write(content)

def collect_files(paths: List[str]) -> List[Path]:
    # Collects all whitelisted filetypes in a single process - fast
    result = []
    for p in paths:
        path = Path(p).resolve()
        if path.is_file() and path.suffix in TEXT_EXTS:
            result.append(path)
    return result


def walk_convert(session_id: str, input_paths: List[str]) -> None:
    dest = Path("data/sessions") / session_id / "obsidian"
    files_to_process = collect_files(input_paths)

    # Use multiprocessing for speed
    with ThreadPoolExecutor() as executer:
        futures = [
            executer.submit(
                convert_to_txt,
                f,
                f.parent if f.is_file() else f,
                dest
            )
            for f in files_to_process
        ]

        for future in futures:
            future.result()
