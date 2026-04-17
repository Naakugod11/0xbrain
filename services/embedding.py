from sentence_transformers import SentenceTransformer
from core.config import settings

# local embedding model - runs on cpu, no api costs
# for production, switch to gpu or an api
model = SentenceTransformer(settings.embedding_model)

def embed_text(text: str) -> list[float]:
    """Convert a single text into a vector."""
    return model.encode(text).tolist()

def embed_batch(texts: list[str]) -> list[list[float]]:
    """Conver multiple texts into vectors at once."""
    return model.encode(texts).tolist()