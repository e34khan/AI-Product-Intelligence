import json
from pathlib import Path

from app.ingestion.base import SourceAdapter
from app.ingestion.models import Document


class StaticDatasetAdapter(SourceAdapter):
    def __init__(self, data_path: Path | str):
        self.data_path = Path(data_path)

    def fetch(self, product_id: str) -> list[Document]:
        documents = []

        with open(self.data_path, encoding="utf-8") as f:
            for line in f:
                item = json.loads(line)

                if item.get("parent_asin") != product_id:
                    continue

                documents.append(Document(
                    text=item.get("text", ""),
                    source="static_dataset",
                    product_id=product_id,
                    document_type="review",
                    title=item.get("title"),
                    rating=item.get("rating"),
                    timestamp=item.get("timestamp"),
                    verified_purchase=item.get("verified_purchase"),
                ))

        return documents
