"""RAG pipeline: retrieve context and generate answer with Ollama."""

import os

import ollama

from .config import OLLAMA_MODEL, OLLAMA_HOST, TOP_K
from .retriever import get_retriever

# Ollama client reads OLLAMA_HOST from env
os.environ.setdefault("OLLAMA_HOST", OLLAMA_HOST)


def build_prompt(context_chunks: list[dict], question: str) -> str:
    """Build prompt with context and question."""
    context = "\n\n".join(
        f"[Source: {c['metadata'].get('source', '?')} p.{c['metadata'].get('page', '?')}]\n{c['content']}"
        for c in context_chunks
    )
    return f"""Use the following context to answer the question. If the context does not contain relevant information, say so.

Context:
{context}

Question: {question}

Answer:"""


def query(question: str, top_k: int | None = None) -> str:
    """Retrieve relevant chunks and generate answer."""
    retrieve = get_retriever()
    chunks = retrieve(question, top_k=top_k or TOP_K)
    if not chunks:
        return "No relevant documents found. Have you run 'python main.py ingest'?"

    prompt = build_prompt(chunks, question)
    response = ollama.generate(
        model=OLLAMA_MODEL,
        prompt=prompt,
    )
    return response["response"]
