from abc import ABC, abstractmethod

from app.ingestion.models import Document


class SourceAdapter(ABC):
    @abstractmethod
    def fetch(self, product_id: str) -> list[Document]:
        """Return all documents this source has for the given product."""
        raise NotImplementedError
