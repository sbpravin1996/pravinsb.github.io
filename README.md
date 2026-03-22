# pravinsb.github.io

## Local RAG for PDFs

A fully local RAG (Retrieval-Augmented Generation) pipeline that ingests PDF documents, embeds them with sentence-transformers, stores vectors in ChromaDB, and generates answers using Ollama.

## Prerequisites

1. **Python 3.9+**
2. **Ollama** installed and running with a model (e.g. `ollama pull llama3.2`)
3. **PDF documents** in the `data/` folder

## Setup

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

Optional: Copy `.env.example` to `.env` and adjust settings.

## Usage

### 1. Ingest PDFs

Place PDF files in `data/`, then run:

```bash
python main.py ingest
```

### 2. Query

```bash
python main.py query "What is the main topic of the document?"
```

Or run without arguments for interactive mode:

```bash
python main.py query
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence-transformers model |
| `OLLAMA_MODEL` | `llama3.2` | Ollama model name |
| `CHROMA_PERSIST_DIR` | `chroma_db` | ChromaDB storage path |
| `DATA_DIR` | `data` | Directory containing PDFs |
| `CHUNK_SIZE` | 512 | Characters per chunk |
| `CHUNK_OVERLAP` | 50 | Overlap between chunks |
| `TOP_K` | 4 | Number of chunks to retrieve |

---

## AI Podcast Generation

See [ai_podcast/README.md](ai_podcast/README.md) for the AI podcast pipeline (LLM + Higgs 2.5 TTS + FFmpeg).
