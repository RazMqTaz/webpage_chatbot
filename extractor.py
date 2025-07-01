import os
import glob
from typing import List, Dict, Any
import logging

class MarkdownExtractor:
    """
    Extracts markdown files from a specified directory and its subdirectories.
    """
    
    def __init__(self, input_directory: str = "data/markdown_files"):
        """
        Initialize the MarkdownExtractor.
        
        Args:
            input_directory (str): Directory containing markdown files to extract
        """
        self.input_directory = input_directory
        self.logger = logging.getLogger(__name__)
        
    def find_markdown_files(self) -> List[str]:
        """
        Find all markdown files in the input directory and subdirectories.
        
        Returns:
            List[str]: List of file paths to markdown files
        """
        if not os.path.exists(self.input_directory):
            self.logger.warning(f"Input directory {self.input_directory} does not exist")
            return []
            
        # Find all .md and .markdown files recursively
        markdown_patterns = [
            os.path.join(self.input_directory, "**/*.md"),
            os.path.join(self.input_directory, "**/*.markdown")
        ]
        
        markdown_files = []
        for pattern in markdown_patterns:
            markdown_files.extend(glob.glob(pattern, recursive=True))
            
        self.logger.info(f"Found {len(markdown_files)} markdown files")
        return markdown_files
    
    def extract_file_content(self, file_path: str) -> Dict[str, Any]:
        """
        Extract content and metadata from a single markdown file.
        
        Args:
            file_path (str): Path to the markdown file
            
        Returns:
            Dict[str, Any]: Dictionary containing file metadata and content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # Get file metadata
            file_stats = os.stat(file_path)
            
            return {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'file_size': file_stats.st_size,
                'modified_time': file_stats.st_mtime,
                'content': content,
                'lines': content.split('\n'),
                'word_count': len(content.split())
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting content from {file_path}: {e}")
            return {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'error': str(e),
                'content': '',
                'lines': [],
                'word_count': 0
            }
    
    def extract_all(self) -> List[Dict[str, Any]]:
        """
        Extract all markdown files from the input directory.
        
        Returns:
            List[Dict[str, Any]]: List of dictionaries containing file data
        """
        markdown_files = self.find_markdown_files()
        extracted_data = []
        
        for file_path in markdown_files:
            file_data = self.extract_file_content(file_path)
            extracted_data.append(file_data)
            
        self.logger.info(f"Successfully extracted {len(extracted_data)} markdown files")
        return extracted_data 