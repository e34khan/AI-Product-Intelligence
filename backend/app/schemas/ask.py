from pydantic import BaseModel


class AskRequest(BaseModel):
    product_id: str  # the external asin, not our internal database id
    question: str


class EvidenceItem(BaseModel):
    number: int  # matches the [n] citation number inside the answer text
    text: str
    distance: float


class AskResponse(BaseModel):
    answer: str
    evidence: list[EvidenceItem]
