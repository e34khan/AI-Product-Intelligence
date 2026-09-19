from app.db.models import Chunk, Document
from app.db.session import SessionLocal
from app.nlp.cleaning import clean_text


def main() -> None:
    session = SessionLocal()

    # order by id so "keep the first occurrence" means the earliest inserted row,
    # matching what we manually inspected earlier
    documents = session.query(Document).order_by(Document.id).all()

    seen = set()  # (product_id, cleaned_text) pairs we've already kept one copy of
    to_delete = []
    cleaned_count = 0

    for document in documents:
        cleaned = clean_text(document.text)

        if cleaned != document.text:
            cleaned_count += 1

        if not cleaned:
            to_delete.append(document)  # nothing left, e.g. a review that was only whitespace
            continue

        key = (document.product_id, cleaned)
        if key in seen:
            to_delete.append(document)  # duplicate of an earlier review for the same product
            continue

        seen.add(key)
        document.text = cleaned  # keep this one, with the cleaned text saved

    # existing chunks were built from the old, dirty text, so none of them are
    # trustworthy anymore. delete all of them now and regenerate from scratch after
    session.query(Chunk).delete()

    for document in to_delete:
        session.delete(document)

    session.commit()
    session.close()

    print(f"cleaned text on {cleaned_count} documents")
    print(f"deleted {len(to_delete)} documents (duplicates or empty after cleaning)")


if __name__ == "__main__":
    main()
