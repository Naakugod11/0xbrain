from anthropic import Anthropic
from core.config import settings
from core.models import QueryResponse, Source
from services.vector_store import query_chunks

client = Anthropic(api_key=settings.anthropic_api_key)

SYSTEM_PROMPT = """You are 0xbrain - a crypto knowledge engine.
You answer questions ONLY based on the provided context documents.

Rules:
- If the context contains the answer, provide it clearly
- Always reference which document the information comes from
- If the context does NOT contain enough info, say so honestly
- Never make uo information that isn't in the context
- Keep answers concise and technical"""

def ask(question: str, top_k: int = None, category_filter: str = None) -> QueryResponse:
    """RAG pipeline: retrieve relevant chunks, then generate an answer."""

    #Step 1: Retrieve relevant chunks from vector store
    chunks = query_chunks(question, top_k, category_filter)

    if not chunks:
        return QueryResponse(
            question=question,
            answer="No relevant documents found in the knowledge base.",
            sources=[],
        )

    # Step 2: Build context from retrieved chunks
    context = "\n\n---\n\n".join([
        f"[Source: {c['metadata']['title']}]\n{c['content']}"
        for c in chunks
    ])

    #Step 3: Ask Claude with the retrieved context
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Context documents:\n\n{context}\n\n---\n\nQuestion: {question}",
        }],
    )

    answer = response.content[0].text

    #Step 4: Build source references
    sources = [
        Source(
            title=c["metadata"]["title"],
            content_snippet=c["content"][:150] + "...",
            relevance_score=round(1- c["distance"], 3),
        )
        for c in chunks
    ]

    return QueryResponse(
        quesion=question,
        answer=answer,
        sources=sources,
    )

