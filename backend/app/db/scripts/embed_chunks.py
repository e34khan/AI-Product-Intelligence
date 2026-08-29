from app.db.models import Chunk
from app.db.session import SessionLocal
from app.nlp.embeddings import embed_texts


def main() -> None:
    session = SessionLocal()

    # only chunks without an embedding yet, so rerunning this script later
    # (e.g. after adding more products) only embeds what's actually new
    chunks = session.query(Chunk).filter(Chunk.embedding.is_(None)).all()

    if not chunks:
        print("nothing to embed")
        return

    texts = [chunk.text for chunk in chunks]
    vectors = embed_texts(texts)

    # zip pairs each chunk with its matching vector by position, since
    # embed_texts returns vectors in the same order the texts were given
    for chunk, vector in zip(chunks, vectors):
        chunk.embedding = vector

    session.commit()
    session.close()

    print(f"embedded {len(chunks)} chunks")


if __name__ == "__main__":
    main()
