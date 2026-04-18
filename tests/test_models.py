import pytest
from core.models import QueryRequest, Source, QueryResponse


def test_query_request_defaults():
    req = QueryRequest(question="What is ETH?")
    assert req.question == "What is ETH?"
    assert req.top_k is None
    assert req.category_filter is None


def test_query_request_with_filter():
    req = QueryRequest(question="test", top_k=3, category_filter="defi")
    assert req.top_k == 3
    assert req.category_filter == "defi"


def test_source_model():
    source = Source(
        title="Bitcoin Whitepaper",
        content_snippet="Some text...",
        relevance_score=0.85,
    )
    assert source.title == "Bitcoin Whitepaper"
    assert source.relevance_score == 0.85


def test_query_response():
    resp = QueryResponse(
        question="What is BTC?",
        answer="Bitcoin is...",
        sources=[],
    )
    assert resp.question == "What is BTC?"
    assert resp.sources == []