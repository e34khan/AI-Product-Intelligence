from app.db.session import SessionLocal
from app.retrieval.bm25 import build_index
from app.retrieval.hybrid import hybrid_retrieve

QUERY = "does the battery drain fast"


def main() -> None:
    session = SessionLocal()

    # built once here, then reused across searches, since rebuilding it per
    # query would recompute term stats over all chunks every single time
    bm25_index = build_index(session)

    results = hybrid_retrieve(session, bm25_index, QUERY, k=5)

    print(f"query: {QUERY}\n")
    for chunk, score in results:
        print(f"rrf_score={score:.4f} chunk_id={chunk.id} product_id={chunk.product_id}")
        print(chunk.text)
        print()

    session.close()


if __name__ == "__main__":
    main()
