"""
Script to fix messenger data in database
Converts empty arrays [] to empty objects {}
"""

from app.database.session import SessionLocal
from app.models.messenger import Messenger
from sqlalchemy import text

def fix_messenger_data():
    """Fix messenger records with empty arrays"""
    db = SessionLocal()
    
    try:
        # Get all messenger records
        messengers = db.query(Messenger).all()
        
        fixed_count = 0
        for messenger in messengers:
            needs_update = False
            
            # Check and fix each field
            if messenger.mail is None or messenger.mail == []:
                messenger.mail = {}
                needs_update = True
                
            if messenger.telegram is None or messenger.telegram == []:
                messenger.telegram = {}
                needs_update = True
                
            if messenger.whatsapp is None or messenger.whatsapp == []:
                messenger.whatsapp = {}
                needs_update = True
                
            if messenger.discord is None or messenger.discord == []:
                messenger.discord = {}
                needs_update = True
            
            if needs_update:
                fixed_count += 1
                print(f"Fixed messenger ID: {messenger.id}")
        
        db.commit()
        print(f"\n✅ Fixed {fixed_count} messenger records")
        print(f"Total messenger records: {len(messengers)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🔧 Fixing messenger data...")
    fix_messenger_data()
