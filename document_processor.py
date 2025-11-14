"""
Document Processing Module
Handles PDF, DOCX, TXT, Markdown, and code files
Extracts text, generates summaries, and indexes for RAG
"""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import re


class DocumentProcessor:
    """Process various document types for RAG and analysis"""

    def __init__(self):
        self.supported_extensions = {
            '.pdf', '.txt', '.md', '.py', '.js', '.java', '.cpp',
            '.c', '.h', '.cs', '.rb', '.go', '.rs', '.docx', '.html'
        }

    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract text from PDF

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dict with 'text', 'pages', 'metadata'
        """
        try:
            import pypdf
            from pypdf import PdfReader

            reader = PdfReader(pdf_path)
            pages = []
            full_text = []

            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                pages.append({
                    'page_number': i + 1,
                    'text': page_text,
                    'char_count': len(page_text)
                })
                full_text.append(page_text)

            metadata = {
                'num_pages': len(reader.pages),
                'file_name': Path(pdf_path).name,
                'file_path': pdf_path,
                'file_size': os.path.getsize(pdf_path)
            }

            # Try to get PDF metadata
            if reader.metadata:
                metadata.update({
                    'title': reader.metadata.get('/Title', 'Unknown'),
                    'author': reader.metadata.get('/Author', 'Unknown'),
                    'subject': reader.metadata.get('/Subject', ''),
                    'creator': reader.metadata.get('/Creator', '')
                })

            return {
                'text': '\n\n'.join(full_text),
                'pages': pages,
                'metadata': metadata,
                'type': 'pdf'
            }

        except Exception as e:
            return {
                'error': f"Failed to process PDF: {str(e)}",
                'text': '',
                'pages': [],
                'metadata': {}
            }

    def process_docx(self, docx_path: str) -> Dict[str, Any]:
        """Extract text from DOCX file"""
        try:
            from docx import Document

            doc = Document(docx_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            text = '\n\n'.join(paragraphs)

            return {
                'text': text,
                'paragraphs': paragraphs,
                'metadata': {
                    'file_name': Path(docx_path).name,
                    'file_path': docx_path,
                    'num_paragraphs': len(paragraphs)
                },
                'type': 'docx'
            }
        except Exception as e:
            return {
                'error': f"Failed to process DOCX: {str(e)}",
                'text': '',
                'paragraphs': [],
                'metadata': {}
            }

    def process_text_file(self, file_path: str) -> Dict[str, Any]:
        """Process plain text, markdown, or code files"""
        try:
            path = Path(file_path)

            # Try to detect encoding
            import chardet
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'

            with open(file_path, 'r', encoding=encoding) as f:
                text = f.read()

            # Detect file type
            file_ext = path.suffix.lower()
            file_type = 'text'
            if file_ext == '.md':
                file_type = 'markdown'
            elif file_ext in {'.py', '.js', '.java', '.cpp', '.c', '.go', '.rs'}:
                file_type = 'code'

            # Extract code structure if it's a code file
            code_info = {}
            if file_type == 'code':
                code_info = self._extract_code_structure(text, file_ext)

            return {
                'text': text,
                'metadata': {
                    'file_name': path.name,
                    'file_path': file_path,
                    'file_type': file_type,
                    'extension': file_ext,
                    'line_count': text.count('\n') + 1,
                    'char_count': len(text),
                    'file_size': os.path.getsize(file_path)
                },
                'code_info': code_info,
                'type': file_type
            }
        except Exception as e:
            return {
                'error': f"Failed to process file: {str(e)}",
                'text': '',
                'metadata': {}
            }

    def _extract_code_structure(self, code: str, extension: str) -> Dict[str, Any]:
        """Extract functions, classes, imports from code"""
        structure = {
            'functions': [],
            'classes': [],
            'imports': []
        }

        if extension == '.py':
            # Python-specific extraction
            import_pattern = r'^(?:from .+ )?import .+$'
            func_pattern = r'^def (\w+)\('
            class_pattern = r'^class (\w+)'

            for line in code.split('\n'):
                line = line.strip()
                if re.match(import_pattern, line):
                    structure['imports'].append(line)
                elif match := re.match(func_pattern, line):
                    structure['functions'].append(match.group(1))
                elif match := re.match(class_pattern, line):
                    structure['classes'].append(match.group(1))

        elif extension == '.js':
            # JavaScript-specific extraction
            func_pattern = r'(?:function|const|let|var)\s+(\w+)\s*=?\s*(?:function|\()'
            class_pattern = r'class\s+(\w+)'

            for line in code.split('\n'):
                if match := re.search(func_pattern, line):
                    structure['functions'].append(match.group(1))
                elif match := re.search(class_pattern, line):
                    structure['classes'].append(match.group(1))

        return structure

    def chunk_text(self, text: str, chunk_size: int = 500,
                   overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks for RAG

        Args:
            text: Text to chunk
            chunk_size: Target size of each chunk (in characters)
            overlap: Number of characters to overlap between chunks

        Returns:
            List of text chunks
        """
        if not text:
            return []

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size

            # Try to break at sentence boundary
            if end < text_length:
                # Look for sentence endings
                sentence_end = max(
                    text.rfind('. ', start, end),
                    text.rfind('! ', start, end),
                    text.rfind('? ', start, end),
                    text.rfind('\n\n', start, end)
                )
                if sentence_end != -1 and sentence_end > start:
                    end = sentence_end + 1

            chunks.append(text[start:end].strip())
            start = end - overlap

        return chunks

    def summarize_document(self, text: str, max_length: int = 500) -> str:
        """
        Create a simple extractive summary

        Args:
            text: Text to summarize
            max_length: Maximum summary length

        Returns:
            Summary text
        """
        # Simple extractive summary: take first few sentences
        sentences = re.split(r'[.!?]+', text)
        summary = []
        current_length = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if current_length + len(sentence) > max_length:
                break

            summary.append(sentence)
            current_length += len(sentence)

        return '. '.join(summary) + '.'

    def process_directory(self, directory: str,
                          recursive: bool = True) -> List[Dict[str, Any]]:
        """
        Process all supported documents in a directory

        Args:
            directory: Path to directory
            recursive: Whether to search recursively

        Returns:
            List of processed documents
        """
        results = []
        path = Path(directory)

        if not path.exists() or not path.is_dir():
            return [{'error': f'Directory not found: {directory}'}]

        # Get all files
        if recursive:
            files = path.rglob('*')
        else:
            files = path.glob('*')

        for file_path in files:
            if not file_path.is_file():
                continue

            ext = file_path.suffix.lower()
            if ext not in self.supported_extensions:
                continue

            # Process based on file type
            if ext == '.pdf':
                result = self.process_pdf(str(file_path))
            elif ext == '.docx':
                result = self.process_docx(str(file_path))
            else:
                result = self.process_text_file(str(file_path))

            results.append(result)

        return results
