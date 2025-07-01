# Markdown ETL Pipeline

A comprehensive ETL (Extract, Transform, Load) pipeline for processing markdown files and converting them into clean text files. This pipeline is designed with a modular architecture consisting of separate classes for each ETL stage.

## Architecture

The pipeline consists of four main components:

1. **`extractor.py`** - `MarkdownExtractor` class
   - Finds and reads markdown files from a specified directory
   - Extracts content and metadata from each file
   - Handles both `.md` and `.markdown` file extensions

2. **`transformer.py`** - `MarkdownTransformer` class
   - Cleans markdown syntax (headers, bold, italic, links, etc.)
   - Extracts sections based on headers
   - Parses YAML frontmatter
   - Provides metadata analysis

3. **`loader.py`** - `MarkdownLoader` class
   - Saves processed content to text files
   - Creates section-based files
   - Generates processing summaries
   - Exports data as JSON

4. **`main.py`** - `MarkdownETLPipeline` class
   - Orchestrates the entire ETL process
   - Provides command-line interface
   - Handles logging and error reporting

## Installation

The pipeline uses existing dependencies from your project. Ensure you have the following packages installed:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# Process markdown files with default settings
python my_code/main.py

# Specify custom input and output directories
python my_code/main.py --input-dir "path/to/markdown/files" --output-dir "path/to/output"
```

### Advanced Options

```bash
# Save each section as a separate file
python my_code/main.py --save-sections

# Skip JSON output
python my_code/main.py --no-json

# Skip metadata headers in text files
python my_code/main.py --no-metadata

# Combine multiple options
python my_code/main.py --input-dir "docs" --output-dir "processed" --save-sections --no-metadata
```

### Programmatic Usage

```python
from my_code.main import MarkdownETLPipeline

# Create pipeline
pipeline = MarkdownETLPipeline(
    input_directory="data/markdown_files",
    output_directory="data/processed_markdown"
)

# Run pipeline
results = pipeline.run_pipeline(
    save_sections=True,
    save_json=True,
    include_metadata=True
)

# Print summary
pipeline.print_summary(results)
```

## Input Structure

Place your markdown files in the input directory (default: `data/markdown_files/`):

```
data/
├── markdown_files/
│   ├── document1.md
│   ├── document2.markdown
│   └── subfolder/
│       └── document3.md
```

## Output Structure

The pipeline creates the following output structure:

```
data/
├── processed_markdown/
│   ├── document1.txt              # Clean text version
│   ├── document1_sections/        # Individual sections (if --save-sections)
│   │   ├── 01_Introduction.txt
│   │   ├── 02_Features.txt
│   │   └── 03_Conclusion.txt
│   ├── document2.txt
│   ├── processing_summary.txt     # Summary of all processed files
│   └── processed_data.json        # Structured data (if JSON enabled)
```

## Features

### Markdown Processing

The transformer handles various markdown elements:

- **Headers** (`# ## ###` etc.) - Removed, used for section detection
- **Bold/Italic** (`**bold**`, `*italic*`) - Syntax removed, text preserved
- **Code blocks** (```` ``` ````) - Removed entirely
- **Inline code** (`` `code` ``) - Backticks removed
- **Links** (`[text](url)`) - URL removed, text preserved
- **Images** (`![alt](src)`) - Source removed, alt text preserved
- **Lists** (`- item`, `1. item`) - Markers removed
- **Blockquotes** (`> text`) - `>` removed
- **Horizontal rules** (`---`) - Removed

### Metadata Extraction

- File size and modification time
- Word and line counts
- YAML frontmatter parsing
- Section detection and counting
- Code block and link detection

### Output Formats

1. **Text Files**: Clean, readable text with optional metadata headers
2. **Section Files**: Individual files for each section (optional)
3. **JSON Export**: Structured data for programmatic access
4. **Summary Report**: Processing statistics and file details

## Example

### Input Markdown
```markdown
---
title: "Sample Document"
---

# Introduction

This is **bold text** and *italic text*.

## Features

- Feature 1
- Feature 2

> This is a blockquote.
```

### Output Text File
```
# File: sample.md
# Original Path: data/markdown_files/sample.md
# File Size: 123 bytes
# Modified: 2024-01-15T10:30:00
# Word Count (Clean): 15
# Sections: 2
# Has Frontmatter: Yes
# Frontmatter: {"title": "Sample Document"}
# ==================================================

This is bold text and italic text.

Features

Feature 1
Feature 2

This is a blockquote.
```

## Error Handling

The pipeline includes comprehensive error handling:

- **File not found**: Logged as warning, skipped
- **Read errors**: Logged as error, file marked as failed
- **Parse errors**: Logged as warning, content processed as-is
- **Write errors**: Logged as error, file skipped

All errors are logged to both console and `markdown_etl.log` file.

## Logging

The pipeline creates detailed logs:

- **File**: `markdown_etl.log`
- **Console**: Real-time progress and summary
- **Levels**: INFO, WARNING, ERROR

## Performance

The pipeline is designed for efficiency:

- **Streaming**: Files are processed one at a time
- **Memory efficient**: Large files don't load entirely into memory
- **Parallel ready**: Architecture supports future parallel processing
- **Progress tracking**: Real-time progress indicators

## Integration

This ETL pipeline integrates well with your existing codebase:

- **Compatible**: Uses same dependencies and patterns
- **Extensible**: Easy to add new transformers or loaders
- **Configurable**: Flexible input/output options
- **Testable**: Modular design enables unit testing

## Future Enhancements

Potential improvements:

- Parallel processing for large file sets
- Additional output formats (CSV, XML, etc.)
- Custom transformation rules
- Web interface for configuration
- Integration with databases
- Real-time processing capabilities 