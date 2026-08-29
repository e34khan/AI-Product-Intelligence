from sqlalchemy.orm import Session

from app.db.models import Chunk
from app.nlp.embeddings import embed_texts


def retrieve(session: Session, query: str, product_id: int | None = None, k: int = 5) -> list[tuple[Chunk, float]]:
    # embed_texts expects a list since the model can batch many texts at once,
    # so we wrap the single query in a list and take the first (only) result back out
    query_vector = embed_texts([query])[0]

    # cosine_distance returns a value per row, smaller means more similar.
    # label it "distance" so we can order by it and also read it back per result
    distance = Chunk.embedding.cosine_distance(query_vector).label("distance")
    results = session.query(Chunk, distance)

    if product_id is not None:
        results = results.filter(Chunk.product_id == product_id)

    results = results.order_by(distance).limit(k)

    return results.all()
