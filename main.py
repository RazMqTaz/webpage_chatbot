#!/usr/bin/env python3
"""
Main ETL pipeline for processing markdown files.
Orchestrates the extraction, transformation, and loading of markdown content.
"""

import os
import sys
import logging
import click
from typing import Dict, List, Any
from tqdm import tqdm

# Import our ETL components
from extractor import MarkdownExtractor
from transformer import MarkdownTransformer
from loader import MarkdownLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('markdown_etl.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class MarkdownETLPipeline:
    """
    Main ETL pipeline class that orchestrates the entire process.
    """
    
    def __init__(self, input_directory: str = "data/markdown_files", 
                 output_directory: str = "data/processed_markdown"):
        """
        Initialize the ETL pipeline.
        
        Args:
            input_directory (str): Directory containing markdown files to process
            output_directory (str): Directory to save processed text files
        """
        self.input_directory = input_directory
        self.output_directory = output_directory
        self.logger = logging.getLogger(__name__)
        
        # Initialize ETL components
        self.extractor = MarkdownExtractor(input_directory)
        self.transformer = MarkdownTransformer()
        self.loader = MarkdownLoader(output_directory)
        
    def run_pipeline(self, save_sections: bool = False, 
                    save_json: bool = True, 
                    include_metadata: bool = True) -> Dict[str, Any]:
        """
        Run the complete ETL pipeline.
        
        Args:
            save_sections (bool): Whether to save sections as separate files
            save_json (bool): Whether to save data as JSON
            include_metadata (bool): Whether to include metadata in text files
            
        Returns:
            Dict[str, Any]: Pipeline results and statistics
        """
        self.logger.info("Starting Markdown ETL Pipeline")
        self.logger.info(f"Input directory: {self.input_directory}")
        self.logger.info(f"Output directory: {self.output_directory}")
        
        # Step 1: Extract
        self.logger.info("Step 1: Extracting markdown files...")
        extracted_data = self.extractor.extract_all()
        
        if not extracted_data:
            self.logger.warning("No markdown files found to process")
            return {
                'status': 'no_files_found',
                'extracted_count': 0,
                'transformed_count': 0,
                'saved_files': {}
            }
        
        # Step 2: Transform
        self.logger.info("Step 2: Transforming markdown content...")
        transformed_data = self.transformer.transform_all(extracted_data)
        
        # Step 3: Load
        self.logger.info("Step 3: Loading processed data...")
        saved_files = self.loader.load_all(
            transformed_data, 
            save_sections=save_sections, 
            save_json=save_json
        )
        
        # Calculate statistics
        successful_files = [f for f in transformed_data if 'error' not in f]
        error_files = [f for f in transformed_data if 'error' in f]
        total_words = sum(f.get('word_count_clean', 0) for f in successful_files)
        total_sections = sum(f.get('section_count', 0) for f in successful_files)
        
        results = {
            'status': 'completed',
            'extracted_count': len(extracted_data),
            'transformed_count': len(transformed_data),
            'successful_count': len(successful_files),
            'error_count': len(error_files),
            'total_words': total_words,
            'total_sections': total_sections,
            'saved_files': saved_files,
            'input_directory': self.input_directory,
            'output_directory': self.output_directory
        }
        
        self.logger.info("ETL Pipeline completed successfully")
        self.logger.info(f"Processed {len(successful_files)} files successfully")
        self.logger.info(f"Encountered {len(error_files)} errors")
        self.logger.info(f"Total words processed: {total_words:,}")
        self.logger.info(f"Total sections extracted: {total_sections}")
        
        return results
    
    def print_summary(self, results: Dict[str, Any]) -> None:
        """
        Print a summary of the pipeline results.
        
        Args:
            results (Dict[str, Any]): Pipeline results
        """
        print("\n" + "="*60)
        print("MARKDOWN ETL PIPELINE SUMMARY")
        print("="*60)
        print(f"Input Directory: {results['input_directory']}")
        print(f"Output Directory: {results['output_directory']}")
        print(f"Files Extracted: {results['extracted_count']}")
        print(f"Files Transformed: {results['transformed_count']}")
        print(f"Successful: {results['successful_count']}")
        print(f"Errors: {results['error_count']}")
        print(f"Total Words: {results['total_words']:,}")
        print(f"Total Sections: {results['total_sections']}")
        
        if results['saved_files']['text_files']:
            print(f"\nText Files Saved: {len(results['saved_files']['text_files'])}")
        if results['saved_files']['section_files']:
            print(f"Section Files Saved: {len(results['saved_files']['section_files'])}")
        if results['saved_files']['summary_file']:
            print(f"Summary File: {results['saved_files']['summary_file']}")
        if results['saved_files']['json_file']:
            print(f"JSON File: {results['saved_files']['json_file']}")
        
        print("="*60)

@click.command()
@click.option("--input-dir", default="data/markdown_files", 
              help="Directory containing markdown files to process")
@click.option("--output-dir", default="data/processed_markdown", 
              help="Directory to save processed text files")
@click.option("--save-sections", is_flag=True, 
              help="Save each section as a separate file")
@click.option("--no-json", is_flag=True, 
              help="Skip saving JSON output")
@click.option("--no-metadata", is_flag=True, 
              help="Skip metadata headers in text files")
def main(input_dir: str, output_dir: str, save_sections: bool, 
         no_json: bool, no_metadata: bool) -> None:
    """
    Markdown ETL Pipeline - Extract, Transform, and Load markdown files to text.
    
    This tool processes markdown files by:
    1. Extracting content and metadata from markdown files
    2. Transforming markdown syntax to clean text
    3. Loading the processed data into text files
    """
    try:
        # Create pipeline
        pipeline = MarkdownETLPipeline(input_dir, output_dir)
        
        # Run pipeline
        results = pipeline.run_pipeline(
            save_sections=save_sections,
            save_json=not no_json,
            include_metadata=not no_metadata
        )
        
        # Print summary
        pipeline.print_summary(results)
        
        if results['status'] == 'completed':
            click.echo(click.style("\n✅ Pipeline completed successfully!", fg="green"))
        else:
            click.echo(click.style("\n⚠️  Pipeline completed with warnings", fg="yellow"))
            
    except Exception as e:
        click.echo(click.style(f"\n❌ Pipeline failed: {e}", fg="red"))
        logging.error(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 