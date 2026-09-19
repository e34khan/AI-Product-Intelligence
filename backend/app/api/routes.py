from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models import Product
from app.db.session import SessionLocal
from app.generation.answer import generate_answer
from app.retrieval.dense import retrieve
from app.schemas.ask import AskRequest, AskResponse, EvidenceItem

router = APIRouter()


def get_session():
    # one session per request. yield hands it to the route function, then the
    # code after yield runs once that request is done, closing it either way
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest, session: Session = Depends(get_session)):
    product = session.query(Product).filter(Product.external_id == request.product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail=f"no product with id {request.product_id}")

    results = retrieve(session, request.question, product_id=product.id, k=5)
    answer = generate_answer(request.question, results)

    # numbered the same way generate_answer numbered them internally, so these
    # entries line up with the [n] citations inside the answer text
    evidence = [
        EvidenceItem(number=i, text=chunk.text, distance=distance)
        for i, (chunk, distance) in enumerate(results, start=1)
    ]

    return AskResponse(answer=answer, evidence=evidence)
