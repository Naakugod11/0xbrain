from services.embedding import embed_text, embed_batch


def test_embed_text_returns_vector():
    vec = embed_text("Hello world")
    assert isinstance(vec, list)
    assert len(vec) == 384  # all-MiniLM-L6-v2 outputs 384 dims


def test_embed_batch_returns_vectors():
    vecs = embed_batch(["Hello", "World"])
    assert len(vecs) == 2
    assert len(vecs[0]) == 384


def test_similar_texts_closer():
    vec1 = embed_text("Ethereum is a blockchain")
    vec2 = embed_text("ETH is a cryptocurrency")
    vec3 = embed_text("Pizza recipe with tomato")

    # Cosine similarity helper
    def cosine(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x ** 2 for x in a) ** 0.5
        norm_b = sum(x ** 2 for x in b) ** 0.5
        return dot / (norm_a * norm_b)

    sim_related = cosine(vec1, vec2)
    sim_unrelated = cosine(vec1, vec3)
    assert sim_related > sim_unrelated
