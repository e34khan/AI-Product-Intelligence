from abc import ABC, abstractmethod

from app.ingestion.models import Document


class SourceAdapter(ABC):
    # ABC plus abstractmethod means any subclass that skips implementing fetch()
    # fails immediately when instantiated, instead of failing later when called
    @abstractmethod
    def fetch(self, product_id: str) -> list[Document]:
        """Return all documents this source has for the given product."""
        raise NotImplementedError
