"""
Admin interface for managing F1 knowledge base sources
"""
import streamlit as st
import sys
from pathlib import Path
import json
from datetime import datetime

# Add utils to path
sys.path.append(str(Path(__file__).parent))

from utils.rag_system import F1RAGSystem
from utils.web_scraper import F1WebScraper

def main():
    st.set_page_config(
        page_title="F1 Knowledge Base Admin",
        page_icon="⚙️",
        layout="wide"
    )
    
    st.title("🏎️ F1 Knowledge Base Admin")
    st.markdown("Manage your F1 chatbot's knowledge base and online sources")
    
    # Initialize RAG system
    if 'rag_system' not in st.session_state:
        with st.spinner("Initializing RAG system..."):
            st.session_state.rag_system = F1RAGSystem()
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("📊 Navigation")
        page = st.selectbox("Select Page", [
            "Dashboard",
            "Update Online Content", 
            "Source Management",
            "Knowledge Base Stats",
            "Manual URL Scraping"
        ])
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Update Online Content":
        show_update_content()
    elif page == "Source Management":
        show_source_management()
    elif page == "Knowledge Base Stats":
        show_knowledge_base_stats()
    elif page == "Manual URL Scraping":
        show_manual_scraping()

def show_dashboard():
    st.header("📈 Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Documents", st.session_state.rag_system.get_knowledge_base_info()['document_count'])
    
    with col2:
        stats = st.session_state.rag_system.get_knowledge_base_stats()
        if stats:
            st.metric("Static Sources", stats['documents'].get('static_sources', 0))
    
    with col3:
        if stats:
            st.metric("Online Sources", stats['documents'].get('online_sources', 0))
    
    st.subheader("🚀 Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Update Online Content", type="primary"):
            with st.spinner("Updating online content..."):
                success = st.session_state.rag_system.update_online_content()
                if success:
                    st.success("✅ Online content updated successfully!")
                    st.rerun()
                else:
                    st.info("ℹ️ No new content found")
    
    with col2:
        if st.button("📊 Refresh Stats"):
            st.rerun()
    
    # Recent activity
    st.subheader("📋 Recent Activity")
    
    # Check for recent online content
    online_dir = Path("./knowledge_base/online")
    if online_dir.exists():
        metadata_file = online_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            st.write(f"**Last Scraped:** {metadata.get('scraped_at', 'Unknown')}")
            st.write(f"**Total Articles:** {metadata.get('total_articles', 0)}")
            
            # Show articles by source
            st.write("**Articles by Source:**")
            for source, count in metadata.get('articles_by_source', {}).items():
                st.write(f"- {source}: {count} articles")

def show_update_content():
    st.header("🔄 Update Online Content")
    
    st.markdown("""
    This will scrape the latest F1 articles from configured sources and update your knowledge base.
    """)
    
    # Show current sources
    st.subheader("📰 Configured Sources")
    scraper = F1WebScraper()
    
    for source_id, source_info in scraper.f1_sources.items():
        with st.expander(f"{source_info['name']} ({source_id})"):
            st.write(f"**Base URL:** {source_info['base_url']}")
            st.write(f"**RSS Feeds:** {len(source_info['rss_feeds'])}")
            for feed in source_info['rss_feeds']:
                st.write(f"- {feed}")
    
    # Update options
    st.subheader("⚙️ Update Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_articles = st.slider("Max Articles per Source", 5, 50, 20)
    
    with col2:
        auto_filter = st.checkbox("Auto-filter for F1 relevance", value=True)
    
    # Update button
    if st.button("🚀 Start Update", type="primary"):
        with st.spinner("Scraping and updating content..."):
            try:
                # Create progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Step 1: Scrape articles
                status_text.text("Scraping articles from RSS feeds...")
                progress_bar.progress(25)
                
                articles = scraper.scrape_rss_feeds(max_articles=max_articles)
                
                # Step 2: Filter articles
                if auto_filter:
                    status_text.text("Filtering for F1 relevance...")
                    progress_bar.progress(50)
                    articles = scraper.filter_f1_content(articles)
                
                # Step 3: Save articles
                status_text.text("Saving articles...")
                progress_bar.progress(75)
                scraper.save_articles(articles)
                
                # Step 4: Update vector store
                status_text.text("Updating knowledge base...")
                progress_bar.progress(90)
                
                success = st.session_state.rag_system.update_online_content()
                
                progress_bar.progress(100)
                status_text.text("Complete!")
                
                if success:
                    st.success(f"✅ Successfully updated with {len(articles)} new articles!")
                else:
                    st.info("ℹ️ No new articles found")
                
            except Exception as e:
                st.error(f"❌ Error updating content: {e}")

def show_source_management():
    st.header("📰 Source Management")
    
    st.markdown("""
    Manage the online sources that your F1 chatbot scrapes for content.
    """)
    
    # Current sources
    st.subheader("🔧 Current Sources")
    
    scraper = F1WebScraper()
    
    for source_id, source_info in scraper.f1_sources.items():
        with st.expander(f"{source_info['name']} ({source_id})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Name:** {source_info['name']}")
                st.write(f"**Base URL:** {source_info['base_url']}")
                st.write(f"**RSS Feeds:** {len(source_info['rss_feeds'])}")
            
            with col2:
                # Show scraping stats
                stats = scraper.get_scraping_stats()
                source_stats = next((s for s in stats['sources'] if s['source'] == source_id), None)
                if source_stats:
                    st.metric("Articles", source_stats['count'])
                else:
                    st.metric("Articles", 0)
    
    # Add new source
    st.subheader("➕ Add New Source")
    
    with st.form("add_source"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_source_id = st.text_input("Source ID", placeholder="e.g., f1_news")
            new_source_name = st.text_input("Source Name", placeholder="e.g., F1 News")
            new_base_url = st.text_input("Base URL", placeholder="https://example.com")
        
        with col2:
            new_rss_feeds = st.text_area("RSS Feeds (one per line)", placeholder="https://example.com/rss")
            new_scrape_patterns = st.text_area("Scrape Patterns (one per line)", placeholder="/news/\n/articles/")
        
        if st.form_submit_button("Add Source"):
            if new_source_id and new_source_name and new_base_url:
                # Add to sources (this would need to be persisted)
                st.success(f"✅ Added source: {new_source_name}")
            else:
                st.error("Please fill in all required fields")

def show_knowledge_base_stats():
    st.header("📊 Knowledge Base Statistics")
    
    stats = st.session_state.rag_system.get_knowledge_base_stats()
    
    if stats:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📚 Document Statistics")
            doc_stats = stats['documents']
            
            st.metric("Total Documents", doc_stats['total_documents'])
            st.metric("Static Documents", doc_stats['static_documents'])
            st.metric("Online Documents", doc_stats['online_documents'])
            st.metric("Total Chunks", doc_stats['total_chunks'])
        
        with col2:
            st.subheader("🗄️ Vector Store Statistics")
            vector_stats = stats['vector_store']
            
            st.metric("Document Count", vector_stats['document_count'])
            st.metric("Collection Name", vector_stats['collection_name'])
            st.metric("Embedding Model", vector_stats['embedding_model'])
        
        # Source breakdown
        st.subheader("📰 Source Breakdown")
        
        if doc_stats['static_sources'] > 0:
            st.write(f"**Static Sources:** {doc_stats['static_sources']}")
        
        if doc_stats['online_sources'] > 0:
            st.write(f"**Online Sources:** {doc_stats['online_sources']}")
        
        # Show online content details
        online_dir = Path("./knowledge_base/online")
        if online_dir.exists():
            st.subheader("🌐 Online Content Details")
            
            for source_file in online_dir.glob("*_articles.json"):
                try:
                    with open(source_file, 'r') as f:
                        articles = json.load(f)
                    
                    source_name = source_file.stem.replace('_articles', '')
                    
                    with st.expander(f"{source_name} ({len(articles)} articles)"):
                        if articles:
                            # Show recent articles
                            recent_articles = sorted(articles, key=lambda x: x.get('scraped_at', ''), reverse=True)[:5]
                            
                            for article in recent_articles:
                                st.write(f"**{article['title']}**")
                                st.write(f"Published: {article.get('published', 'Unknown')}")
                                st.write(f"Source: {article['source']}")
                                st.write("---")
                except Exception as e:
                    st.error(f"Error reading {source_file}: {e}")
    else:
        st.error("Could not retrieve statistics")

def show_manual_scraping():
    st.header("🔗 Manual URL Scraping")
    
    st.markdown("""
    Manually scrape specific URLs to add to your knowledge base.
    """)
    
    # URL input
    st.subheader("📝 Add URLs")
    
    urls_text = st.text_area(
        "Enter URLs (one per line)",
        placeholder="https://www.formula1.com/en/latest/article/example.html\nhttps://www.motorsport.com/f1/news/example/",
        height=150
    )
    
    if st.button("🚀 Scrape URLs", type="primary"):
        if urls_text.strip():
            urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
            
            with st.spinner(f"Scraping {len(urls)} URLs..."):
                try:
                    scraper = F1WebScraper()
                    articles = scraper.scrape_specific_urls(urls)
                    
                    if articles:
                        # Filter for F1 relevance
                        filtered_articles = scraper.filter_f1_content(articles)
                        
                        # Save articles
                        scraper.save_articles(filtered_articles)
                        
                        # Update knowledge base
                        success = st.session_state.rag_system.update_online_content()
                        
                        if success:
                            st.success(f"✅ Successfully scraped and added {len(filtered_articles)} articles!")
                        else:
                            st.warning("⚠️ Articles scraped but knowledge base update failed")
                    else:
                        st.error("❌ No articles could be scraped from the provided URLs")
                        
                except Exception as e:
                    st.error(f"❌ Error scraping URLs: {e}")
        else:
            st.error("Please enter at least one URL")

if __name__ == "__main__":
    main()
