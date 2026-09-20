from pydantic import BaseModel

class TransactionLineOut(BaseModel):
    cont: str
    tip: str
    suma: float

    class Config:
        from_attributes = True

class ReviewItem(BaseModel):
    document_id: int
    transaction_id: int
    doc_type: str | None
    status: str
    necesita_verificare: bool
    validation_flags: list[str] | None
    observatii: str | None
    lines: list[TransactionLineOut]

    class Config:
        from_attributes = True