from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    file_path: Mapped[str] = mapped_column(String(500))
    doc_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # completed by Agent 1
    status: Mapped[str] = mapped_column(String(50), default="uploaded")     # uploaded / classified / approved / rejected
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    transactions: Mapped[list["Transaction"]] = relationship(backref="document")