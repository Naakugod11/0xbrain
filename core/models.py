from pydantic import BaseModel
from typing import List

class DocumentChunk(BaseModel):
    content: str
    source: str
    chunk_index: int
    metadata: dict = {}

class IngestRequest(BaseModel):
    source: str 
    title: int
    category: str = "general"

class IngestResponse(BaseModel):
    title: str
    chunks_created: int
    status: str

class QueryRequest(BaseModel):
    question: str
    top_k: int | None = None
    category_filter: str | None = None

class Source(BaseModel):
    title: str
    content_snippet: str
    relevance_score: float

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[Source]

class DocumentInfo(BaseModel):
    title: str
    category: str
    chunk_count: int