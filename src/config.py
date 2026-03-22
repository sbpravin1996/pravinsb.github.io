"""Configuration settings for the RAG pipeline."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / os.getenv("DATA_DIR", "data")
CHROMA_PERSIST_DIR = PROJECT_ROOT / os.getenv("CHROMA_PERSIST_DIR", "chroma_db")

# Embedding
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# LLM
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Chunking
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# Retrieval
TOP_K = int(os.getenv("TOP_K", "4"))
COLLECTION_NAME = "pdf_docs"
