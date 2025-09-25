"""
Web scraping and document ingestion system for F1 knowledge base
"""
import requests
from bs4 import BeautifulSoup
import feedparser
from newspaper import Article
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import time
import re
from urllib.parse import urljoin, urlparse

class F1WebScraper:
    """Web scraper for F1-related content"""
    
    def __init__(self, cache_dir: str = "./data/web_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # F1-related sources
        self.f1_sources = {
            'official_f1': {
                'name': 'Formula 1 Official',
                'base_url': 'https://www.formula1.com',
                'rss_feeds': [
                    'https://www.formula1.com/en/latest/all.rss'
                ],
                'scrape_patterns': [
                    '/en/latest/',
                    '/en/news/',
                    '/en/racing/'
                ]
            },
            'motorsport': {
                'name': 'Motorsport.com',
                'base_url': 'https://www.motorsport.com',
                'rss_feeds': [
                    'https://www.motorsport.com/f1/rss/'
                ],
                'scrape_patterns': [
                    '/f1/news/',
                    '/f1/analysis/',
                    '/f1/technical/'
                ]
            },
            'autosport': {
                'name': 'Autosport',
                'base_url': 'https://www.autosport.com',
                'rss_feeds': [
                    'https://www.autosport.com/f1/rss/'
                ],
                'scrape_patterns': [
                    '/f1/news/',
                    '/f1/analysis/',
                    '/f1/technical/'
                ]
            },
            'f1_technical': {
                'name': 'F1 Technical',
                'base_url': 'https://www.f1technical.net',
                'rss_feeds': [
                    'https://www.f1technical.net/rss.php'
                ],
                'scrape_patterns': [
                    '/news/',
                    '/articles/',
                    '/features/'
                ]
            }
        }
    
    def scrape_rss_feeds(self, max_articles: int = 50) -> List[Dict]:
        """Scrape articles from RSS feeds"""
        articles = []
        
        for source_id, source_info in self.f1_sources.items():
            print(f"Scraping RSS feeds from {source_info['name']}...")
            
            for rss_url in source_info['rss_feeds']:
                try:
                    feed = feedparser.parse(rss_url)
                    
                    for entry in feed.entries[:max_articles // len(self.f1_sources)]:
                        article_data = {
                            'title': entry.get('title', ''),
                            'url': entry.get('link', ''),
                            'summary': entry.get('summary', ''),
                            'published': entry.get('published', ''),
                            'source': source_info['name'],
                            'source_id': source_id,
                            'content': '',
                            'scraped_at': datetime.now().isoformat()
                        }
                        
                        # Try to get full article content
                        try:
                            content = self._scrape_article_content(article_data['url'])
                            article_data['content'] = content
                        except Exception as e:
                            print(f"Could not scrape content from {article_data['url']}: {e}")
                            article_data['content'] = article_data['summary']
                        
                        articles.append(article_data)
                        time.sleep(1)  # Be respectful to servers
                        
                except Exception as e:
                    print(f"Error scraping RSS feed {rss_url}: {e}")
        
        return articles
    
    def _scrape_article_content(self, url: str) -> str:
        """Scrape full article content from URL"""
        try:
            # Check cache first
            cached_content = self._get_cached_content(url)
            if cached_content:
                return cached_content
            
            # Use newspaper3k for article extraction
            article = Article(url)
            article.download()
            article.parse()
            
            content = article.text
            if not content:
                # Fallback to BeautifulSoup
                response = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try to find main content
                content_selectors = [
                    'article',
                    '.article-content',
                    '.post-content',
                    '.entry-content',
                    'main',
                    '.content'
                ]
                
                for selector in content_selectors:
                    content_elem = soup.select_one(selector)
                    if content_elem:
                        content = content_elem.get_text(strip=True)
                        break
                
                if not content:
                    content = soup.get_text(strip=True)
            
            # Cache the content
            self._cache_content(url, content)
            return content
            
        except Exception as e:
            print(f"Error scraping content from {url}: {e}")
            return ""
    
    def _get_cached_content(self, url: str) -> Optional[str]:
        """Get cached content for URL"""
        cache_file = self.cache_dir / f"{hash(url)}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    # Check if cache is less than 24 hours old
                    cached_time = datetime.fromisoformat(data['cached_at'])
                    if datetime.now() - cached_time < timedelta(hours=24):
                        return data['content']
            except Exception:
                pass
        return None
    
    def _cache_content(self, url: str, content: str):
        """Cache content for URL"""
        cache_file = self.cache_dir / f"{hash(url)}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'url': url,
                    'content': content,
                    'cached_at': datetime.now().isoformat()
                }, f)
        except Exception as e:
            print(f"Error caching content: {e}")
    
    def scrape_specific_urls(self, urls: List[str]) -> List[Dict]:
        """Scrape specific URLs"""
        articles = []
        
        for url in urls:
            try:
                print(f"Scraping {url}...")
                
                article = Article(url)
                article.download()
                article.parse()
                
                article_data = {
                    'title': article.title or 'Untitled',
                    'url': url,
                    'summary': article.summary or '',
                    'published': article.publish_date.isoformat() if article.publish_date else '',
                    'source': urlparse(url).netloc,
                    'source_id': 'manual',
                    'content': article.text,
                    'scraped_at': datetime.now().isoformat()
                }
                
                articles.append(article_data)
                time.sleep(1)  # Be respectful
                
            except Exception as e:
                print(f"Error scraping {url}: {e}")
        
        return articles
    
    def filter_f1_content(self, articles: List[Dict]) -> List[Dict]:
        """Filter articles for F1 relevance"""
        f1_keywords = [
            'formula 1', 'f1', 'grand prix', 'gp', 'fia', 'fia formula 1',
            'racing', 'race', 'driver', 'team', 'championship', 'circuit',
            'aerodynamics', 'engine', 'power unit', 'hybrid', 'turbo',
            'mercedes', 'ferrari', 'red bull', 'mclaren', 'alpine',
            'hamilton', 'verstappen', 'leclerc', 'norris', 'alonso'
        ]
        
        filtered_articles = []
        
        for article in articles:
            # Check title and content for F1 relevance
            text_to_check = f"{article['title']} {article['content']}".lower()
            
            relevance_score = sum(1 for keyword in f1_keywords if keyword in text_to_check)
            
            if relevance_score >= 2:  # At least 2 F1 keywords
                article['relevance_score'] = relevance_score
                filtered_articles.append(article)
        
        # Sort by relevance score
        filtered_articles.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return filtered_articles
    
    def save_articles(self, articles: List[Dict], output_dir: str = "./knowledge_base/online"):
        """Save articles to knowledge base"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Group articles by source
        articles_by_source = {}
        for article in articles:
            source = article['source_id']
            if source not in articles_by_source:
                articles_by_source[source] = []
            articles_by_source[source].append(article)
        
        # Save each source's articles
        for source_id, source_articles in articles_by_source.items():
            source_file = output_path / f"{source_id}_articles.json"
            
            with open(source_file, 'w', encoding='utf-8') as f:
                json.dump(source_articles, f, indent=2, ensure_ascii=False)
            
            print(f"Saved {len(source_articles)} articles from {source_id} to {source_file}")
        
        # Save metadata
        metadata = {
            'total_articles': len(articles),
            'sources': list(articles_by_source.keys()),
            'scraped_at': datetime.now().isoformat(),
            'articles_by_source': {k: len(v) for k, v in articles_by_source.items()}
        }
        
        with open(output_path / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Saved {len(articles)} total articles to {output_path}")
    
    def get_scraping_stats(self) -> Dict:
        """Get statistics about scraped content"""
        cache_files = list(self.cache_dir.glob("*.json"))
        online_dir = Path("./knowledge_base/online")
        
        stats = {
            'cached_articles': len(cache_files),
            'online_articles': 0,
            'sources': []
        }
        
        if online_dir.exists():
            for source_file in online_dir.glob("*_articles.json"):
                try:
                    with open(source_file, 'r') as f:
                        articles = json.load(f)
                        stats['online_articles'] += len(articles)
                        stats['sources'].append({
                            'source': source_file.stem.replace('_articles', ''),
                            'count': len(articles)
                        })
                except Exception:
                    pass
        
        return stats
