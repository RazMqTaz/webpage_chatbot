import os

def create_file(session_id: str, filename: str, extension: str, content: str):
    # Creates file with bot-specific content and extension and stores it in the session folder

    if not extension.startswith("."):
        extension = "." + extension

    print(f"Creating file with name: {filename}, extension: {extension}, and content: {content}")

    # Make sure session folder exists
    session_folder = f"data/sessions/{session_id}/created_files"
    os.makedirs(session_folder, exist_ok=True)

    """This loop will iterate through files until it finds one that doesnt exist
       Basically this means that you could have:
       filename.py
       filename_2.py
       filename_3.py
       otherFilename.py
    """
    base_fn = filename
    counter = 1
    while True:
        candidate = f"{base_fn}{extension}" if counter == 1 else f"{base_fn}_{counter}{extension}"
        file_path = os.path.join(session_folder, candidate)
        if not os.path.exists(file_path):
            break
        counter += 1
        if counter >= 50:
            raise RuntimeError("Too many files with the same name in session folder")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return file_path

    