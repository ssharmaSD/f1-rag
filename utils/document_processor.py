"""
Document processing utilities for F1 knowledge base
"""
import os
import re
from typing import List, Dict
from pathlib import Path

class DocumentProcessor:
    """Processes markdown documents for RAG system"""
    
    def __init__(self, knowledge_base_path: str):
        self.knowledge_base_path = Path(knowledge_base_path)
        
    def load_documents(self) -> List[Dict[str, str]]:
        """Load all markdown documents from knowledge base"""
        documents = []
        
        for md_file in self.knowledge_base_path.glob("*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract title from first heading
            title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else md_file.stem
            
            # Split content into chunks
            chunks = self._split_into_chunks(content, title)
            
            for i, chunk in enumerate(chunks):
                documents.append({
                    'id': f"{md_file.stem}_{i}",
                    'title': title,
                    'content': chunk,
                    'source': str(md_file),
                    'chunk_index': i
                })
                
        return documents
    
    def _split_into_chunks(self, content: str, title: str, max_chunk_size: int = 500) -> List[str]:
        """Split document into smaller chunks for better retrieval"""
        # Remove markdown headers and clean up
        content = re.sub(r'^#+ .+$', '', content, flags=re.MULTILINE)
        content = re.sub(r'\n+', '\n', content).strip()
        
        # Split by paragraphs first
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed max size, start new chunk
            if len(current_chunk) + len(paragraph) > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for better embedding"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        return text.strip()
