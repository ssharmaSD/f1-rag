"""
Enhanced document processor for both static and online content
"""
import os
import re
import json
from typing import List, Dict
from pathlib import Path
from datetime import datetime

class EnhancedDocumentProcessor:
    """Processes both static markdown documents and dynamic online content"""
    
    def __init__(self, knowledge_base_path: str, online_content_path: str = "./knowledge_base/online"):
        self.knowledge_base_path = Path(knowledge_base_path)
        self.online_content_path = Path(online_content_path)
        
    def load_all_documents(self) -> List[Dict[str, str]]:
        """Load documents from both static and online sources"""
        documents = []
        
        # Load static markdown documents
        static_docs = self._load_static_documents()
        documents.extend(static_docs)
        
        # Load online articles
        online_docs = self._load_online_documents()
        documents.extend(online_docs)
        
        print(f"Loaded {len(static_docs)} static documents and {len(online_docs)} online documents")
        return documents
    
    def _load_static_documents(self) -> List[Dict[str, str]]:
        """Load static markdown documents"""
        documents = []
        
        for md_file in self.knowledge_base_path.glob("*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract title from first heading
            title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else md_file.stem
            
            # Split content into chunks
            chunks = self._split_into_chunks(content, title, source_type='static')
            
            for i, chunk in enumerate(chunks):
                documents.append({
                    'id': f"static_{md_file.stem}_{i}",
                    'title': title,
                    'content': chunk,
                    'source': str(md_file),
                    'source_type': 'static',
                    'chunk_index': i,
                    'last_updated': datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
                })
                
        return documents
    
    def _load_online_documents(self) -> List[Dict[str, str]]:
        """Load online articles from JSON files"""
        documents = []
        
        if not self.online_content_path.exists():
            return documents
        
        for json_file in self.online_content_path.glob("*_articles.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    articles = json.load(f)
                
                source_name = json_file.stem.replace('_articles', '')
                
                for article in articles:
                    if not article.get('content'):
                        continue
                    
                    # Split article into chunks
                    chunks = self._split_into_chunks(
                        article['content'], 
                        article['title'], 
                        source_type='online',
                        max_chunk_size=800  # Larger chunks for articles
                    )
                    
                    for i, chunk in enumerate(chunks):
                        documents.append({
                            'id': f"online_{source_name}_{hash(article['url'])}_{i}",
                            'title': article['title'],
                            'content': chunk,
                            'source': article['url'],
                            'source_type': 'online',
                            'source_name': source_name,
                            'chunk_index': i,
                            'published': article.get('published', ''),
                            'scraped_at': article.get('scraped_at', ''),
                            'relevance_score': article.get('relevance_score', 0)
                        })
                        
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
                
        return documents
    
    def _split_into_chunks(self, content: str, title: str, source_type: str = 'static', max_chunk_size: int = 500) -> List[str]:
        """Split document into smaller chunks for better retrieval"""
        # Remove markdown headers for static content
        if source_type == 'static':
            content = re.sub(r'^#+ .+$', '', content, flags=re.MULTILINE)
        
        # Clean up content
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
        
        # Ensure we have at least one chunk
        if not chunks:
            chunks = [content[:max_chunk_size]]
            
        return chunks
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for better embedding"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        return text.strip()
    
    def get_document_stats(self) -> Dict:
        """Get statistics about loaded documents"""
        static_docs = self._load_static_documents()
        online_docs = self._load_online_documents()
        
        stats = {
            'total_documents': len(static_docs) + len(online_docs),
            'static_documents': len(static_docs),
            'online_documents': len(online_docs),
            'static_sources': len(set(doc['source'] for doc in static_docs)),
            'online_sources': len(set(doc.get('source_name', '') for doc in online_docs)),
            'total_chunks': sum(len(self._split_into_chunks(doc['content'], doc['title'])) for doc in static_docs + online_docs)
        }
        
        return stats
    
    def update_online_content(self, scraper=None) -> int:
        """Update online content using ethical web scraper"""
        print("Updating online content using ethical scraping...")
        
        # Use ethical scraper if no scraper provided
        if scraper is None:
            from .ethical_web_scraper import EthicalF1WebScraper
            scraper = EthicalF1WebScraper()
        
        # Fetch content ethically (RSS feeds + APIs only)
        articles = scraper.fetch_all_ethical_content()
        
        # Save articles with ethical compliance metadata
        scraper.save_articles(articles)
        
        print(f"Updated with {len(articles)} new articles (ethically sourced)")
        return len(articles)
