import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    # Simple approach: Get all user_subscribed records where user.subscription_id is NULL
    find_query = text("""
        SELECT u.id, u.username, us.subs_id, s.name
        FROM users u
        JOIN user_subscribed us ON u.id = us.user_id
        JOIN subscriptions s ON us.subs_id = s.id
        WHERE u.subscription_id IS NULL
    """)
    
    records = db.execute(find_query).fetchall()
    
    print(f"Found {len(records)} subscription records for users without subscription_id...")
    
    # Update each user with their subscription (take first one if multiple)
    updated_users = set()
    count = 0
    
    for user_id, username, subs_id, sub_name in records:
        if user_id not in updated_users:
            update_query = text("UPDATE users SET subscription_id = :subs_id WHERE id = :user_id")
            db.execute(update_query, {"user_id": user_id, "subs_id": subs_id})
            updated_users.add(user_id)
            count += 1
            print(f"  ✓ Updated {username} (ID: {user_id}) → {sub_name} (ID: {subs_id})")
    
    db.commit()
    print(f"\n✅ Updated {count} users!")
    
    # Verify final state
    verify_query = text("""
        SELECT u.id, u.username, u.subscription_id, s.name
        FROM users u
        LEFT JOIN subscriptions s ON u.subscription_id = s.id
    """)
    
    all_users = db.execute(verify_query).fetchall()
    print(f"\n📊 All Users Status:")
    for user in all_users:
        status = f"{user[3]} (ID: {user[2]})" if user[2] else "No Subscription"
        print(f"  - {user[1]} (ID: {user[0]}) → {status}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
