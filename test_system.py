"""
Test script for F1 RAG system
"""
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent))

from utils.rag_system import F1RAGSystem

def test_system():
    """Test the RAG system with sample questions"""
    print("🏎️ Testing F1 RAG System...")
    
    try:
        # Initialize system
        print("Initializing RAG system...")
        rag_system = F1RAGSystem()
        print("✅ System initialized successfully!")
        
        # Test questions
        test_questions = [
            "What is Formula 1?",
            "How do F1 engines work?",
            "What are the F1 rules?",
            "Who are the most successful F1 drivers?"
        ]
        
        print("\n📝 Testing with sample questions:")
        print("=" * 50)
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n{i}. Question: {question}")
            print("-" * 30)
            
            try:
                response = rag_system.chat(question)
                print(f"Answer: {response}")
            except Exception as e:
                print(f"Error: {e}")
        
        # Test knowledge base info
        print("\n📊 Knowledge Base Information:")
        print("=" * 50)
        info = rag_system.get_knowledge_base_info()
        for key, value in info.items():
            print(f"{key}: {value}")
            
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_system()
