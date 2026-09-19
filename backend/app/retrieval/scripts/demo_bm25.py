from app.db.session import SessionLocal
from app.retrieval.bm25 import build_index

QUERY = "does the battery drain fast"


def main() -> None:
    session = SessionLocal()

    # builds the index fresh from whatever is currently in the chunks table.
    # fine for our small corpus, no need to persist or cache it yet
    index = build_index(session)
    results = index.search(QUERY, k=5)

    print(f"query: {QUERY}\n")
    for chunk_id, score in results:
        print(f"score={score:.4f} chunk_id={chunk_id}")
        print(index.text_by_id[chunk_id])
        print()

    session.close()


if __name__ == "__main__":
    main()
