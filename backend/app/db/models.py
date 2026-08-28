from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

EMBEDDING_DIM = 384  # all-MiniLM-L6-v2's output size


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    title: Mapped[str] = mapped_column(String)
    source: Mapped[str] = mapped_column(String)


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    source: Mapped[str] = mapped_column(String)
    document_type: Mapped[str] = mapped_column(String)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    text: Mapped[str] = mapped_column(Text)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    review_timestamp: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    verified_purchase: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    # duplicated from documents.product_id on purpose so retrieval queries can filter by
    # product without joining through documents first
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    chunk_index: Mapped[int] = mapped_column(Integer)  # position of this chunk within its document
    text: Mapped[str] = mapped_column(Text)
    # nullable because we insert the chunk's text first and fill this in once we run the embedding model
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
