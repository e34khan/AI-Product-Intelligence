from app.db.models import Document as DocumentRow  # renamed to avoid confusion with ingestion.models.Document
from app.db.models import Product
from app.db.session import SessionLocal
from app.ingestion.adapters.static_dataset import StaticDatasetAdapter

DATA_PATH = "app/ingestion/data/laptop_reviews.jsonl"

PRODUCTS = [
    ("B08157248B", "Mid 2019 Apple MacBook Air with 1.6GHz Intel Core i5 (13 inch, 8GB RAM, 256GB) Silver (Renewed)"),
    ("B01GO1T2TS", "2016 HP 15.6 Inch Premium Laptop PC, AMD Quad-Core APU 2.0GHz Processor, 4GB DDR3 RAM, 500GB HDD, Radeon R4 Graphics, SuperMulti DVD Burner, HDMI, Windows 10"),
    ("B076DKFYF9", "Dell Latitude E7450 14in HD High Performance Ultra Book Business Laptop NoteBook (Intel Dual Core i5 5300U, 8GB Ram, 256GB Solid State SSD, Camera, HDMI, WIFI) Win 10 Pro (Renewed)"),
    ("B0BY2Y5T1J", "ASUS ROG Strix G15 Gaming Laptop, 240Hz 15.6\" FHD 3ms IPS, Intel Core i7-10750H CPU, NVIDIA GeForce RTX 2070, 16GB DDR4, 1TB PCIe SSD, RGB KB, Wi-Fi 6, Windows 10, G512LW-ES76"),
    ("B09H5Z36S1", "Microsoft Surface Laptop Studio - 14.4\" Touchscreen - Intel Core i7 - 32GB Memory - 2TB SSD - Platinum"),
]


def main() -> None:
    adapter = StaticDatasetAdapter(DATA_PATH)
    session = SessionLocal()

    for external_id, title in PRODUCTS:
        product = Product(external_id=external_id, title=title, source="static_dataset")
        session.add(product)
        session.flush()  # sends the insert now so product.id gets filled in, without committing yet

        documents = adapter.fetch(external_id)
        for doc in documents:
            session.add(DocumentRow(
                product_id=product.id,  # links this row back to its product
                source=doc.source,
                document_type=doc.document_type,
                title=doc.title,
                text=doc.text,
                rating=doc.rating,
                review_timestamp=doc.timestamp,  # renamed from doc.timestamp to match the column name
                verified_purchase=doc.verified_purchase,
            ))

        print(f"{external_id}: inserted {len(documents)} documents")

    session.commit()  # saves everything from all 5 products at once
    session.close()


if __name__ == "__main__":
    main()
