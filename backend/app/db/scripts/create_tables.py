from app.db.base import Base
from app.db.models import Chunk, Document, Product  # noqa: F401 (this import registers the models on Base)
from app.db.session import engine


def main() -> None:
    Base.metadata.create_all(engine)
    print("tables created")


if __name__ == "__main__":
    main()
