import os
import json
from typing import List, Dict, Any
import logging
from datetime import datetime

class MarkdownLoader:
    """
    Loads transformed markdown data into text files and other output formats.
    """
    
    def __init__(self, output_directory: str = "data/processed_markdown"):
        """
        Initialize the MarkdownLoader.
        
        Args:
            output_directory (str): Directory to save processed text files
        """
        self.output_directory = output_directory
        self.logger = logging.getLogger(__name__)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_directory, exist_ok=True)
        
    def save_as_text_file(self, file_data: Dict[str, Any], include_metadata: bool = True) -> str:
        """
        Save a single transformed markdown file as a text file.
        
        Args:
            file_data (Dict[str, Any]): Transformed file data
            include_metadata (bool): Whether to include metadata at the top of the file
            
        Returns:
            str: Path to the saved text file
        """
        if 'error' in file_data:
            self.logger.warning(f"Skipping file with error: {file_data['file_path']}")
            return ""
            
        try:
            # Create filename from original filename
            base_name = os.path.splitext(file_data['file_name'])[0]
            text_filename = f"{base_name}.txt"
            text_filepath = os.path.join(self.output_directory, text_filename)
            
            with open(text_filepath, 'w', encoding='utf-8') as f:
                if include_metadata:
                    # Write metadata header
                    f.write(f"# File: {file_data['file_name']}\n")
                    f.write(f"# Original Path: {file_data['file_path']}\n")
                    f.write(f"# File Size: {file_data['file_size']} bytes\n")
                    f.write(f"# Modified: {datetime.fromtimestamp(file_data['modified_time']).isoformat()}\n")
                    f.write(f"# Word Count (Clean): {file_data['word_count_clean']}\n")
                    f.write(f"# Sections: {file_data['section_count']}\n")
                    
                    # Write metadata details
                    metadata = file_data.get('metadata', {})
                    if metadata.get('has_frontmatter'):
                        f.write(f"# Has Frontmatter: Yes\n")
                        if metadata.get('frontmatter'):
                            f.write(f"# Frontmatter: {json.dumps(metadata['frontmatter'], indent=2)}\n")
                    
                    f.write(f"# {'='*50}\n\n")
                
                # Write clean content
                f.write(file_data['clean_content'])
                
            self.logger.info(f"Saved text file: {text_filepath}")
            return text_filepath
            
        except Exception as e:
            self.logger.error(f"Error saving text file for {file_data['file_path']}: {e}")
            return ""
    
    def save_sections_as_separate_files(self, file_data: Dict[str, Any]) -> List[str]:
        """
        Save each section of a markdown file as a separate text file.
        
        Args:
            file_data (Dict[str, Any]): Transformed file data
            
        Returns:
            List[str]: List of paths to saved section files
        """
        if 'error' in file_data or not file_data.get('sections'):
            return []
            
        saved_files = []
        base_name = os.path.splitext(file_data['file_name'])[0]
        
        try:
            # Create sections subdirectory
            sections_dir = os.path.join(self.output_directory, f"{base_name}_sections")
            os.makedirs(sections_dir, exist_ok=True)
            
            for i, section in enumerate(file_data['sections']):
                section_title = section.get('title', f'Section_{i+1}')
                # Clean filename
                safe_title = "".join(c for c in section_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_title = safe_title.replace(' ', '_')
                
                section_filename = f"{i+1:02d}_{safe_title}.txt"
                section_filepath = os.path.join(sections_dir, section_filename)
                
                with open(section_filepath, 'w', encoding='utf-8') as f:
                    f.write(f"# Section: {section_title}\n")
                    f.write(f"# Level: {section.get('level', 'N/A')}\n")
                    f.write(f"# Source File: {file_data['file_name']}\n")
                    f.write(f"# {'='*50}\n\n")
                    f.write(section.get('content', ''))
                
                saved_files.append(section_filepath)
                
            self.logger.info(f"Saved {len(saved_files)} section files for {file_data['file_name']}")
            
        except Exception as e:
            self.logger.error(f"Error saving section files for {file_data['file_path']}: {e}")
            
        return saved_files
    
    def save_metadata_summary(self, all_file_data: List[Dict[str, Any]]) -> str:
        """
        Save a summary of all processed files' metadata.
        
        Args:
            all_file_data (List[Dict[str, Any]]): List of all transformed file data
            
        Returns:
            str: Path to the saved summary file
        """
        try:
            summary_filepath = os.path.join(self.output_directory, "processing_summary.txt")
            
            with open(summary_filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Markdown Processing Summary\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n")
                f.write(f"# Total Files Processed: {len(all_file_data)}\n\n")
                
                # Calculate totals
                total_words = sum(f.get('word_count_clean', 0) for f in all_file_data if 'error' not in f)
                total_sections = sum(f.get('section_count', 0) for f in all_file_data if 'error' not in f)
                files_with_errors = sum(1 for f in all_file_data if 'error' in f)
                
                f.write(f"Total Words (Clean): {total_words:,}\n")
                f.write(f"Total Sections: {total_sections}\n")
                f.write(f"Files with Errors: {files_with_errors}\n\n")
                
                f.write(f"# Individual File Details\n")
                f.write(f"# {'='*80}\n\n")
                
                for file_data in all_file_data:
                    f.write(f"File: {file_data['file_name']}\n")
                    f.write(f"  Path: {file_data['file_path']}\n")
                    f.write(f"  Size: {file_data.get('file_size', 'N/A')} bytes\n")
                    f.write(f"  Words (Clean): {file_data.get('word_count_clean', 'N/A')}\n")
                    f.write(f"  Sections: {file_data.get('section_count', 'N/A')}\n")
                    
                    if 'error' in file_data:
                        f.write(f"  Status: ERROR - {file_data['error']}\n")
                    else:
                        f.write(f"  Status: SUCCESS\n")
                    
                    f.write("\n")
            
            self.logger.info(f"Saved processing summary: {summary_filepath}")
            return summary_filepath
            
        except Exception as e:
            self.logger.error(f"Error saving processing summary: {e}")
            return ""
    
    def save_as_json(self, all_file_data: List[Dict[str, Any]]) -> str:
        """
        Save all transformed data as a JSON file for programmatic access.
        
        Args:
            all_file_data (List[Dict[str, Any]]): List of all transformed file data
            
        Returns:
            str: Path to the saved JSON file
        """
        try:
            json_filepath = os.path.join(self.output_directory, "processed_data.json")
            
            # Prepare data for JSON serialization
            json_data = {
                'processing_info': {
                    'timestamp': datetime.now().isoformat(),
                    'total_files': len(all_file_data),
                    'output_directory': self.output_directory
                },
                'files': []
            }
            
            for file_data in all_file_data:
                # Remove raw content to keep JSON file manageable
                json_file_data = {k: v for k, v in file_data.items() 
                                if k not in ['raw_content', 'clean_content']}
                json_data['files'].append(json_file_data)
            
            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved JSON data: {json_filepath}")
            return json_filepath
            
        except Exception as e:
            self.logger.error(f"Error saving JSON data: {e}")
            return ""
    
    def load_all(self, transformed_data: List[Dict[str, Any]], 
                 save_sections: bool = False, 
                 save_json: bool = True) -> Dict[str, List[str]]:
        """
        Load all transformed markdown data into various output formats.
        
        Args:
            transformed_data (List[Dict[str, Any]]): List of transformed file data
            save_sections (bool): Whether to save sections as separate files
            save_json (bool): Whether to save data as JSON
            
        Returns:
            Dict[str, List[str]]: Dictionary mapping output types to file paths
        """
        saved_files = {
            'text_files': [],
            'section_files': [],
            'summary_file': '',
            'json_file': ''
        }
        
        # Save individual text files
        for file_data in transformed_data:
            text_filepath = self.save_as_text_file(file_data)
            if text_filepath:
                saved_files['text_files'].append(text_filepath)
            
            # Save sections if requested
            if save_sections:
                section_files = self.save_sections_as_separate_files(file_data)
                saved_files['section_files'].extend(section_files)
        
        # Save summary
        summary_filepath = self.save_metadata_summary(transformed_data)
        if summary_filepath:
            saved_files['summary_file'] = summary_filepath
        
        # Save JSON if requested
        if save_json:
            json_filepath = self.save_as_json(transformed_data)
            if json_filepath:
                saved_files['json_file'] = json_filepath
        
        self.logger.info(f"Successfully loaded {len(transformed_data)} files to {self.output_directory}")
        return saved_files 