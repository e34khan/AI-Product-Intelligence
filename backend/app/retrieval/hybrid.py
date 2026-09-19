from collections import defaultdict

from sqlalchemy.orm import Session

from app.db.models import Chunk
from app.retrieval.bm25 import BM25Index
from app.retrieval.dense import retrieve

RRF_K = 60  # standard default from the original reciprocal rank fusion paper


def hybrid_retrieve(
    session: Session,
    bm25_index: BM25Index,
    query: str,
    product_id: int | None = None,
    k: int = 5,
    candidates: int = 20,
) -> list[tuple[Chunk, float]]:
    # pull a wider candidate set from each method first, then fuse and narrow
    # down to k, same two-stage shape we'll reuse later for reranking
    dense_results = retrieve(session, query, product_id=product_id, k=candidates)
    bm25_results = bm25_index.search(query, k=candidates, product_id=product_id)

    # reciprocal rank fusion: combine using each method's RANK position, not its
    # raw score, since dense distances (roughly 0 to 1) and bm25 scores (roughly
    # 8 to 13 here) are not on comparable scales
    rrf_scores = defaultdict(float)

    for rank, (chunk, _distance) in enumerate(dense_results, start=1):
        rrf_scores[chunk.id] += 1 / (RRF_K + rank)

    for rank, (chunk_id, _score) in enumerate(bm25_results, start=1):
        rrf_scores[chunk_id] += 1 / (RRF_K + rank)

    top_ids = sorted(rrf_scores.items(), key=lambda pair: pair[1], reverse=True)[:k]

    # fetch the winning chunks in one query, then rebuild the rrf-ranked order
    # since sql's IN clause does not promise to preserve the order we ask in
    chunk_ids = [chunk_id for chunk_id, _ in top_ids]
    chunks_by_id = {c.id: c for c in session.query(Chunk).filter(Chunk.id.in_(chunk_ids)).all()}

    return [(chunks_by_id[chunk_id], score) for chunk_id, score in top_ids]
