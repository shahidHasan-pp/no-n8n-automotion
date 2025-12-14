import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    result = db.execute(text("SHOW COLUMNS FROM subscriptions LIKE 'time'")).fetchone()
    print(f"Column 'time' definition: {result}")
    print(f"\nType: {result[1]}")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
