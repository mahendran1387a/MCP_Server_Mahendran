"""
Vector Store Module - FAISS-based persistent embeddings for RAG
Supports local embeddings using sentence-transformers
"""
import os
import pickle
from typing import List, Dict, Any, Optional
import numpy as np
from pathlib import Path


class VectorStore:
    """Local vector store using FAISS for semantic search and RAG"""

    def __init__(self, store_path: str = "./data/vector_store",
                 model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize vector store

        Args:
            store_path: Path to store vector database
            model_name: Local sentence-transformer model name
        """
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)
        self.model_name = model_name

        # Lazy imports for optional dependencies
        self.faiss = None
        self.model = None
        self.index = None
        self.documents = []
        self.metadata = []

    def initialize(self):
        """Initialize FAISS and embedding model"""
        try:
            import faiss
            from sentence_transformers import SentenceTransformer

            self.faiss = faiss
            print(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)

            # Load existing index if available
            index_path = self.store_path / "faiss.index"
            docs_path = self.store_path / "documents.pkl"
            meta_path = self.store_path / "metadata.pkl"

            if index_path.exists() and docs_path.exists():
                print("Loading existing vector store...")
                self.index = faiss.read_index(str(index_path))
                with open(docs_path, 'rb') as f:
                    self.documents = pickle.load(f)
                with open(meta_path, 'rb') as f:
                    self.metadata = pickle.load(f)
                print(f"Loaded {len(self.documents)} documents from store")
            else:
                print("Creating new vector store...")
                # Create new index (L2 distance)
                dimension = self.model.get_sentence_embedding_dimension()
                self.index = faiss.IndexFlatL2(dimension)

        except ImportError as e:
            raise ImportError(f"Required dependencies not installed: {e}")

    def add_documents(self, texts: List[str], metadata: Optional[List[Dict]] = None):
        """
        Add documents to vector store

        Args:
            texts: List of text documents to add
            metadata: Optional metadata for each document
        """
        if not self.model or self.index is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first")

        print(f"Encoding {len(texts)} documents...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        embeddings = np.array(embeddings).astype('float32')

        # Add to FAISS index
        self.index.add(embeddings)

        # Store documents and metadata
        self.documents.extend(texts)
        if metadata:
            self.metadata.extend(metadata)
        else:
            self.metadata.extend([{} for _ in texts])

        print(f"Added {len(texts)} documents. Total: {len(self.documents)}")

        # Auto-save
        self.save()

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of dicts with 'text', 'score', and 'metadata'
        """
        if not self.model or self.index is None:
            raise RuntimeError("Vector store not initialized")

        if len(self.documents) == 0:
            return []

        # Encode query
        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')

        # Search
        k = min(k, len(self.documents))
        distances, indices = self.index.search(query_embedding, k)

        # Format results
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.documents):
                results.append({
                    'text': self.documents[idx],
                    'score': float(dist),
                    'metadata': self.metadata[idx],
                    'rank': i + 1
                })

        return results

    def save(self):
        """Save vector store to disk"""
        if self.index is None:
            return

        index_path = self.store_path / "faiss.index"
        docs_path = self.store_path / "documents.pkl"
        meta_path = self.store_path / "metadata.pkl"

        self.faiss.write_index(self.index, str(index_path))
        with open(docs_path, 'wb') as f:
            pickle.dump(self.documents, f)
        with open(meta_path, 'wb') as f:
            pickle.dump(self.metadata, f)

        print(f"Vector store saved to {self.store_path}")

    def clear(self):
        """Clear all documents from store"""
        if self.model:
            dimension = self.model.get_sentence_embedding_dimension()
            self.index = self.faiss.IndexFlatL2(dimension)
        self.documents = []
        self.metadata = []
        self.save()
        print("Vector store cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        return {
            'total_documents': len(self.documents),
            'model': self.model_name,
            'store_path': str(self.store_path),
            'index_size': self.index.ntotal if self.index else 0
        }
