from sqlalchemy.orm import Session
from sqlalchemy import func, tuple_
from app.models.transaction import Transaction, TransactionLine
from app.models.document import Document
from app.ml.anomaly_model import detect_anomalies


def run_anomaly_detection(db: Session, company_id: int) -> list[dict]:
    rows = (
        db.query(Transaction, Document)
        .join(Document, Transaction.document_id == Document.id)
        .filter(Document.company_id == company_id)
        .all()
    )

    data = []
    for tx, doc in rows:
        total = sum(l.suma for l in tx.lines if l.tip == "debit")
        data.append({
            "transaction_id": tx.id,
            "suma_totala": float(total),
            "doc_type": doc.doc_type,
        })

    return detect_anomalies(data)

def find_duplicates(db: Session, company_id: int) -> list[dict]:
    rows = (
        db.query(Document.supplier, Document.total_amount, func.count(Document.id).label("count"))
        .filter(
            Document.company_id == company_id,
            Document.supplier.isnot(None),
            Document.total_amount.isnot(None),
            Document.document_date.isnot(None)
        )
        .group_by(Document.supplier, Document.total_amount)
        .having(func.count(Document.id) > 1)
        .all()
    )

    row_id = (
        db.query(Document.id, Document.supplier, Document.total_amount, Document.document_date)
        .filter(
            Document.company_id == company_id,
            Document.supplier.isnot(None),
            Document.total_amount.isnot(None),
            Document.document_date.isnot(None)
        )
        .where(tuple_(Document.supplier, Document.total_amount).in_([(row.supplier, row.total_amount) for row in rows]))
        .all()
    )

    count_by_group = {
        (r.supplier, r.total_amount): r.count
        for r in rows
    }

    result = []
    for r in row_id:
        key = (r.supplier, r.total_amount)
        result.append({
            "document_id": r.id,
            "supplier": r.supplier,
            "total_amount": float(r.total_amount),
            "document_date": r.document_date.isoformat(),
            "duplicate_group_size": count_by_group.get(key),
        })

    return result