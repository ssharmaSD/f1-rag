# F1 Racing Chatbot with RAG

A comprehensive chatbot that teaches Formula 1 racing from both sporting and engineering perspectives using Retrieval-Augmented Generation (RAG) with free/open-source models.

## Features

- **Comprehensive Knowledge Base**: Covers F1 rules, regulations, history, engineering, and technical aspects
- **RAG Implementation**: Uses semantic search to retrieve relevant context for accurate responses
- **Free Models**: Built with HuggingFace transformers and free models (no API costs)
- **Interactive Interface**: User-friendly Streamlit web interface
- **Educational Focus**: Designed specifically for beginners learning about F1

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the chatbot:
```bash
streamlit run app.py
```

## Architecture

- **Knowledge Base**: Structured F1 data in markdown files
- **Vector Store**: ChromaDB for semantic search
- **Embeddings**: Sentence transformers for document and query embeddings
- **LLM**: HuggingFace transformers (free models like GPT-2, T5, or Llama-2)
- **Interface**: Streamlit for web-based chat interface

## Usage

The chatbot can answer questions about:
- F1 rules and regulations
- Race procedures and formats
- Engineering and technical aspects
- Historical information
- Driver and team information
- Car specifications and aerodynamics

## ⚠️ Known Issues & Debugging Needed

### Critical Issues
- **Knowledge Base Accuracy**: Vector search and retrieval needs optimization for better relevance
- **Response Intelligence**: Chatbot responses need enhancement for better educational value
- **LLM Integration**: Disabled due to PyTorch security vulnerability (CVE-2025-32434)
- **Content Quality**: Some retrieved content may not be optimally relevant to queries

### Technical Debugging Required
- Vector similarity scoring optimization
- Response generation improvement (currently using basic fallback)
- Knowledge base chunking strategy refinement
- F1 content filtering and relevance scoring
- Integration with secure LLM models

### Data Source Issues
- Some RSS feeds may be intermittently unavailable
- API endpoints (Ergast) occasionally down
- Content deduplication needed
- Source attribution consistency

## Current Status
🟡 **Beta Version** - Functional but requires debugging and optimization for production use
