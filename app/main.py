from fastapi import FastAPI
from app.api import routes_documents, routes_review
from app import models

app = FastAPI()
app.include_router(routes_documents.router)
app.include_router(routes_review.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}