"""Ingest PDF documents: load, chunk, embed, and store in ChromaDB."""

from pathlib import Path

from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings as ChromaSettings

from .config import (
    DATA_DIR,
    CHROMA_PERSIST_DIR,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    COLLECTION_NAME,
)


def load_pdf_text(file_path: Path) -> list[tuple[str, int]]:
    """Load PDF and return list of (page_text, page_number)."""
    chunks_with_meta = []
    reader = PdfReader(file_path)
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            chunks_with_meta.append((text.strip(), i + 1))
    return chunks_with_meta


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
    return chunks


def ingest():
    """Load all PDFs from data/, chunk, embed, and store in ChromaDB."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)

    pdf_files = list(DATA_DIR.rglob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {DATA_DIR}")
        return

    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)

    client = chromadb.PersistentClient(
        path=str(CHROMA_PERSIST_DIR),
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    all_texts = []
    all_metadatas = []
    all_ids = []
    id_counter = 0

    for pdf_path in pdf_files:
        print(f"Processing: {pdf_path}")
        pages = load_pdf_text(pdf_path)
        source_name = pdf_path.name

        for page_text, page_num in pages:
            page_chunks = chunk_text(page_text, CHUNK_SIZE, CHUNK_OVERLAP)
            for chunk in page_chunks:
                all_texts.append(chunk)
                all_metadatas.append({
                    "source": source_name,
                    "page": page_num,
                })
                all_ids.append(f"doc_{id_counter}")
                id_counter += 1

    if not all_texts:
        print("No text extracted from PDFs.")
        return

    # Embed in batches
    print(f"Embedding {len(all_texts)} chunks...")
    embeddings = model.encode(all_texts, show_progress_bar=True)

    # Upsert into ChromaDB
    collection.add(
        ids=all_ids,
        embeddings=embeddings.tolist(),
        documents=all_texts,
        metadatas=all_metadatas,
    )
    print(f"Stored {len(all_texts)} chunks in ChromaDB.")
