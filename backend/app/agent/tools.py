from app.db.models import AspectSentiment, Product
from app.db.session import SessionLocal
from app.retrieval.bm25 import build_index
from app.retrieval.hybrid import hybrid_retrieve
from app.retrieval.rerank import rerank

# built once, lazily, and reused across tool calls within this process, same
# pattern as the model caching in embeddings.py and rerank.py
_bm25_index = None


def _get_bm25_index(session):
    global _bm25_index
    if _bm25_index is None:
        _bm25_index = build_index(session)
    return _bm25_index


def _resolve_product_id(session, external_id: str) -> int | None:
    product = session.query(Product).filter(Product.external_id == external_id).first()
    return product.id if product else None


def retrieve_reviews(product_id: str, question: str) -> str:
    """Retrieve relevant customer review excerpts for one product and a specific question."""
    session = SessionLocal()
    try:
        internal_id = _resolve_product_id(session, product_id)
        if internal_id is None:
            return f"No product found with id {product_id}"

        bm25_index = _get_bm25_index(session)
        # widen with hybrid, then rerank narrows to the 5 most precise matches,
        # same two-stage pattern as everywhere else in the retrieval pipeline
        wide_results = hybrid_retrieve(session, bm25_index, question, product_id=internal_id, k=20)
        chunks = [chunk for chunk, _score in wide_results]
        reranked = rerank(question, chunks, k=5)

        if not reranked:
            return "No relevant reviews found."

        return "\n\n".join(f"- {chunk.text}" for chunk, _score in reranked)
    finally:
        session.close()


def get_aspect_summary(product_id: str) -> str:
    """Get aggregated aspect-based sentiment counts (battery, display, keyboard, etc) for one product."""
    session = SessionLocal()
    try:
        internal_id = _resolve_product_id(session, product_id)
        if internal_id is None:
            return f"No product found with id {product_id}"

        rows = (
            session.query(AspectSentiment.aspect, AspectSentiment.sentiment)
            .filter(AspectSentiment.product_id == internal_id)
            .all()
        )

        if not rows:
            return "No aspect sentiment data found."

        # build a nested count: {aspect: {sentiment: count}}
        counts: dict[str, dict[str, int]] = {}
        for aspect, sentiment in rows:
            counts.setdefault(aspect, {}).setdefault(sentiment, 0)
            counts[aspect][sentiment] += 1

        lines = []
        for aspect, sentiments in counts.items():
            parts = ", ".join(f"{s}={n}" for s, n in sentiments.items())
            lines.append(f"{aspect}: {parts}")
        return "\n".join(lines)
    finally:
        session.close()
