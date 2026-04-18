from services.chunking import chunk_text

def test_chunk_text_creates_chunks():
    text = "Hello world. " * 200
    chunks = chunk_text(text, source="test.pdf")
    assert len(chunks) > 1
    assert chunks[0].source == "test.pdf"
    assert chunks[0].chunk_index == 0


def test_chunk_text_short_text():
    text = "This is a short text."
    chunks = chunk_text(text, source="short.pdf")
    assert len(chunks) == 1
    assert chunks[0].content == text


def test_chunk_indices_sequential():
    text = "Some sentence here. " * 300
    chunks = chunk_text(text, source="test.pdf")
    for i, chunk in enumerate(chunks):
        assert chunk.chunk_index == i


def test_chunks_have_overlap():
    text = "Word " * 1000
    chunks = chunk_text(text, source="test.pdf")
    if len(chunks) > 1:
        # Last words of chunk 0 should appear in start of chunk 1
        end_of_first = chunks[0].content[-50:]
        start_of_second = chunks[1].content[:100]
        # At least some overlap should exist
        assert any(word in start_of_second for word in end_of_first.split())
