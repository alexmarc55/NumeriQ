from app.db.session import SessionLocal
from app.agents.anomaly_detector import calculate_z_score


print("Testing calculate_z_score function...")
print(calculate_z_score(SessionLocal(), company_id=1))