"""
Vector store implementation using ChromaDB for F1 knowledge base
"""
import chromadb
from chromadb.config import Settings
import numpy as np
from typing import List, Dict, Tuple
import os
from sentence_transformers import SentenceTransformer

class F1VectorStore:
    """Vector store for F1 knowledge base using ChromaDB"""
    
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        self.persist_directory = persist_directory
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="f1_knowledge",
            metadata={"description": "F1 racing knowledge base"}
        )
    
    def add_documents(self, documents: List[Dict[str, str]]):
        """Add documents to vector store"""
        ids = []
        texts = []
        metadatas = []
        
        for doc in documents:
            ids.append(doc['id'])
            texts.append(doc['content'])
            metadatas.append({
                'title': doc['title'],
                'source': doc['source'],
                'chunk_index': doc['chunk_index']
            })
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts).tolist()
        
        # Add to collection
        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        print(f"Added {len(documents)} documents to vector store")
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, str]]:
        """Search for relevant documents"""
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()[0]
        
        # Search collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                'content': results['documents'][0][i],
                'title': results['metadatas'][0][i]['title'],
                'source': results['metadatas'][0][i]['source'],
                'chunk_index': results['metadatas'][0][i]['chunk_index'],
                'similarity': 1 - results['distances'][0][i]  # Convert distance to similarity
            })
        
        return formatted_results
    
    def get_collection_info(self) -> Dict:
        """Get information about the collection"""
        count = self.collection.count()
        return {
            'document_count': count,
            'collection_name': 'f1_knowledge',
            'embedding_model': 'all-MiniLM-L6-v2'
        }
    
    def clear_collection(self):
        """Clear all documents from collection"""
        # Delete and recreate collection
        self.client.delete_collection("f1_knowledge")
        self.collection = self.client.create_collection(
            name="f1_knowledge",
            metadata={"description": "F1 racing knowledge base"}
        )
        print("Collection cleared")
