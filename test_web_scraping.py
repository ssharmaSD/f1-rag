"""
Test script for web scraping functionality
"""
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent))

def test_web_scraping():
    """Test the web scraping system"""
    print("🌐 Testing F1 Web Scraping System")
    print("=" * 50)
    
    try:
        from utils.web_scraper import F1WebScraper
        
        # Initialize scraper
        print("Initializing web scraper...")
        scraper = F1WebScraper()
        print("✅ Web scraper initialized")
        
        # Test RSS feed scraping
        print("\n📰 Testing RSS feed scraping...")
        articles = scraper.scrape_rss_feeds(max_articles=10)
        print(f"✅ Scraped {len(articles)} articles from RSS feeds")
        
        if articles:
            # Show sample article
            sample_article = articles[0]
            print(f"\n📄 Sample Article:")
            print(f"Title: {sample_article['title']}")
            print(f"Source: {sample_article['source']}")
            print(f"URL: {sample_article['url']}")
            print(f"Content length: {len(sample_article['content'])} characters")
        
        # Test F1 filtering
        print("\n🔍 Testing F1 content filtering...")
        filtered_articles = scraper.filter_f1_content(articles)
        print(f"✅ Filtered to {len(filtered_articles)} F1-relevant articles")
        
        if filtered_articles:
            print(f"Average relevance score: {sum(a['relevance_score'] for a in filtered_articles) / len(filtered_articles):.2f}")
        
        # Test saving articles
        print("\n💾 Testing article saving...")
        scraper.save_articles(filtered_articles)
        print("✅ Articles saved successfully")
        
        # Test stats
        print("\n📊 Scraping statistics:")
        stats = scraper.get_scraping_stats()
        print(f"Cached articles: {stats['cached_articles']}")
        print(f"Online articles: {stats['online_articles']}")
        print(f"Sources: {len(stats['sources'])}")
        
        print("\n🎉 Web scraping test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

def test_enhanced_rag():
    """Test the enhanced RAG system with online content"""
    print("\n🧠 Testing Enhanced RAG System")
    print("=" * 50)
    
    try:
        from utils.rag_system import F1RAGSystem
        
        # Initialize RAG system
        print("Initializing enhanced RAG system...")
        rag = F1RAGSystem()
        print("✅ Enhanced RAG system initialized")
        
        # Test document loading
        print("\n📚 Testing document loading...")
        stats = rag.get_knowledge_base_stats()
        if stats:
            print(f"Total documents: {stats['documents']['total_documents']}")
            print(f"Static documents: {stats['documents']['static_documents']}")
            print(f"Online documents: {stats['documents']['online_documents']}")
            print(f"Total chunks: {stats['documents']['total_chunks']}")
        
        # Test search with source info
        print("\n🔍 Testing search with source information...")
        results = rag.search_with_source_info("What is Formula 1?", n_results=3)
        
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Title: {result['title']}")
            print(f"Source Type: {result['source_type']}")
            print(f"Similarity: {result['similarity']:.3f}")
            print(f"Content preview: {result['content'][:100]}...")
        
        # Test chat functionality
        print("\n💬 Testing chat functionality...")
        response = rag.chat("What are the latest F1 rules?")
        print(f"Response: {response[:200]}...")
        
        print("\n🎉 Enhanced RAG test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during RAG testing: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests"""
    print("🏎️ F1 Web Scraping & Enhanced RAG Test Suite")
    print("=" * 60)
    
    # Test web scraping
    test_web_scraping()
    
    # Test enhanced RAG
    test_enhanced_rag()
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed!")
    print("\nTo run the admin interface:")
    print("  streamlit run admin_app.py")
    print("\nTo run the main chatbot:")
    print("  streamlit run app.py")

if __name__ == "__main__":
    main()
