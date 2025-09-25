"""
Ethical web scraping system for F1 knowledge base that respects robots.txt and rate limits
"""
import requests
from bs4 import BeautifulSoup
import feedparser
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse, urlencode
from urllib.robotparser import RobotFileParser
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EthicalF1WebScraper:
    """Ethical web scraper that respects robots.txt and rate limits"""
    
    def __init__(self, cache_dir: str = "./data/web_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Respectful headers
        self.headers = {
            'User-Agent': 'F1-Educational-Bot/1.0 (Educational use only; respects robots.txt)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        # Rate limiting: minimum delay between requests per domain
        self.domain_delays = {}
        self.last_request_time = {}
        self.default_delay = 2  # 2 seconds between requests
        
        # Robots.txt cache
        self.robots_cache = {}
        
        # Ethical F1 sources that allow scraping or provide RSS feeds
        self.ethical_f1_sources = {
            'f1_official_rss': {
                'name': 'Formula 1 Official RSS',
                'type': 'rss_only',  # Only use RSS feeds, no direct scraping
                'feeds': [
                    'https://www.formula1.com/en/latest/all.xml'  # Official RSS feed
                ],
                'allowed': True,
                'reason': 'Official RSS feed provided for public consumption'
            },
            'motorsport_rss': {
                'name': 'Motorsport.com RSS',
                'type': 'rss_only',
                'feeds': [
                    'https://www.motorsport.com/rss/f1/news/'
                ],
                'allowed': True,
                'reason': 'RSS feeds are provided for public consumption'
            },
            'fia_official': {
                'name': 'FIA Official',
                'type': 'api_or_rss',
                'base_url': 'https://www.fia.com',
                'feeds': [
                    'https://www.fia.com/rss/news'
                ],
                'allowed': True,
                'reason': 'Official governing body, RSS feeds available'
            },
            # Note: We avoid direct scraping of news sites without explicit permission
        }
        
        # Alternative: Use official APIs and RSS feeds only
        self.api_sources = {
            'ergast_api': {
                'name': 'Ergast F1 API',
                'base_url': 'https://ergast.com/api/f1',
                'type': 'api',
                'allowed': True,
                'reason': 'Free API specifically designed for F1 data access',
                'endpoints': {
                    'current_season': '/current.json',
                    'drivers': '/current/drivers.json',
                    'constructors': '/current/constructors.json',
                    'circuits': '/current/circuits.json'
                }
            }
        }
    
    def check_robots_txt(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt"""
        try:
            parsed_url = urlparse(url)
            domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # Check cache first
            if domain in self.robots_cache:
                rp = self.robots_cache[domain]
            else:
                # Fetch and parse robots.txt
                rp = RobotFileParser()
                rp.set_url(f"{domain}/robots.txt")
                try:
                    rp.read()
                    self.robots_cache[domain] = rp
                except Exception as e:
                    logger.warning(f"Could not fetch robots.txt for {domain}: {e}")
                    # If we can't fetch robots.txt, be conservative and assume not allowed
                    return False
            
            # Check if our user agent can fetch this URL
            return rp.can_fetch(self.headers['User-Agent'], url)
            
        except Exception as e:
            logger.error(f"Error checking robots.txt for {url}: {e}")
            return False
    
    def respect_rate_limit(self, domain: str):
        """Implement respectful rate limiting per domain"""
        now = time.time()
        
        if domain in self.last_request_time:
            time_since_last = now - self.last_request_time[domain]
            delay = self.domain_delays.get(domain, self.default_delay)
            
            if time_since_last < delay:
                sleep_time = delay - time_since_last
                logger.info(f"Rate limiting: waiting {sleep_time:.1f}s for {domain}")
                time.sleep(sleep_time)
        
        self.last_request_time[domain] = time.time()
    
    def scrape_rss_feeds_only(self) -> List[Dict]:
        """Scrape only from RSS feeds (ethical and intended for consumption)"""
        articles = []
        
        for source_id, source_info in self.ethical_f1_sources.items():
            if not source_info['allowed']:
                continue
                
            logger.info(f"Fetching RSS feeds from {source_info['name']}")
            
            for feed_url in source_info.get('feeds', []):
                try:
                    # RSS feeds are intended for consumption, so this is ethical
                    domain = urlparse(feed_url).netloc
                    self.respect_rate_limit(domain)
                    
                    logger.info(f"Fetching RSS feed: {feed_url}")
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries[:10]:  # Limit to recent articles
                        article_data = {
                            'title': entry.get('title', ''),
                            'url': entry.get('link', ''),
                            'summary': entry.get('summary', ''),
                            'published': entry.get('published', ''),
                            'source': source_info['name'],
                            'source_id': source_id,
                            'content': entry.get('summary', ''),  # Use summary for RSS
                            'scraped_at': datetime.now().isoformat(),
                            'scraping_method': 'rss_feed',
                            'ethical_status': 'approved'
                        }
                        
                        articles.append(article_data)
                        
                except Exception as e:
                    logger.error(f"Error fetching RSS feed {feed_url}: {e}")
        
        return articles
    
    def fetch_from_apis(self) -> List[Dict]:
        """Fetch data from official APIs"""
        api_data = []
        
        for source_id, source_info in self.api_sources.items():
            if not source_info['allowed']:
                continue
                
            logger.info(f"Fetching from API: {source_info['name']}")
            
            try:
                base_url = source_info['base_url']
                domain = urlparse(base_url).netloc
                self.respect_rate_limit(domain)
                
                # Fetch current season data
                for endpoint_name, endpoint_path in source_info['endpoints'].items():
                    try:
                        url = f"{base_url}{endpoint_path}"
                        logger.info(f"Fetching: {url}")
                        
                        response = requests.get(url, headers=self.headers, timeout=10)
                        response.raise_for_status()
                        
                        data = response.json()
                        
                        # Convert API data to article format
                        article_data = {
                            'title': f"F1 {endpoint_name.replace('_', ' ').title()} - {datetime.now().strftime('%Y-%m-%d')}",
                            'url': url,
                            'summary': f"Official F1 data from {source_info['name']}",
                            'published': datetime.now().isoformat(),
                            'source': source_info['name'],
                            'source_id': f"{source_id}_{endpoint_name}",
                            'content': json.dumps(data, indent=2),  # Store JSON as content
                            'scraped_at': datetime.now().isoformat(),
                            'scraping_method': 'api',
                            'ethical_status': 'approved',
                            'data_type': 'structured_data'
                        }
                        
                        api_data.append(article_data)
                        
                    except Exception as e:
                        logger.error(f"Error fetching {endpoint_name}: {e}")
                        
            except Exception as e:
                logger.error(f"Error with API {source_id}: {e}")
        
        return api_data
    
    def scrape_with_permission(self, urls: List[str]) -> List[Dict]:
        """Only scrape URLs that explicitly allow it via robots.txt"""
        articles = []
        
        for url in urls:
            try:
                # Check robots.txt first
                if not self.check_robots_txt(url):
                    logger.warning(f"Skipping {url} - not allowed by robots.txt")
                    continue
                
                domain = urlparse(url).netloc
                self.respect_rate_limit(domain)
                
                logger.info(f"Scraping (with permission): {url}")
                
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract article content
                title = soup.find('title')
                title_text = title.get_text() if title else 'Untitled'
                
                # Try to find main content
                content_selectors = ['article', '.article-content', '.post-content', 'main']
                content = ''
                
                for selector in content_selectors:
                    content_elem = soup.select_one(selector)
                    if content_elem:
                        content = content_elem.get_text(strip=True)
                        break
                
                if not content:
                    content = soup.get_text(strip=True)
                
                article_data = {
                    'title': title_text,
                    'url': url,
                    'summary': content[:500] + '...' if len(content) > 500 else content,
                    'published': datetime.now().isoformat(),
                    'source': domain,
                    'source_id': 'manual_scrape',
                    'content': content,
                    'scraped_at': datetime.now().isoformat(),
                    'scraping_method': 'ethical_scraping',
                    'ethical_status': 'robots_txt_approved'
                }
                
                articles.append(article_data)
                
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
        
        return articles
    
    def get_ethical_sources_info(self) -> Dict:
        """Get information about ethical sources"""
        return {
            'rss_sources': {k: v for k, v in self.ethical_f1_sources.items() if v['allowed']},
            'api_sources': {k: v for k, v in self.api_sources.items() if v['allowed']},
            'scraping_policy': {
                'respects_robots_txt': True,
                'rate_limited': True,
                'default_delay_seconds': self.default_delay,
                'user_agent': self.headers['User-Agent']
            }
        }
    
    def fetch_all_ethical_content(self) -> List[Dict]:
        """Fetch content from all ethical sources"""
        all_articles = []
        
        logger.info("Starting ethical content fetching...")
        
        # 1. Fetch from RSS feeds
        logger.info("Fetching from RSS feeds...")
        rss_articles = self.scrape_rss_feeds_only()
        all_articles.extend(rss_articles)
        logger.info(f"Fetched {len(rss_articles)} articles from RSS feeds")
        
        # 2. Fetch from APIs
        logger.info("Fetching from APIs...")
        api_articles = self.fetch_from_apis()
        all_articles.extend(api_articles)
        logger.info(f"Fetched {len(api_articles)} items from APIs")
        
        # 3. Filter for F1 relevance
        filtered_articles = self.filter_f1_content(all_articles)
        
        logger.info(f"Total ethical content fetched: {len(filtered_articles)} articles")
        return filtered_articles
    
    def filter_f1_content(self, articles: List[Dict]) -> List[Dict]:
        """Filter articles for F1 relevance"""
        f1_keywords = [
            'formula 1', 'f1', 'grand prix', 'gp', 'fia', 'fia formula 1',
            'racing', 'race', 'driver', 'team', 'championship', 'circuit',
            'aerodynamics', 'engine', 'power unit', 'hybrid', 'turbo',
            'mercedes', 'ferrari', 'red bull', 'mclaren', 'alpine', 'aston martin',
            'hamilton', 'verstappen', 'leclerc', 'norris', 'alonso', 'russell'
        ]
        
        filtered_articles = []
        
        for article in articles:
            # For API data, always include (it's F1-specific)
            if article.get('scraping_method') == 'api':
                article['relevance_score'] = 10  # High relevance for API data
                filtered_articles.append(article)
                continue
            
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
        """Save articles with ethical metadata"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Group articles by scraping method
        articles_by_method = {}
        for article in articles:
            method = article.get('scraping_method', 'unknown')
            if method not in articles_by_method:
                articles_by_method[method] = []
            articles_by_method[method].append(article)
        
        # Save each method's articles
        for method, method_articles in articles_by_method.items():
            method_file = output_path / f"{method}_articles.json"
            
            with open(method_file, 'w', encoding='utf-8') as f:
                json.dump(method_articles, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(method_articles)} articles from {method} to {method_file}")
        
        # Save ethical compliance metadata
        compliance_metadata = {
            'total_articles': len(articles),
            'scraping_methods': list(articles_by_method.keys()),
            'ethical_compliance': {
                'respects_robots_txt': True,
                'rate_limited': True,
                'uses_rss_feeds': 'rss_feed' in articles_by_method,
                'uses_official_apis': 'api' in articles_by_method,
                'user_agent': self.headers['User-Agent']
            },
            'scraped_at': datetime.now().isoformat(),
            'articles_by_method': {k: len(v) for k, v in articles_by_method.items()}
        }
        
        with open(output_path / 'ethical_compliance.json', 'w') as f:
            json.dump(compliance_metadata, f, indent=2)
        
        logger.info(f"Saved {len(articles)} total articles with ethical compliance metadata")
        return compliance_metadata
