import re
from typing import List, Dict, Any
import logging

class MarkdownTransformer:
    """
    Transforms raw markdown content into clean, structured text data.
    """
    
    def __init__(self):
        """
        Initialize the MarkdownTransformer.
        """
        self.logger = logging.getLogger(__name__)
        
    def clean_markdown_syntax(self, content: str) -> str:
        """
        Remove markdown syntax and formatting from content.
        
        Args:
            content (str): Raw markdown content
            
        Returns:
            str: Clean text content without markdown syntax
        """
        # Remove headers (# ## ### etc.)
        content = re.sub(r'^#{1,6}\s+', '', content, flags=re.MULTILINE)
        
        # Remove bold and italic markers
        content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # Bold
        content = re.sub(r'\*(.*?)\*', r'\1', content)      # Italic
        content = re.sub(r'__(.*?)__', r'\1', content)      # Bold underscore
        content = re.sub(r'_(.*?)_', r'\1', content)        # Italic underscore
        
        # Remove code blocks
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        content = re.sub(r'`([^`]+)`', r'\1', content)      # Inline code
        
        # Remove links but keep text
        content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
        
        # Remove images
        content = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', content)
        
        # Remove horizontal rules
        content = re.sub(r'^[-*_]{3,}$', '', content, flags=re.MULTILINE)
        
        # Remove blockquotes
        content = re.sub(r'^>\s+', '', content, flags=re.MULTILINE)
        
        # Remove list markers
        content = re.sub(r'^[\s]*[-*+]\s+', '', content, flags=re.MULTILINE)
        content = re.sub(r'^[\s]*\d+\.\s+', '', content, flags=re.MULTILINE)
        
        # Clean up extra whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        return content.strip()
    
    def extract_sections(self, content: str) -> List[Dict[str, str]]:
        """
        Extract sections from markdown content based on headers.
        
        Args:
            content (str): Clean markdown content
            
        Returns:
            List[Dict[str, str]]: List of sections with title and content
        """
        sections = []
        lines = content.split('\n')
        current_section = {'title': 'Introduction', 'content': []}
        
        for line in lines:
            # Check if line is a header
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if header_match:
                # Save previous section if it has content
                if current_section['content']:
                    current_section['content'] = '\n'.join(current_section['content']).strip()
                    sections.append(current_section.copy())
                
                # Start new section
                header_level = len(header_match.group(1))
                header_text = header_match.group(2).strip()
                current_section = {
                    'title': header_text,
                    'level': header_level,
                    'content': []
                }
            else:
                current_section['content'].append(line)
        
        # Add the last section
        if current_section['content']:
            current_section['content'] = '\n'.join(current_section['content']).strip()
            sections.append(current_section)
        
        return sections
    
    def extract_metadata(self, content: str) -> Dict[str, Any]:
        """
        Extract metadata from markdown content (frontmatter, etc.).
        
        Args:
            content (str): Raw markdown content
            
        Returns:
            Dict[str, Any]: Extracted metadata
        """
        metadata = {
            'has_frontmatter': False,
            'frontmatter': {},
            'word_count': len(content.split()),
            'line_count': len(content.split('\n')),
            'has_code_blocks': bool(re.search(r'```', content)),
            'has_links': bool(re.search(r'\[.*?\]\(.*?\)', content)),
            'has_images': bool(re.search(r'!\[.*?\]\(.*?\)', content))
        }
        
        # Check for YAML frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if frontmatter_match:
            metadata['has_frontmatter'] = True
            try:
                import yaml
                frontmatter_text = frontmatter_match.group(1)
                metadata['frontmatter'] = yaml.safe_load(frontmatter_text) or {}
            except ImportError:
                self.logger.warning("PyYAML not available, skipping frontmatter parsing")
            except Exception as e:
                self.logger.warning(f"Error parsing frontmatter: {e}")
        
        return metadata
    
    def transform_file(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform a single markdown file's data.
        
        Args:
            file_data (Dict[str, Any]): Raw file data from extractor
            
        Returns:
            Dict[str, Any]: Transformed file data
        """
        if 'error' in file_data:
            return file_data
        
        try:
            raw_content = file_data['content']
            
            # Clean markdown syntax
            clean_content = self.clean_markdown_syntax(raw_content)
            
            # Extract sections
            sections = self.extract_sections(raw_content)
            
            # Extract metadata
            metadata = self.extract_metadata(raw_content)
            
            # Create transformed data
            transformed_data = {
                'file_path': file_data['file_path'],
                'file_name': file_data['file_name'],
                'file_size': file_data['file_size'],
                'modified_time': file_data['modified_time'],
                'raw_content': raw_content,
                'clean_content': clean_content,
                'sections': sections,
                'metadata': metadata,
                'word_count_clean': len(clean_content.split()),
                'section_count': len(sections)
            }
            
            return transformed_data
            
        except Exception as e:
            self.logger.error(f"Error transforming file {file_data['file_path']}: {e}")
            return {
                **file_data,
                'error': str(e),
                'clean_content': '',
                'sections': [],
                'metadata': {}
            }
    
    def transform_all(self, extracted_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform all extracted markdown files.
        
        Args:
            extracted_data (List[Dict[str, Any]]): List of raw file data
            
        Returns:
            List[Dict[str, Any]]: List of transformed file data
        """
        transformed_data = []
        
        for file_data in extracted_data:
            transformed_file = self.transform_file(file_data)
            transformed_data.append(transformed_file)
            
        self.logger.info(f"Successfully transformed {len(transformed_data)} markdown files")
        return transformed_data 