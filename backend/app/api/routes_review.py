from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.db.session import get_db
from app.models.document import Document
from app.models.transaction import Transaction
from app.schemas.review import ReviewItem
from app.agents.anomaly_detector import find_duplicates, calculate_z_score, check_new_suppliers
from app.ml.anomaly_model import detect_statistical_outliers

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

@router.get("/anomaly/{company_id}")
def get_anomalies(company_id: int, db: Session = Depends(get_db)):
    duplicates = find_duplicates(db, company_id)
    z_scores = calculate_z_score(db, company_id)
    new_suppliers = check_new_suppliers(db, company_id)
    statistical_outliers = detect_statistical_outliers(db, company_id)

    result = {"duplicates": duplicates, "z_scores": [z for z in z_scores if z.get("is_anomaly")], "new_suppliers": [n for n in new_suppliers if n.get("is_new_supplier")], "statistical_outliers": [s for s in statistical_outliers if s.get("is_anomaly")]}
    return result