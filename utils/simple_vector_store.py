"""
Simple vector store implementation using numpy and cosine similarity
"""
import numpy as np
import json
import os
from pathlib import Path
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer

class SimpleVectorStore:
    """Simple vector store using numpy arrays and cosine similarity"""
    
    def __init__(self, persist_directory: str = "./data/simple_vector_db"):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Storage
        self.documents = []
        self.embeddings = None
        self.metadata = []
        
        # Load existing data if available
        self._load_data()
    
    def add_documents(self, documents: List[Dict[str, str]]):
        """Add documents to vector store"""
        new_embeddings = []
        new_metadata = []
        
        for doc in documents:
            # Generate embedding
            embedding = self.embedding_model.encode(doc['content'])
            new_embeddings.append(embedding)
            
            # Store metadata
            new_metadata.append({
                'id': doc['id'],
                'title': doc['title'],
                'source': doc['source'],
                'chunk_index': doc['chunk_index']
            })
            
            # Store document
            self.documents.append(doc['content'])
        
        # Update embeddings array
        if self.embeddings is None:
            self.embeddings = np.array(new_embeddings)
        else:
            self.embeddings = np.vstack([self.embeddings, np.array(new_embeddings)])
        
        # Update metadata
        self.metadata.extend(new_metadata)
        
        # Save data
        self._save_data()
        
        print(f"Added {len(documents)} documents to vector store")
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, str]]:
        """Search for relevant documents"""
        if len(self.documents) == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Calculate cosine similarities
        similarities = np.dot(self.embeddings, query_embedding.T).flatten()
        
        # Get top results
        top_indices = np.argsort(similarities)[::-1][:n_results]
        
        # Format results
        results = []
        for idx in top_indices:
            results.append({
                'content': self.documents[idx],
                'title': self.metadata[idx]['title'],
                'source': self.metadata[idx]['source'],
                'chunk_index': self.metadata[idx]['chunk_index'],
                'similarity': float(similarities[idx])
            })
        
        return results
    
    def get_collection_info(self) -> Dict:
        """Get information about the collection"""
        return {
            'document_count': len(self.documents),
            'collection_name': 'f1_knowledge_simple',
            'embedding_model': 'all-MiniLM-L6-v2'
        }
    
    def clear_collection(self):
        """Clear all documents from collection"""
        self.documents = []
        self.embeddings = None
        self.metadata = []
        self._save_data()
        print("Collection cleared")
    
    def _save_data(self):
        """Save data to disk"""
        data = {
            'documents': self.documents,
            'metadata': self.metadata
        }
        
        # Save documents and metadata
        with open(self.persist_directory / 'data.json', 'w') as f:
            json.dump(data, f)
        
        # Save embeddings
        if self.embeddings is not None:
            np.save(self.persist_directory / 'embeddings.npy', self.embeddings)
    
    def _load_data(self):
        """Load data from disk"""
        data_file = self.persist_directory / 'data.json'
        embeddings_file = self.persist_directory / 'embeddings.npy'
        
        if data_file.exists() and embeddings_file.exists():
            try:
                # Load documents and metadata
                with open(data_file, 'r') as f:
                    data = json.load(f)
                
                self.documents = data['documents']
                self.metadata = data['metadata']
                
                # Load embeddings
                self.embeddings = np.load(embeddings_file)
                
                print(f"Loaded {len(self.documents)} documents from disk")
            except Exception as e:
                print(f"Error loading data: {e}")
                self.documents = []
                self.metadata = []
                self.embeddings = None
