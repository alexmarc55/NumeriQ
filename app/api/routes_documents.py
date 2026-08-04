import shutil
import os
from fastapi import APIRouter, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.document import Document
from app.schemas.document import DocumentResponse
from app.models.company import Company
from app.orchestrator.graph import Orchestrator
from app.models.transaction import Transaction, TransactionLine

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = "app/uploads"

orchestrator = Orchestrator()

@router.post("/upload", response_model=DocumentResponse)
def upload_document(company_id: int, file: UploadFile, db: Session = Depends(get_db)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    doc = Document(company_id=company_id, file_path=file_path, status="uploaded")
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

@router.get("/", response_model=list[DocumentResponse])
def list_documents(company_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Document)
    if company_id:
        query = query.filter(Document.company_id == company_id)
    return query.all()

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.post("/{document_id}/classify", response_model=DocumentResponse)
def classify(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    company = db.query(Company).filter(Company.id == doc.company_id).first()

    result_state = orchestrator.run(
        document_id=doc.id, file_path=doc.file_path, company_cui=company.cui
    )

    if result_state.errors:
        raise HTTPException(status_code=500, detail="; ".join(result_state.errors))

    if result_state.proposed_entry:
        entry = result_state.proposed_entry

        transaction = Transaction(
            document_id=doc.id,
            necesita_verificare=entry.get("necesita_verificare", False),
            observatii=entry.get("observatii"),
            validation_flags=result_state.validation_flags or None,
        )
        db.add(transaction)
        db.flush()

        for linie in entry.get("linii", []):
            db.add(TransactionLine(
                transaction_id=transaction.id,
                cont=linie["cont"],
                tip=linie["tip"],
                suma=linie["suma"],
            ))

    doc.doc_type = result_state.doc_type
    doc.status = result_state.status
    db.commit()
    db.refresh(doc)
    return doc