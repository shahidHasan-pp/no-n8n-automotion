import sys
import os
from sqlalchemy import text

# Add parent dir to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.session import SessionLocal

def seed():
    db = SessionLocal()
    try:
        with open("scripts/dummy_seed.sql", "r") as f:
            sql_script = f.read()
        
        # Split statements by ; and execute empty check
        statements = sql_script.split(';')
        for statement in statements:
            if statement.strip():
                try:
                    db.execute(text(statement))
                    db.commit() # Commit immediately
                    print(f"Executed: {statement[:50]}...")
                except Exception as e:
                     db.rollback() # Rollback this failed statement
                     print(f"Skipping/Error: {e}")
        
        db.commit()
        print("Seeding completed successfully.")
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
