import pandas as pd
from sklearn.ensemble import IsolationForest

def detect_anomalies(transactions: list[dict]) -> list[dict]:

    if len(transactions) < 5:
        for t in transactions:
            t['anomaly_score'] = None
            t['is_anomaly'] = False

    df = pd.DataFrame(transactions)

    x = df[["suma_totala"]]

    model = IsolationForest(contamination=0.1, random_state=42)
    predictions = model.fit_predict(x)
    scores = model.decision_function(x)

    df['is_anomaly'] = predictions == -1
    df['anomaly_score'] = scores

    return df.to_dict(orient='records')
