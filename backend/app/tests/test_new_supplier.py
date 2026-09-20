from app.db.session import SessionLocal
from app.agents.anomaly_detector import check_new_suppliers


print("Testing check_new_suppliers function...")
print(check_new_suppliers(SessionLocal(), company_id=1))