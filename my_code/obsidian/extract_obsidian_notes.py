import os
from pathlib import Path

def extract_md(md_path: Path) -> str:
    # Returns contents of markdown file as-is
    with md_path.open("r", encoding="utf-8") as f:
        return f.read()
    
def convert_md_to_txt(md_path: Path, base_src: Path, base_dest: Path) -> None:
    relative_path = md_path.relative_to(base_src)
    output_txt_path = base_dest / relative_path.with_suffix(".txt")

    os.makedirs(output_txt_path.parent, exist_ok=True)

    md_content = extract_md(md_path=md_path)
    with open(output_txt_path, "w", encoding="utf-8") as out_file:
        out_file.write(md_content)

def walk_convert(session_id: str, src_dir: str) -> None:
    src = Path(src_dir).resolve()
    dest = f"data/sessions/{session_id}/obsidian"

    if src.is_file() and src.suffix == ".md":
        convert_md_to_txt(md_path=src, base_src=src.parent, base_dest=dest)
    elif src.is_dir():
        for md_file in src.rglob("*.md"):
            convert_md_to_txt(md_path=md_file, base_src=src, base_dest=dest)

if __name__ == "__main__":
    walk_convert()
