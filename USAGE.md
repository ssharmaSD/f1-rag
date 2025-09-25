# F1 Racing Chatbot - Usage Guide

## Quick Start

### 1. Installation
```bash
# Clone or download the project
cd f1-rag

# Install dependencies
pip install -r requirements.txt

# Or use the setup script
python setup.py
```

### 2. Run the Chatbot
```bash
streamlit run app.py
```

The chatbot will open in your browser at `http://localhost:8501`

## Features

### 🎯 What the Chatbot Can Do
- **Answer F1 Questions**: Ask about rules, regulations, history, engineering
- **Educational Focus**: Designed specifically for beginners
- **Comprehensive Knowledge**: Covers sport and engineering aspects
- **Free to Use**: No API costs or subscriptions required

### 📚 Knowledge Areas Covered
- **F1 Basics**: What is Formula 1, race format, points system
- **Rules & Regulations**: Technical and sporting regulations
- **Engineering**: Aerodynamics, power units, chassis, electronics
- **History**: Origins, legendary drivers, significant moments
- **Teams & Drivers**: Current and historic teams and drivers
- **Strategy**: Race strategy, tire management, overtaking

## Example Questions

### Basic Questions
- "What is Formula 1?"
- "How does the F1 points system work?"
- "What are the current F1 rules?"

### Engineering Questions
- "How do F1 engines work?"
- "What is aerodynamics in F1?"
- "How does DRS work?"
- "What are F1 tires made of?"

### Historical Questions
- "Who are the most successful F1 drivers?"
- "What happened in the 1994 San Marino Grand Prix?"
- "How has F1 safety evolved?"

### Strategy Questions
- "How do pit stops work?"
- "What is tire strategy in F1?"
- "How do teams plan race strategy?"

## Technical Details

### Architecture
- **RAG System**: Retrieval-Augmented Generation
- **Vector Store**: ChromaDB for semantic search
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **LLM**: Microsoft DialoGPT-medium (free model)
- **Interface**: Streamlit web application

### Performance
- **Response Time**: Typically 2-5 seconds
- **Accuracy**: High accuracy for F1-specific questions
- **Fallback**: Simple response generation if LLM fails

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Make sure all dependencies are installed
pip install -r requirements.txt
```

#### 2. Model Download Issues
```bash
# Clear HuggingFace cache
rm -rf ~/.cache/huggingface/
```

#### 3. ChromaDB Issues
```bash
# Clear vector database
rm -rf ./data/chroma_db/
```

#### 4. Memory Issues
- The system works on CPU but GPU is recommended
- Reduce batch size in config.py if needed

### System Requirements
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB for models and data
- **GPU**: Optional but recommended for better performance

## Customization

### Adding New Knowledge
1. Add markdown files to `knowledge_base/` directory
2. Restart the application
3. The system will automatically index new content

### Modifying Configuration
Edit `config.py` to change:
- Model settings
- Retrieval parameters
- UI configuration
- Performance settings

### Using Different Models
Change the model in `config.py`:
```python
LLM_MODEL = "your-preferred-model"
```

## Advanced Usage

### Testing the System
```bash
python test_system.py
```

### Command Line Interface
```python
from utils.rag_system import F1RAGSystem

rag = F1RAGSystem()
response = rag.chat("What is Formula 1?")
print(response)
```

### Batch Processing
```python
questions = ["What is F1?", "How do engines work?"]
for question in questions:
    response = rag.chat(question)
    print(f"Q: {question}\nA: {response}\n")
```

## Support

### Getting Help
- Check the README.md for basic information
- Review the knowledge base files for content
- Test with example questions first
- Check system requirements

### Contributing
- Add new knowledge base content
- Improve the RAG system
- Enhance the user interface
- Optimize performance

## License

This project is open source and free to use for educational purposes.
