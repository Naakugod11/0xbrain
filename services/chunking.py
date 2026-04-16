from core.config import settings
from core.models import DocumentChunk

def chunk_text(text:str, source: str) -> list[DocumentChunk]:
    """Split text into overlapping chunks."""
    text = " ".join(text.split())

    chunk_size = settings.chunk_size
    overlap = settings.chunk_overlap

    char_chunk_size = chunk_size * 4
    char_overlap = overlap + 4

    chunks = []
    start = 0
    index = 0

    while start < len(text):
        end = start + char_chunk_size
        chunk_content = text[start:end]

        if end < len(text):
            last_period = chunk_content.rfind(". ")
            if last_period > char_chunk_size * 0.5:
                chunk_content = chunk_content[:last_period + 1]
                end = start + last_period + 1
        
        chunks.append(DocumentChunk(
            content=chunk_content.strip(),
            source=source,
            chunk_index=index,
        ))

        start = end - char_overlap
        index += 1
    
    return chunks