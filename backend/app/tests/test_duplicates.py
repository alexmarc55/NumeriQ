from app.db.session import SessionLocal
from app.agents.anomaly_detector import find_duplicates


print("Testing find_duplicates function...")
print(find_duplicates(SessionLocal(), company_id=1))