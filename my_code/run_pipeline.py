import subprocess
#import query_bot

def run_script(path, description):
    print(f"\n=== Running: {description} ===")
    result = subprocess.run(["python3", path])
    if result.returncode != 0:
        print(f"Error running {description}")
        print(result.stderr)
        return False
    else:
        print(f"Finished: {description}")
        return True

def main():
    steps = [
        ("my_code/crawler.py", "Crawler"),
        ("my_code/scraper.py", "Scraper"),
        ("my_code/chunker.py", "Chunker"),
        ("my_code/embedder.py", "Embedder"),
    ]

    #run all except query bot
    for path, desc in steps:
        success = run_script(path, desc)
        if not success:
            print("Pipeline stopped due to an error")
            return

    print("\nStarting interactive query session...\n")
    #query_bot.main()
    

if __name__ == "__main__":
    main()

