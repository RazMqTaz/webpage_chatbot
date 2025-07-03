# test_google_doc.py

from google_docs import (
    get_doc_content,
    extract_doc_id,
    DocFormatter,
)


def main():

    url = input("Enter Google Docs URL: ")
    try:
        doc_id = extract_doc_id(url)
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    print(f"\nFetching document with ID: {doc_id} ...")
    full_doc = get_doc_content(doc_id)

    formatter = DocFormatter(full_doc)

    formatter.format_to_chunks()
    formatter.save_chunks_as_txt(f"data/google/{doc_id}/document_chunks.txt")
    print(f"\nChunks saved as text file in data/google/{doc_id}/document_chunks.txt")

if __name__ == "__main__":
    main()
