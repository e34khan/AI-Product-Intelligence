from app.ingestion.adapters.static_dataset import StaticDatasetAdapter

MACBOOK_AIR_ASIN = "B08157248B"  # just a real product id to prove fetch() actually works


def main() -> None:
    adapter = StaticDatasetAdapter("app/ingestion/data/laptop_reviews.jsonl")
    documents = adapter.fetch(MACBOOK_AIR_ASIN)

    print(f"fetched {len(documents)} documents for {MACBOOK_AIR_ASIN}")
    print(documents[0])


if __name__ == "__main__":
    main()
