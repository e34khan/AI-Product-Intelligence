from dataclasses import dataclass


# the common shape every adapter returns, regardless of what source it reads from
@dataclass
class Document:
    text: str
    source: str
    product_id: str
    document_type: str
    # everything below is optional since not every source will have it (a spec page has no rating)
    title: str | None = None
    rating: float | None = None
    timestamp: int | None = None
    verified_purchase: bool | None = None
