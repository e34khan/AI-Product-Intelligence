from app.db.session import SessionLocal
from app.retrieval.dense import retrieve

QUERY = "does the battery drain fast"


def main() -> None:
    session = SessionLocal()

    # no product_id filter here, so this searches across all 5 products at once
    results = retrieve(session, QUERY, k=5)

    print(f"query: {QUERY}\n")
    for chunk, distance in results:
        print(f"distance={distance:.4f} product_id={chunk.product_id}")
        print(chunk.text)
        print()

    session.close()


if __name__ == "__main__":
    main()
