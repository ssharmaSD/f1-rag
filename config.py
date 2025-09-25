"""
Configuration file for F1 RAG Chatbot
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
KNOWLEDGE_BASE_PATH = BASE_DIR / "knowledge_base"
DATA_PATH = BASE_DIR / "data"
MODELS_PATH = BASE_DIR / "models"

# Vector store configuration
VECTOR_STORE_PATH = DATA_PATH / "chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "f1_knowledge"

# LLM configuration
LLM_MODEL = "microsoft/DialoGPT-medium"  # Free model
MAX_LENGTH = 512
TEMPERATURE = 0.7
TOP_P = 0.9

# RAG configuration
MAX_CHUNK_SIZE = 500
N_RETRIEVAL_RESULTS = 3
SIMILARITY_THRESHOLD = 0.7

# Streamlit configuration
PAGE_TITLE = "F1 Racing Chatbot"
PAGE_ICON = "🏎️"
LAYOUT = "wide"

# Chat configuration
MAX_CHAT_HISTORY = 50
ENABLE_CHAT_EXPORT = True

# Performance configuration
ENABLE_CACHING = True
CACHE_TTL = 3600  # 1 hour

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FILE = DATA_PATH / "chatbot.log"

# Create directories if they don't exist
for path in [DATA_PATH, MODELS_PATH, VECTOR_STORE_PATH]:
    path.mkdir(parents=True, exist_ok=True)
