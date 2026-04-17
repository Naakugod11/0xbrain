import json
from anthropic import Anthropic
from core.config import settings
from core.models import QueryResponse, Source
from services.vector_store import query_chunks

client = Anthropic(api_key=settings.anthropic_api_key)

SYSTEM_PROMPT = """You are 0xbrain — a crypto knowledge engine.
You answer questions ONLY based on the provided context documents.

Rules:
- If the context contains the answer, provide it clearly
- Always reference which document the information comes from
- If the context does NOT contain enough info, say so honestly
- Never make up information that isn't in the context
- Keep answers concise and technical"""

DECOMPOSE_PROMPT = """Break this question into 2-4 simple sub-questions that would help find all relevant information.
Return ONLY a JSON array of strings, nothing else.

Example:
Question: "How does Uniswap compare to Aave?"
["How does Uniswap work?", "How does Aave work?", "What are the differences between AMMs and lending protocols?"]

Question: "{question}"
"""


def decompose_question(question: str) -> list[str]:
    """Use Claude to split a complex question into sub-queries."""
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=256,
        messages=[{
            "role": "user",
            "content": DECOMPOSE_PROMPT.format(question=question),
        }],
    )

    raw = response.content[0].text
    try:
        sub_questions = json.loads(raw)
        if isinstance(sub_questions, list):
            return sub_questions
    except json.JSONDecodeError:
        pass

    # Fallback: use original question
    return [question]


def ask(question: str, top_k: int = None, category_filter: str = None) -> QueryResponse:
    """Multi-query RAG pipeline: decompose question, retrieve from multiple angles, generate answer."""

    # Step 1: Decompose into sub-questions
    sub_questions = decompose_question(question)

    # Step 2: Retrieve chunks for each sub-question
    all_chunks = []
    seen_ids = set()

    for sq in sub_questions:
        chunks = query_chunks(sq, top_k=top_k or 3, category_filter=category_filter)
        for c in chunks:
            # Deduplicate by content
            chunk_id = f"{c['metadata']['title']}_{c['metadata']['chunk_index']}"
            if chunk_id not in seen_ids:
                seen_ids.add(chunk_id)
                all_chunks.append(c)

    if not all_chunks:
        return QueryResponse(
            question=question,
            answer="No relevant documents found in the knowledge base.",
            sources=[],
        )

    # Step 3: Build context from all retrieved chunks
    context = "\n\n---\n\n".join([
        f"[Source: {c['metadata']['title']}]\n{c['content']}"
        for c in all_chunks
    ])

    # Step 4: Ask Claude with the combined context
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

    # Step 5: Build source references
    sources = [
        Source(
            title=c["metadata"]["title"],
            content_snippet=c["content"][:150] + "...",
            relevance_score=round(1 - c["distance"], 3),
        )
        for c in all_chunks
    ]

    return QueryResponse(
        question=question,
        answer=answer,
        sources=sources,
    )
