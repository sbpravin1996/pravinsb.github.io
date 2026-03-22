"""Query embedding and similarity search."""

from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings as ChromaSettings

from .config import (
    CHROMA_PERSIST_DIR,
    EMBEDDING_MODEL,
    TOP_K,
    COLLECTION_NAME,
)


def get_retriever():
    """Return a retriever function."""
    model = SentenceTransformer(EMBEDDING_MODEL)
    client = chromadb.PersistentClient(
        path=str(CHROMA_PERSIST_DIR),
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
    except Exception:
        return lambda query, top_k=TOP_K: []

    def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
        """Retrieve top-k relevant chunks for a query."""
        query_embedding = model.encode([query])
        results = collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        chunks = []
        if results["documents"] and results["documents"][0]:
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0] or [{}] * len(results["documents"][0]),
                results["distances"][0] if results["distances"] else [0] * len(results["documents"][0]),
            ):
                chunks.append({
                    "content": doc,
                    "metadata": meta or {},
                    "distance": dist,
                })
        return chunks

    return retrieve
