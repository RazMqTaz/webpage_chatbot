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

    # Use format_tabs() to get tab-separated text
    formatter.format_tabs()

    # Save tabs as separate txt files in a directory
    out_dir = f"data/google/{doc_id}/document_tabs"
    formatter.save_tabs_as_txt(out_dir)

    print(f"\nTabs saved as separate text files in {out_dir}")


if __name__ == "__main__":
    main()
