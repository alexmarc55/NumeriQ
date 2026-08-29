from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.db.session import get_db
from app.models.document import Document
from app.models.transaction import Transaction
from app.schemas.review import ReviewItem
from backend.app.agents.anomaly_detector import run_anomaly_detection

router = APIRouter(prefix="/review", tags=["review"])


@router.get("/pending", response_model=list[ReviewItem])
def list_pending(db: Session = Depends(get_db)):
    docs = (
        db.query(Document)
        .filter(Document.status == "needs_review")
        .options(joinedload(Document.transactions).joinedload(Transaction.lines))
        .all()
    )

    items = []
    for doc in docs:
        for tx in doc.transactions:
            items.append(ReviewItem(
                document_id=doc.id,
                transaction_id=tx.id,
                doc_type=doc.doc_type,
                status=doc.status,
                necesita_verificare=tx.necesita_verificare,
                validation_flags=tx.validation_flags,
                observatii=tx.observatii,
                lines=tx.lines,
            ))
    return items


@router.post("/{transaction_id}/approve")
def approve(transaction_id: int, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    doc = db.query(Document).filter(Document.id == tx.document_id).first()
    doc.status = "approved"
    tx.necesita_verificare = False
    db.commit()
    return {"status": "approved", "document_id": doc.id}


@router.post("/{transaction_id}/reject")
def reject(transaction_id: int, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    doc = db.query(Document).filter(Document.id == tx.document_id).first()
    doc.status = "rejected"
    db.commit()
    return {"status": "rejected", "document_id": doc.id}

@router.get("/anomalies/{company_id}")
def get_anomalies(company_id: int, db: Session = Depends(get_db)):
    results = run_anomaly_detection(db, company_id)
    return [r for r in results if r.get("is_anomaly")]