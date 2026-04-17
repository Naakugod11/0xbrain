import chromadb
from chromadb.config import Settings as ChromaSettings
from core.config import settings
from core.models import DocumentChunk
from services.embedding import embed_text, embed_batch

# PersistentClient saves to disk — survives server restarts.
client = chromadb.PersistentClient(
    path=settings.chroma_persist_dir,
)

# measures angle between vectors for the fast nearest-neoghbor search algo
collection = client.get_or_create_collection(
    name="0xbrain",
    metadata={"hnsw:space": "cosine"},
)

def add_chunks(chunks: list[DocumentChunk], title: str, category: str = "general"):
    """Add document chunks to the vector store. Uses upsert to avoid duplicates"""
    texts = [chunk.content for chunk in chunks]
    embeddings = embed_batch(texts)

    collection.upsert(
        ids=[f"{title}_{chunk.chunk_index}" for chunk in chunks],
        documents=texts,
        embeddings=embeddings,
        metadatas=[{
            "source": chunk.source,
            "title": title,
            "category": category,
            "chunk_index": chunk.chunk_index,
        }for chunk in chunks],
    )

def query_chunks(question: str, top_k: int = None, category_filter: str = None) -> list[dict]:
    """Find the most relevant chunks for a question."""
    k = top_k or settings.top_k_results
    query_embedding = embed_text(question)

    where_filter = None
    if category_filter:
        where_filter = {"category": category_filter}
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        where=where_filter,
    )

    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "content": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
        })
    
    return chunks

def list_documents() -> list[dict]:
    """List all unique documents in the store."""
    all_items = collection.get()

    docs = {}
    for meta in all_items["metadatas"]:
        title = meta["title"]
        if title not in docs:
            docs[title] = {
                "title": title,
                "category": meta.get("category", "general"),
                "chunk_count" : 0,
            }
        docs[title]["chunk_count"] += 1
    
    return list(docs.values())
