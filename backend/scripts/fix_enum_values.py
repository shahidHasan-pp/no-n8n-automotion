import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    db.execute(text("UPDATE subscriptions SET time = 'MONTHLY' WHERE time = 'Monthly'"))
    db.execute(text("UPDATE subscriptions SET time = 'YEARLY' WHERE time = 'Yearly'"))
    db.execute(text("UPDATE subscriptions SET time = 'LIFETIME' WHERE time = 'Lifetime'"))
    db.commit()
    print("Database values updated to uppercase!")
    
    # Verify
    result = db.execute(text('SELECT id, name, time FROM subscriptions')).fetchall()
    print("\nVerified values:")
    for r in result:
        print(f"  {r[1]}: {r[2]}")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
