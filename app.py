"""
F1 Racing Chatbot with RAG - Streamlit Interface
"""
import streamlit as st
import sys
import os
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent))

from utils.rag_system import F1RAGSystem

# Page configuration
st.set_page_config(
    page_title="F1 Racing Chatbot",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #e10600;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #e10600;
    }
    .user-message {
        background-color: #f0f2f6;
        border-left-color: #0066cc;
    }
    .bot-message {
        background-color: #fff5f5;
        border-left-color: #e10600;
    }
    .stButton > button {
        background-color: #e10600;
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #c00500;
    }
    .info-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'rag_system' not in st.session_state:
    st.session_state.rag_system = None
if 'initialized' not in st.session_state:
    st.session_state.initialized = False

# Header
st.markdown('<h1 class="main-header">🏎️ F1 Racing Chatbot</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Learn about Formula 1 racing from both sporting and engineering perspectives!</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🚀 About This Chatbot")
    st.markdown("""
    This chatbot uses **Retrieval-Augmented Generation (RAG)** to answer questions about Formula 1 racing.
    
    **Features:**
    - 📚 Comprehensive F1 knowledge base
    - 🔍 Semantic search for accurate answers
    - 🤖 Free AI models (no API costs)
    - 🎓 Educational focus for beginners
    
    **Topics covered:**
    - F1 rules and regulations
    - Engineering and technology
    - History and legends
    - Teams and drivers
    - Strategy and tactics
    """)
    
    st.header("💡 Example Questions")
    example_questions = [
        "What is Formula 1?",
        "How do F1 engines work?",
        "What are the current F1 rules?",
        "Who are the most successful F1 drivers?",
        "How does aerodynamics work in F1?",
        "What is the F1 points system?",
        "How do pit stops work?",
        "What is DRS in Formula 1?"
    ]
    
    for question in example_questions:
        if st.button(question, key=f"example_{question}"):
            st.session_state.user_input = question
            st.rerun()
    
    st.header("📊 Knowledge Base Info")
    if st.session_state.rag_system:
        info = st.session_state.rag_system.get_knowledge_base_info()
        st.metric("Documents", info['document_count'])
        st.metric("Model", info['embedding_model'])

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Chat with the F1 Expert")
    
    # Initialize RAG system
    if not st.session_state.initialized:
        with st.spinner("Initializing F1 knowledge base..."):
            try:
                st.session_state.rag_system = F1RAGSystem()
                st.session_state.initialized = True
                st.success("✅ F1 knowledge base loaded successfully!")
            except Exception as e:
                st.error(f"❌ Error initializing system: {e}")
                st.stop()
    
    # Chat interface
    if st.session_state.initialized:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask me anything about Formula 1!"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = st.session_state.rag_system.chat(prompt)
                        st.markdown(response)
                        
                        # Add assistant response to chat history
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        
                    except Exception as e:
                        error_msg = f"Sorry, I encountered an error: {e}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})

with col2:
    st.header("🎯 Quick Actions")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", type="secondary"):
        st.session_state.messages = []
        st.rerun()
    
    # Reload knowledge base button
    if st.button("🔄 Reload Knowledge Base", type="secondary"):
        with st.spinner("Reloading knowledge base..."):
            try:
                st.session_state.rag_system = F1RAGSystem()
                st.success("✅ Knowledge base reloaded!")
            except Exception as e:
                st.error(f"❌ Error reloading: {e}")
    
    st.header("📚 Knowledge Topics")
    topics = [
        "🏁 F1 Basics",
        "📋 Rules & Regulations", 
        "⚙️ Engineering & Technology",
        "📖 History & Legends",
        "👥 Teams & Drivers",
        "🎯 Strategy & Tactics"
    ]
    
    for topic in topics:
        st.markdown(f"• {topic}")
    
    st.header("🔧 Technical Info")
    st.markdown("""
    **RAG System:**
    - Vector Store: Custom NumPy-based
    - Embeddings: Sentence Transformers
    - LLM: Fallback Response Generation
    - Framework: Streamlit + Transformers
    
    **Data Sources:**
    - Static F1 Knowledge Base
    - Official F1 RSS Feeds
    - Ergast F1 API (Free)
    - Ethical Web Scraping Only
    
    **No API costs!** 🎉
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        🏎️ F1 Racing Chatbot | Built with RAG and free AI models | 
        <a href='https://github.com' target='_blank'>GitHub</a>
    </div>
    """, 
    unsafe_allow_html=True
)
