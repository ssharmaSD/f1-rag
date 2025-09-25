"""
Retrieval-Augmented Generation system for F1 chatbot
"""
from typing import List, Dict
from .simple_vector_store import SimpleVectorStore
from .enhanced_document_processor import EnhancedDocumentProcessor
import torch
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for config import
sys.path.append(str(Path(__file__).parent.parent))

try:
    from transformers import (
        AutoTokenizer, 
        AutoModelForCausalLM, 
        pipeline
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: Transformers not available. Using simple response generation.")

try:
    import config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

class F1RAGSystem:
    """RAG system for F1 knowledge base"""
    
    def __init__(self, knowledge_base_path: str = None):
        # Use config if available, otherwise use defaults
        if CONFIG_AVAILABLE:
            self.knowledge_base_path = knowledge_base_path or str(config.KNOWLEDGE_BASE_PATH)
            self.vector_store_path = str(config.VECTOR_STORE_PATH)
            self.llm_model = config.LLM_MODEL
            self.max_length = config.MAX_LENGTH
            self.temperature = config.TEMPERATURE
            self.top_p = config.TOP_P
            self.n_retrieval_results = config.N_RETRIEVAL_RESULTS
        else:
            self.knowledge_base_path = knowledge_base_path or "./knowledge_base"
            self.vector_store_path = "./data/chroma_db"
            self.llm_model = "microsoft/DialoGPT-medium"
            self.max_length = 512
            self.temperature = 0.7
            self.top_p = 0.9
            self.n_retrieval_results = 3
        
        self.vector_store = SimpleVectorStore(self.vector_store_path)
        self.document_processor = EnhancedDocumentProcessor(self.knowledge_base_path)
        
        # Initialize LLM (using a free model)
        self._setup_llm()
        
        # Load knowledge base
        self._load_knowledge_base()
    
    def _setup_llm(self):
        """Setup the language model"""
        if not TRANSFORMERS_AVAILABLE:
            print("Transformers not available. Using simple response generation.")
            self.generator = None
            return
            
        # Check if CUDA is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        try:
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.llm_model)
            self.model = AutoModelForCausalLM.from_pretrained(self.llm_model)
            
            # Add padding token if it doesn't exist
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Create text generation pipeline
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if device == "cuda" else -1,
                max_length=self.max_length,
                do_sample=True,
                temperature=self.temperature,
                top_p=self.top_p,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            print(f"Loaded LLM: {self.llm_model} on {device}")
            
        except Exception as e:
            print(f"Error loading LLM: {e}")
            print("Falling back to simple response generation")
            self.generator = None
    
    def _load_knowledge_base(self):
        """Load and index the knowledge base"""
        try:
            # Check if collection is empty
            if self.vector_store.get_collection_info()['document_count'] == 0:
                print("Loading knowledge base...")
                documents = self.document_processor.load_all_documents()
                self.vector_store.add_documents(documents)
                print(f"Loaded {len(documents)} document chunks")
            else:
                print("Knowledge base already loaded")
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
    
    def retrieve_context(self, query: str, n_results: int = None) -> str:
        """Retrieve relevant context for the query"""
        try:
            if n_results is None:
                n_results = self.n_retrieval_results
            results = self.vector_store.search(query, n_results)
            
            if not results:
                return "No relevant information found in the knowledge base."
            
            # Combine results into context
            context_parts = []
            for result in results:
                context_parts.append(f"Source: {result['title']}\n{result['content']}\n")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return "Error retrieving information from knowledge base."
    
    def generate_response(self, query: str, context: str) -> str:
        """Generate response using retrieved context"""
        if self.generator is None:
            return self._simple_response(query, context)
        
        try:
            # Create prompt with context
            prompt = f"""Based on the following information about Formula 1 racing, please answer the question in a helpful and educational way for a beginner:

Context:
{context}

Question: {query}

Answer:"""
            
            # Generate response
            response = self.generator(
                prompt,
                max_length=len(prompt.split()) + 100,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Extract generated text
            generated_text = response[0]['generated_text']
            answer = generated_text.split("Answer:")[-1].strip()
            
            # Clean up the response
            answer = self._clean_response(answer)
            
            return answer
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return self._simple_response(query, context)
    
    def _simple_response(self, query: str, context: str) -> str:
        """Simple response generation when LLM is not available"""
        if not context or "No relevant information found" in context:
            return "I don't have specific information about that topic in my knowledge base. Could you try asking about F1 rules, engineering, history, teams, drivers, or strategy?"
        
        # Extract key information from context
        lines = context.split('\n')
        relevant_lines = [line for line in lines if line.strip() and not line.startswith('Source:')]
        
        if relevant_lines:
            return f"Based on my knowledge base: {' '.join(relevant_lines[:3])}"
        else:
            return "I found some information but couldn't extract a clear answer. Please try rephrasing your question."
    
    def _clean_response(self, response: str) -> str:
        """Clean up generated response"""
        # Remove any remaining prompt text
        if "Question:" in response:
            response = response.split("Question:")[0]
        
        # Remove any incomplete sentences at the end
        sentences = response.split('.')
        if len(sentences) > 1 and len(sentences[-1].strip()) < 10:
            response = '.'.join(sentences[:-1]) + '.'
        
        return response.strip()
    
    def chat(self, query: str) -> str:
        """Main chat interface"""
        # Retrieve relevant context
        context = self.retrieve_context(query)
        
        # Generate response
        response = self.generate_response(query, context)
        
        return response
    
    def get_knowledge_base_info(self) -> Dict:
        """Get information about the knowledge base"""
        return self.vector_store.get_collection_info()
    
    def update_online_content(self):
        """Update online content and refresh vector store using ethical scraping"""
        try:
            from .ethical_web_scraper import EthicalF1WebScraper
            
            print("Updating online content using ethical scraping...")
            scraper = EthicalF1WebScraper()
            
            # Update online content
            new_articles_count = self.document_processor.update_online_content(scraper)
            
            if new_articles_count > 0:
                # Reload all documents (including new online content)
                print("Reloading knowledge base with updated content...")
                documents = self.document_processor.load_all_documents()
                
                # Clear and rebuild vector store
                self.vector_store.clear_collection()
                self.vector_store.add_documents(documents)
                
                print(f"Updated knowledge base with {new_articles_count} new articles")
                return True
            else:
                print("No new articles found")
                return False
                
        except Exception as e:
            print(f"Error updating online content: {e}")
            return False
    
    def get_knowledge_base_stats(self) -> Dict:
        """Get detailed statistics about the knowledge base"""
        try:
            vector_stats = self.vector_store.get_collection_info()
            doc_stats = self.document_processor.get_document_stats()
            
            return {
                'vector_store': vector_stats,
                'documents': doc_stats,
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}
    
    def search_with_source_info(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search with detailed source information"""
        try:
            results = self.vector_store.search(query, n_results)
            
            # Add source type information
            for result in results:
                if 'static_' in result.get('id', ''):
                    result['source_type'] = 'static'
                elif 'online_' in result.get('id', ''):
                    result['source_type'] = 'online'
                else:
                    result['source_type'] = 'unknown'
            
            return results
        except Exception as e:
            print(f"Error searching with source info: {e}")
            return []
