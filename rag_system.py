"""
RAG (Retrieval-Augmented Generation) System
Combines vector store, document processing, and LLM for intelligent Q&A
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
from vector_store import VectorStore
from document_processor import DocumentProcessor


class RAGSystem:
    """Complete RAG system for document Q&A"""

    def __init__(self, store_path: str = "./data/rag_store"):
        self.vector_store = VectorStore(store_path=store_path)
        self.doc_processor = DocumentProcessor()
        self.initialized = False

    async def initialize(self):
        """Initialize the RAG system"""
        print("Initializing RAG system...")
        self.vector_store.initialize()
        self.initialized = True
        print("RAG system ready!")

    async def index_document(self, file_path: str) -> Dict[str, Any]:
        """
        Index a single document into the RAG system

        Args:
            file_path: Path to document file

        Returns:
            Status dict with indexing results
        """
        if not self.initialized:
            raise RuntimeError("RAG system not initialized")

        path = Path(file_path)
        if not path.exists():
            return {'error': f'File not found: {file_path}', 'success': False}

        # Process document based on type
        ext = path.suffix.lower()

        if ext == '.pdf':
            doc_data = self.doc_processor.process_pdf(file_path)
        elif ext == '.docx':
            doc_data = self.doc_processor.process_docx(file_path)
        else:
            doc_data = self.doc_processor.process_text_file(file_path)

        if 'error' in doc_data:
            return {'error': doc_data['error'], 'success': False}

        # Chunk the document
        chunks = self.doc_processor.chunk_text(doc_data['text'], chunk_size=500, overlap=50)

        if not chunks:
            return {'error': 'No content extracted from document', 'success': False}

        # Create metadata for each chunk
        metadata_list = []
        for i, chunk in enumerate(chunks):
            meta = {
                'source': file_path,
                'file_name': path.name,
                'chunk_index': i,
                'total_chunks': len(chunks),
                **doc_data.get('metadata', {})
            }
            metadata_list.append(meta)

        # Add to vector store
        self.vector_store.add_documents(chunks, metadata_list)

        return {
            'success': True,
            'file': file_path,
            'chunks_indexed': len(chunks),
            'total_chars': len(doc_data['text']),
            'metadata': doc_data.get('metadata', {})
        }

    async def index_directory(self, directory: str, recursive: bool = True) -> Dict[str, Any]:
        """
        Index all documents in a directory

        Args:
            directory: Path to directory
            recursive: Whether to search recursively

        Returns:
            Summary of indexing results
        """
        if not self.initialized:
            raise RuntimeError("RAG system not initialized")

        results = {
            'success': 0,
            'failed': 0,
            'total_chunks': 0,
            'files': []
        }

        # Get all documents
        path = Path(directory)
        if not path.exists() or not path.is_dir():
            return {'error': f'Directory not found: {directory}', 'success': False}

        # Process each file
        extensions = self.doc_processor.supported_extensions
        if recursive:
            files = [f for f in path.rglob('*') if f.suffix.lower() in extensions]
        else:
            files = [f for f in path.glob('*') if f.suffix.lower() in extensions]

        print(f"Found {len(files)} documents to index...")

        for file_path in files:
            result = await self.index_document(str(file_path))
            if result.get('success'):
                results['success'] += 1
                results['total_chunks'] += result.get('chunks_indexed', 0)
            else:
                results['failed'] += 1

            results['files'].append(result)

        return results

    async def query(self, question: str, k: int = 5) -> Dict[str, Any]:
        """
        Query the RAG system

        Args:
            question: User question
            k: Number of relevant chunks to retrieve

        Returns:
            Dict with relevant contexts and metadata
        """
        if not self.initialized:
            raise RuntimeError("RAG system not initialized")

        # Search vector store
        search_results = self.vector_store.search(question, k=k)

        if not search_results:
            return {
                'question': question,
                'contexts': [],
                'answer': 'No relevant documents found in the knowledge base.',
                'sources': []
            }

        # Format contexts
        contexts = []
        sources = set()

        for result in search_results:
            contexts.append({
                'text': result['text'],
                'score': result['score'],
                'source': result['metadata'].get('file_name', 'Unknown'),
                'chunk': result['metadata'].get('chunk_index', 0)
            })
            sources.add(result['metadata'].get('file_name', 'Unknown'))

        return {
            'question': question,
            'contexts': contexts,
            'sources': list(sources),
            'num_results': len(search_results)
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        return {
            'initialized': self.initialized,
            **self.vector_store.get_stats()
        }

    async def clear_index(self):
        """Clear all indexed documents"""
        if self.initialized:
            self.vector_store.clear()
            print("RAG index cleared")


class CodeRAG(RAGSystem):
    """Specialized RAG system for code repositories"""

    def __init__(self, store_path: str = "./data/code_rag_store"):
        super().__init__(store_path)
        # Add code-specific extensions
        self.doc_processor.supported_extensions.update({
            '.tsx', '.jsx', '.ts', '.vue', '.php', '.rb', '.swift',
            '.kt', '.scala', '.sh', '.yml', '.yaml', '.json', '.xml'
        })

    async def analyze_repository(self, repo_path: str) -> Dict[str, Any]:
        """
        Analyze and index entire code repository

        Args:
            repo_path: Path to repository root

        Returns:
            Analysis results with statistics
        """
        # Index all code files
        index_result = await self.index_directory(repo_path, recursive=True)

        # Generate repository summary
        path = Path(repo_path)
        stats = {
            'repository': path.name,
            'path': str(path),
            'files_indexed': index_result.get('success', 0),
            'total_chunks': index_result.get('total_chunks', 0),
            'failed_files': index_result.get('failed', 0)
        }

        # Count by file type
        file_types = {}
        for file_result in index_result.get('files', []):
            if file_result.get('success'):
                file_name = file_result.get('file', '')
                ext = Path(file_name).suffix
                file_types[ext] = file_types.get(ext, 0) + 1

        stats['file_types'] = file_types

        return stats

    async def find_function(self, function_name: str) -> Dict[str, Any]:
        """
        Find function definition in indexed code

        Args:
            function_name: Name of function to find

        Returns:
            Function location and code
        """
        query = f"function {function_name} definition implementation"
        results = await self.query(query, k=3)
        return results

    async def find_similar_code(self, code_snippet: str, k: int = 5) -> Dict[str, Any]:
        """
        Find similar code patterns

        Args:
            code_snippet: Code to find similar patterns for
            k: Number of results

        Returns:
            Similar code chunks
        """
        return await self.query(code_snippet, k=k)
