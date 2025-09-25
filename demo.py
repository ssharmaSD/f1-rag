"""
Demo script for F1 RAG Chatbot
"""
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent))

def run_demo():
    """Run a demonstration of the F1 chatbot"""
    print("🏎️ F1 Racing Chatbot Demo")
    print("=" * 50)
    print("This demo showcases the RAG system with sample questions.")
    print("The chatbot uses free models and comprehensive F1 knowledge.\n")
    
    try:
        from utils.rag_system import F1RAGSystem
        
        # Initialize system
        print("Initializing F1 RAG system...")
        rag_system = F1RAGSystem()
        print("✅ System ready!\n")
        
        # Demo questions
        demo_questions = [
            {
                "question": "What is Formula 1?",
                "category": "Basics"
            },
            {
                "question": "How do F1 engines work?",
                "category": "Engineering"
            },
            {
                "question": "What are the F1 rules for overtaking?",
                "category": "Rules"
            },
            {
                "question": "Who are the most successful F1 drivers?",
                "category": "History"
            }
        ]
        
        for i, demo in enumerate(demo_questions, 1):
            print(f"📝 Demo {i}: {demo['category']}")
            print(f"Question: {demo['question']}")
            print("-" * 40)
            
            try:
                response = rag_system.chat(demo['question'])
                print(f"Answer: {response}")
            except Exception as e:
                print(f"Error: {e}")
            
            print("\n" + "=" * 50 + "\n")
        
        # Show system info
        print("📊 System Information:")
        info = rag_system.get_knowledge_base_info()
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        print("\n🎉 Demo completed successfully!")
        print("\nTo run the full chatbot:")
        print("  streamlit run app.py")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("\nMake sure to install dependencies first:")
        print("  pip install -r requirements.txt")

if __name__ == "__main__":
    run_demo()
