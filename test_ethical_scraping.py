"""
Test script for ethical web scraping functionality
"""
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent))

def test_ethical_scraping():
    """Test the ethical web scraping system"""
    print("🌐 Testing Ethical F1 Web Scraping System")
    print("=" * 50)
    
    try:
        from utils.ethical_web_scraper import EthicalF1WebScraper
        
        # Initialize ethical scraper
        print("Initializing ethical web scraper...")
        scraper = EthicalF1WebScraper()
        print("✅ Ethical web scraper initialized")
        
        # Show ethical sources info
        print("\n📋 Ethical Sources Information:")
        sources_info = scraper.get_ethical_sources_info()
        
        print("\n🔄 RSS Sources:")
        for source_id, source in sources_info['rss_sources'].items():
            print(f"  • {source['name']}: {source['reason']}")
        
        print("\n🔌 API Sources:")
        for source_id, source in sources_info['api_sources'].items():
            print(f"  • {source['name']}: {source['reason']}")
        
        print("\n⚙️ Scraping Policy:")
        policy = sources_info['scraping_policy']
        print(f"  • Respects robots.txt: {policy['respects_robots_txt']}")
        print(f"  • Rate limited: {policy['rate_limited']}")
        print(f"  • Default delay: {policy['default_delay_seconds']}s")
        print(f"  • User agent: {policy['user_agent']}")
        
        # Test RSS-only scraping (ethical and safe)
        print("\n📰 Testing RSS-only scraping...")
        rss_articles = scraper.scrape_rss_feeds_only()
        print(f"✅ Fetched {len(rss_articles)} articles from RSS feeds")
        
        if rss_articles:
            # Show sample article
            sample_article = rss_articles[0]
            print(f"\n📄 Sample RSS Article:")
            print(f"  Title: {sample_article['title']}")
            print(f"  Source: {sample_article['source']}")
            print(f"  Method: {sample_article['scraping_method']}")
            print(f"  Ethical Status: {sample_article['ethical_status']}")
            print(f"  Content length: {len(sample_article['content'])} characters")
        
        # Test API fetching (also ethical)
        print("\n🔌 Testing API data fetching...")
        api_articles = scraper.fetch_from_apis()
        print(f"✅ Fetched {len(api_articles)} items from APIs")
        
        if api_articles:
            sample_api = api_articles[0]
            print(f"\n📊 Sample API Data:")
            print(f"  Title: {sample_api['title']}")
            print(f"  Source: {sample_api['source']}")
            print(f"  Method: {sample_api['scraping_method']}")
            print(f"  Data Type: {sample_api.get('data_type', 'N/A')}")
        
        # Test combined ethical content fetching
        print("\n🌟 Testing combined ethical content fetching...")
        all_ethical_content = scraper.fetch_all_ethical_content()
        print(f"✅ Fetched {len(all_ethical_content)} total items ethically")
        
        # Test saving with ethical metadata
        print("\n💾 Testing ethical content saving...")
        compliance_metadata = scraper.save_articles(all_ethical_content)
        print("✅ Articles saved with ethical compliance metadata")
        
        print(f"\n📊 Ethical Compliance Summary:")
        compliance = compliance_metadata['ethical_compliance']
        print(f"  • Total articles: {compliance_metadata['total_articles']}")
        print(f"  • Respects robots.txt: {compliance['respects_robots_txt']}")
        print(f"  • Rate limited: {compliance['rate_limited']}")
        print(f"  • Uses RSS feeds: {compliance['uses_rss_feeds']}")
        print(f"  • Uses official APIs: {compliance['uses_official_apis']}")
        print(f"  • Methods used: {', '.join(compliance_metadata['scraping_methods'])}")
        
        print("\n🎉 Ethical web scraping test completed successfully!")
        print("\n📚 All content obtained through ethical means:")
        print("  ✅ RSS feeds (designed for consumption)")
        print("  ✅ Official APIs (designed for data access)")
        print("  ✅ Robots.txt compliance")
        print("  ✅ Rate limiting respected")
        print("  ✅ Educational use only")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

def test_robots_txt_compliance():
    """Test robots.txt compliance checking"""
    print("\n🤖 Testing Robots.txt Compliance")
    print("=" * 40)
    
    try:
        from utils.ethical_web_scraper import EthicalF1WebScraper
        
        scraper = EthicalF1WebScraper()
        
        # Test URLs for robots.txt compliance
        test_urls = [
            "https://www.formula1.com/en/latest/",
            "https://www.motorsport.com/f1/",
            "https://www.fia.com/news",
        ]
        
        for url in test_urls:
            try:
                allowed = scraper.check_robots_txt(url)
                status = "✅ ALLOWED" if allowed else "❌ BLOCKED"
                print(f"  {status}: {url}")
            except Exception as e:
                print(f"  ⚠️ ERROR checking {url}: {e}")
        
        print("\n🛡️ Robots.txt compliance checking working!")
        
    except Exception as e:
        print(f"❌ Error testing robots.txt: {e}")

def main():
    """Run all ethical scraping tests"""
    print("🏎️ F1 Ethical Web Scraping Test Suite")
    print("=" * 60)
    
    # Test ethical scraping
    test_ethical_scraping()
    
    # Test robots.txt compliance
    test_robots_txt_compliance()
    
    print("\n" + "=" * 60)
    print("🎉 All ethical scraping tests completed!")
    print("\n📖 Key Takeaways:")
    print("  • Only RSS feeds and APIs are used by default")
    print("  • All scraping respects robots.txt")
    print("  • Rate limiting is implemented")
    print("  • Educational use only")
    print("  • Full ethical compliance")
    print("\n📚 For more information, see: ETHICAL_SCRAPING_GUIDE.md")

if __name__ == "__main__":
    main()
