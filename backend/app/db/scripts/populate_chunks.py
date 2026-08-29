from app.db.models import Chunk, Document
from app.db.session import SessionLocal
from app.nlp.chunking import chunk_text


def main() -> None:
    session = SessionLocal()

    # load every review we already inserted, so we can chunk each one
    documents = session.query(Document).all()

    total_chunks = 0
    for document in documents:
        pieces = chunk_text(document.text)

        # chunk_index records where each piece sits within its source document,
        # since one document can produce multiple chunk rows
        for index, piece in enumerate(pieces):
            session.add(Chunk(
                document_id=document.id,
                product_id=document.product_id,
                chunk_index=index,
                text=piece,
                embedding=None,  # filled in later once we run the embedding model
            ))
            total_chunks += 1

    session.commit()
    session.close()

    print(f"documents: {len(documents)}")
    print(f"chunks: {total_chunks}")


if __name__ == "__main__":
    main()
