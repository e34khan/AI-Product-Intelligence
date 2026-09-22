from sentence_transformers import CrossEncoder

from app.db.models import Chunk

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"  # small, fast, widely used for exactly this

# same lazy-load-once pattern as embeddings.py, since loading the model takes a moment
_model = None


def get_reranker() -> CrossEncoder:
    global _model
    if _model is None:
        _model = CrossEncoder(MODEL_NAME)
    return _model


def rerank(query: str, chunks: list[Chunk], k: int = 5) -> list[tuple[Chunk, float]]:
    model = get_reranker()

    # the cross-encoder looks at the query and each chunk together, not independently,
    # which is what makes it more accurate than dense/bm25 but too slow to run over
    # the whole corpus, hence only running it on an already-narrowed candidate list
    pairs = [(query, chunk.text) for chunk in chunks]
    scores = model.predict(pairs)  # higher score means more relevant, unlike distance

    scored = list(zip(chunks, scores))
    scored.sort(key=lambda pair: pair[1], reverse=True)

    return scored[:k]
