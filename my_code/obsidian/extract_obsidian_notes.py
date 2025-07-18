import os
from pathlib import Path

SOURCE_DIR = "/Users/erazemmattick/Desktop/Notes/school"
DEST_DIR = "data/obsidian"

def extract_md(md_path: Path) -> str:
    # Returns contents of markdown file as-is
    with md_path.open("r", encoding="utf-8") as f:
        return f.read()
    
def convert_md_to_txt(md_path: Path, base_src: Path, base_dest: Path) -> None:
    relative_path = md_path.relative_to(base_src)
    output_txt_path = base_dest / relative_path.with_suffix(".txt")

    os.makedirs(output_txt_path, exist_ok=True)

    md_content = extract_md(md_path=md_path)
    with open(output_txt_path, "w", encoding="utf-8") as out_file:
        out_file.write(md_content)

def walk_convert(src_dir: str, dest_dir: str) -> None:
    base_src = Path(src_dir).resolve()
    base_dest = Path(dest_dir).resolve()

    for md_file in base_src.rglob("*.md"):
        convert_md_to_txt(md_path=md_file, base_src=base_src, base_dest=base_dest)

if __name__ == "__main__":
    walk_convert(SOURCE_DIR, DEST_DIR)
