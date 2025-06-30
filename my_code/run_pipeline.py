import subprocess
import query_bot
import click
import sys


def run_script(args):
    print(f"\n=== Running: {' '.join(args)} ===")
    result = subprocess.run(args)
    if result.returncode != 0:
        print(f"Error running {' '.join(args)}")
        print(result.stderr)
        sys.exit(result.returncode)


@click.command()
# Crawler options
@click.option(
    "--domain", required=True, help="Starting domain (e.g., https://example.com/)"
)
@click.option(
    "--max-pages", default=100, show_default=True, type=int, help="Max pages to crawl"
)
@click.option(
    "--delay", default=1.0, show_default=True, type=float, help="Delay between requests"
)
@click.option(
    "--filter-media-types/--no-filter-media-types",
    default=True,
    show_default=True,
    help="Skip media files like .mp3, .zip",
)
@click.option(
    "--output",
    default="data/crawled_pages.txt",
    show_default=True,
    help="File to save crawled URLs",
)

# Scraper options
@click.option(
    "--input-file",
    default="data/crawled_pages.txt",
    show_default=True,
    help="File containing URLs to scrape",
)
@click.option(
    "--output-dir",
    default="data/scraped_data",
    show_default=True,
    help="Directory to save scraped data",
)

# Chunk/embed options
@click.option(
    "--input-dir",
    default="data/scraped_data",
    show_default=True,
    help="Directory with scraped text files",
)
@click.option(
    "--chunk-size", default=500, show_default=True, type=int, help="Tokens per chunk"
)
@click.option(
    "--chunk-overlap",
    default=50,
    show_default=True,
    type=int,
    help="Token overlap between chunks",
)
@click.option(
    "--batch-size",
    default=100,
    show_default=True,
    type=int,
    help="Batch size for embedding API calls",
)
@click.option(
    "--collection-name",
    default="web_chunks",
    show_default=True,
    help="ChromaDB collection name",
)
@click.option(
    "--chromadb-path",
    default="chromadb",
    show_default=True,
    help="Path for ChromaDB persistence",
)
@click.option(
    "--embedding-model",
    default="text-embedding-3-small",
    show_default=True,
    help="OpenAI embedding model",
)
@click.option(
    "--verbose/--quiet", default=True, show_default=True, help="Toggle verbosity"
)

# Query bot options
@click.option(
    "--top-k",
    default=5,
    show_default=True,
    type=int,
    help="Number of top matching chunks for query bot",
)
def main(
    domain,
    max_pages,
    delay,
    filter_media_types,
    output,
    input_file,
    output_dir,
    input_dir,
    chunk_size,
    chunk_overlap,
    batch_size,
    collection_name,
    chromadb_path,
    embedding_model,
    verbose,
    top_k,
):
    # Build and run crawler
    crawler_args = [
        "python3",
        "my_code/crawler.py",
        "--domain",
        domain,
        "--max-pages",
        str(max_pages),
        "--delay",
        str(delay),
        "--filter-media-types" if filter_media_types else "--no-filter-media-types",
        "--output",
        output,
    ]
    run_script(crawler_args)

    # Run scraper
    scraper_args = [
        "python3",
        "my_code/scraper.py",
        "--input-file",
        input_file,
        "--output-dir",
        output_dir,
    ]
    run_script(scraper_args)

    # Run chunk/embed
    chunk_args = [
        "python3",
        "my_code/chunk_embed.py",
        "--input-dir",
        input_dir,
        "--chunk-size",
        str(chunk_size),
        "--chunk-overlap",
        str(chunk_overlap),
        "--batch-size",
        str(batch_size),
        "--collection-name",
        collection_name,
        "--chromadb-path",
        chromadb_path,
        "--embedding-model",
        embedding_model,
    ]
    if verbose:
        chunk_args.append("--verbose")
    else:
        chunk_args.append("--quiet")

    run_script(chunk_args)

    query_bot_args = [
        "python3",
        "my_code/query_bot.py",
        "--domain",
        domain,
        "--top-k",
        str(top_k),
    ]
    run_script(query_bot_args)


if __name__ == "__main__":
    main()
