"""
Setup script for F1 RAG Chatbot
"""
import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = ["data", "data/chroma_db", "models"]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def test_installation():
    """Test if the system can be imported"""
    print("🧪 Testing installation...")
    try:
        from utils.rag_system import F1RAGSystem
        print("✅ System imports successfully!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main setup function"""
    print("🏎️ F1 RAG Chatbot Setup")
    print("=" * 40)
    
    # Create directories
    create_directories()
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed during package installation")
        return
    
    # Test installation
    if not test_installation():
        print("❌ Setup failed during import test")
        return
    
    print("\n🎉 Setup completed successfully!")
    print("\nTo run the chatbot:")
    print("  streamlit run app.py")
    print("\nTo test the system:")
    print("  python test_system.py")

if __name__ == "__main__":
    main()
