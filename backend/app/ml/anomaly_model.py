import pandas as pd
from sklearn.ensemble import IsolationForest
from sqlalchemy.orm import Session

from app.models.document import Document

def detect_statistical_outliers(db: Session, company_id) -> list[dict]:

    rows = (
        db.query(Document)
        .filter(Document.company_id == company_id)
        .filter(Document.total_amount.isnot(None))
        .all()
    )

    df = pd.DataFrame([{
        "document_id": row.id,
        "total_amount": float(row.total_amount),
    } for row in rows])


    if len(df) < 5:
        df['anomaly_score'] = None
        df['is_anomaly'] = False
        return df.to_dict(orient='records')

    x = df[["total_amount"]]

    model = IsolationForest(contamination=0.1, random_state=42)
    predictions = model.fit_predict(x)
    scores = model.decision_function(x)

    df['is_anomaly'] = predictions == -1
    df['anomaly_score'] = scores

    return df.to_dict(orient='records')
