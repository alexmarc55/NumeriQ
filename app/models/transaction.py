from sqlalchemy import String, ForeignKey, Numeric, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    necesita_verificare: Mapped[bool] = mapped_column(default=False)
    observatii: Mapped[str | None] = mapped_column(String(500), nullable=True)
    validation_flags: Mapped[list | None] = mapped_column(JSON, nullable=True) 

    lines: Mapped[list["TransactionLine"]] = relationship(back_populates="transaction", cascade="all, delete-orphan")


class TransactionLine(Base):
    __tablename__ = "transaction_lines"

    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"))
    cont: Mapped[str] = mapped_column(String(20))
    tip: Mapped[str] = mapped_column(String(10))  # "debit" sau "credit"
    suma: Mapped[float] = mapped_column(Numeric(12, 2))

    transaction: Mapped["Transaction"] = relationship(back_populates="lines")