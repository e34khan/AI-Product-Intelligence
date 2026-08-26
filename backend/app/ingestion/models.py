from dataclasses import dataclass


@dataclass
class Document:
    text: str
    source: str
    product_id: str
    document_type: str
    title: str | None = None
    rating: float | None = None
    timestamp: int | None = None
    verified_purchase: bool | None = None
