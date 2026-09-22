from app.db.session import SessionLocal
from app.retrieval.bm25 import build_index
from app.retrieval.hybrid import hybrid_retrieve
from app.retrieval.rerank import rerank

QUERY = "does the battery drain fast"


def main() -> None:
    session = SessionLocal()

    bm25_index = build_index(session)

    # pull a wide candidate set from hybrid first, then rerank narrows it down further
    candidates = hybrid_retrieve(session, bm25_index, QUERY, k=20)
    chunks = [chunk for chunk, _score in candidates]

    results = rerank(QUERY, chunks, k=5)

    print(f"query: {QUERY}\n")
    for chunk, score in results:
        print(f"rerank_score={score:.4f} chunk_id={chunk.id} product_id={chunk.product_id}")
        print(chunk.text)
        print()

    session.close()


if __name__ == "__main__":
    main()
