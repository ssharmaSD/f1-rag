# Dependency Troubleshooting Guide

## Common Dependency Issues and Solutions

### 1. PyTorch Installation Issues

**Problem**: PyTorch installation fails or conflicts with other packages.

**Solutions**:
```bash
# Option 1: Install PyTorch with CPU support only
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Option 2: Use conda instead of pip
conda install pytorch torchvision torchaudio cpuonly -c pytorch

# Option 3: Install specific version
pip install torch==2.0.1
```

### 2. Transformers Library Conflicts

**Problem**: Transformers version conflicts with other packages.

**Solutions**:
```bash
# Install compatible version
pip install transformers==4.30.2

# Or install without dependencies and resolve manually
pip install transformers --no-deps
pip install tokenizers safetensors huggingface-hub
```

### 3. ChromaDB Issues

**Problem**: ChromaDB installation fails or has import errors.

**Solutions**:
```bash
# Install with specific dependencies
pip install chromadb[server]

# Or install alternative vector store
pip install faiss-cpu
```

### 4. Streamlit Issues

**Problem**: Streamlit installation or runtime errors.

**Solutions**:
```bash
# Install latest stable version
pip install streamlit

# Or install specific version
pip install streamlit==1.28.1
```

### 5. NumPy/Pandas Conflicts

**Problem**: NumPy or Pandas version conflicts.

**Solutions**:
```bash
# Install compatible versions
pip install numpy==1.24.3 pandas==2.0.3

# Or let pip resolve automatically
pip install numpy pandas
```

## Step-by-Step Installation

### Method 1: Clean Installation
```bash
# Create new virtual environment
python -m venv f1-chatbot-env
source f1-chatbot-env/bin/activate  # On Windows: f1-chatbot-env\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install minimal requirements first
pip install -r requirements-minimal.txt

# Test basic functionality
python -c "import streamlit, transformers, chromadb; print('Basic imports successful')"
```

### Method 2: Conda Installation
```bash
# Create conda environment
conda create -n f1-chatbot python=3.9
conda activate f1-chatbot

# Install packages via conda
conda install pytorch cpuonly -c pytorch
conda install -c conda-forge streamlit transformers sentence-transformers
pip install chromadb python-dotenv
```

### Method 3: Docker Installation
```bash
# Create Dockerfile
cat > Dockerfile << EOF
FROM python:3.9-slim

WORKDIR /app
COPY requirements-minimal.txt .
RUN pip install -r requirements-minimal.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
EOF

# Build and run
docker build -t f1-chatbot .
docker run -p 8501:8501 f1-chatbot
```

## Platform-Specific Issues

### macOS (Apple Silicon)
```bash
# Install PyTorch for Apple Silicon
pip install torch torchvision torchaudio

# If you get architecture errors, try:
arch -arm64 pip install torch
```

### Windows
```bash
# Install Visual C++ Build Tools if you get compilation errors
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Use pre-compiled wheels
pip install --only-binary=all torch transformers
```

### Linux
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-dev build-essential

# Install Python packages
pip install -r requirements-minimal.txt
```

## Testing Installation

### Test Script
```python
# test_imports.py
try:
    import streamlit as st
    print("✅ Streamlit imported successfully")
except ImportError as e:
    print(f"❌ Streamlit import failed: {e}")

try:
    import transformers
    print("✅ Transformers imported successfully")
except ImportError as e:
    print(f"❌ Transformers import failed: {e}")

try:
    import chromadb
    print("✅ ChromaDB imported successfully")
except ImportError as e:
    print(f"❌ ChromaDB import failed: {e}")

try:
    import sentence_transformers
    print("✅ Sentence Transformers imported successfully")
except ImportError as e:
    print(f"❌ Sentence Transformers import failed: {e}")

try:
    import torch
    print(f"✅ PyTorch imported successfully (version: {torch.__version__})")
except ImportError as e:
    print(f"❌ PyTorch import failed: {e}")
```

Run with: `python test_imports.py`

## Alternative Approaches

### 1. Use Google Colab
- Upload the project to Google Colab
- Install dependencies in Colab environment
- Run the chatbot in Colab

### 2. Use Hugging Face Spaces
- Deploy directly to Hugging Face Spaces
- Use their pre-configured environment

### 3. Use Replit
- Import project to Replit
- Use their package manager

## Getting Help

If you're still having issues:

1. **Check Python version**: `python --version` (should be 3.8+)
2. **Check pip version**: `pip --version`
3. **Clear pip cache**: `pip cache purge`
4. **Use virtual environment**: Always use a virtual environment
5. **Check system requirements**: Ensure you have enough RAM and storage

## Minimal Working Example

If all else fails, try this minimal setup:

```python
# minimal_app.py
import streamlit as st

st.title("F1 Chatbot (Minimal)")
st.write("This is a minimal version without RAG functionality.")

user_input = st.text_input("Ask about F1:")
if user_input:
    st.write(f"You asked: {user_input}")
    st.write("This is a placeholder response. Install full dependencies for RAG functionality.")
```

Run with: `streamlit run minimal_app.py`
