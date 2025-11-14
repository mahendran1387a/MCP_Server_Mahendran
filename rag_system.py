"""
RAG (Retrieval-Augmented Generation) System
Handles document storage, embedding, and retrieval using ChromaDB
"""
import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict
import hashlib
from datetime import datetime


class RAGSystem:
    """RAG system for document storage and retrieval"""

    def __init__(self, persist_directory="./rag_db"):
        """Initialize the RAG system with ChromaDB"""
        self.persist_directory = persist_directory

        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )

        print(f"✓ RAG system initialized with {self.collection.count()} documents")

    def add_document(self, text: str, metadata: Dict = None) -> str:
        """Add a document to the RAG database"""
        if not text.strip():
            raise ValueError("Document text cannot be empty")

        # Generate unique ID based on content hash
        doc_id = hashlib.md5(text.encode()).hexdigest()

        # Prepare metadata
        doc_metadata = {
            "timestamp": datetime.now().isoformat(),
            "length": len(text),
            **(metadata or {})
        }

        # Add to collection
        self.collection.add(
            documents=[text],
            metadatas=[doc_metadata],
            ids=[doc_id]
        )

        return doc_id

    def add_documents_batch(self, documents: List[str], metadatas: List[Dict] = None) -> List[str]:
        """Add multiple documents in batch"""
        if not documents:
            return []

        doc_ids = []
        docs_to_add = []
        metas_to_add = []

        for i, text in enumerate(documents):
            if not text.strip():
                continue

            doc_id = hashlib.md5(text.encode()).hexdigest()
            doc_ids.append(doc_id)
            docs_to_add.append(text)

            metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
            metadata.update({
                "timestamp": datetime.now().isoformat(),
                "length": len(text)
            })
            metas_to_add.append(metadata)

        if docs_to_add:
            self.collection.add(
                documents=docs_to_add,
                metadatas=metas_to_add,
                ids=doc_ids
            )

        return doc_ids

    def query(self, query_text: str, n_results: int = 3) -> Dict:
        """Query the RAG database for relevant documents"""
        if not query_text.strip():
            return {
                "documents": [],
                "metadatas": [],
                "distances": []
            }

        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )

        return {
            "documents": results["documents"][0] if results["documents"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else [],
            "distances": results["distances"][0] if results["distances"] else []
        }

    def get_all_documents(self) -> Dict:
        """Get all documents in the database"""
        results = self.collection.get()
        return {
            "count": len(results["ids"]),
            "documents": results["documents"],
            "metadatas": results["metadatas"],
            "ids": results["ids"]
        }

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID"""
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False

    def clear_database(self) -> bool:
        """Clear all documents from the database"""
        try:
            self.client.delete_collection(name="documents")
            self.collection = self.client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
            return True
        except Exception as e:
            print(f"Error clearing database: {e}")
            return False

    def get_stats(self) -> Dict:
        """Get database statistics"""
        all_docs = self.collection.get()
        return {
            "total_documents": len(all_docs["ids"]),
            "total_characters": sum(len(doc) for doc in all_docs["documents"]),
            "collection_name": "documents"
        }


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks"""
    if not text:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]

        # Try to break at sentence boundary
        if end < text_length:
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)

            if break_point > chunk_size // 2:  # Only break if it's not too early
                chunk = text[start:start + break_point + 1]
                end = start + break_point + 1

        chunks.append(chunk.strip())
        start = end - overlap

    return [c for c in chunks if c]


def process_uploaded_file(file_path: str, filename: str) -> List[str]:
    """Process uploaded file and return chunks"""
    _, ext = os.path.splitext(filename.lower())

    try:
        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

        elif ext == '.pdf':
            # PDF processing
            try:
                import PyPDF2
                text = ""
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            except ImportError:
                raise Exception("PyPDF2 not installed. Install with: pip install PyPDF2")

        elif ext in ['.doc', '.docx']:
            # Word document processing
            try:
                import docx
                doc = docx.Document(file_path)
                text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            except ImportError:
                raise Exception("python-docx not installed. Install with: pip install python-docx")

        elif ext == '.json':
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                text = json.dumps(data, indent=2)

        elif ext == '.md':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

        else:
            # Try to read as plain text
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

        # Split into chunks
        chunks = chunk_text(text, chunk_size=1000, overlap=200)
        return chunks

    except Exception as e:
        raise Exception(f"Error processing file: {str(e)}")


# Global RAG instance
_rag_instance = None

def get_rag_system():
    """Get or create global RAG system instance"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGSystem()
    return _rag_instance
