
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.crud import user as user_crud
from app.crud import subscription as subscription_crud
from app.crud import quiz as quiz_crud
from app.crud import user_subscribed as user_sup_crud
from app.schemas.quiz import UserSubscribedCreate, UserSubscribed

class SubscriptionService:
    def subscribe_user(
        self, 
        db: Session, 
        username: str, 
        subscription_name: str
    ) -> UserSubscribed:
        
        # 1. Get User
        user = user_crud.get_by_username(db, username=username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # 2. Get Subscription
        sub = subscription_crud.get_by_name(db, name=subscription_name)
        if not sub:
            # Try by ID
            try:
                sub_id = int(subscription_name)
                sub = subscription_crud.get(db, id=sub_id)
            except ValueError:
                pass
                
        if not sub:
            raise HTTPException(status_code=404, detail="Subscription not found")

        # 3. Calculate subscription period
        start_date = datetime.utcnow()
        
        # Calculate end_date based on subscription duration
        if sub.time == "MONTHLY":
            end_date = start_date + timedelta(days=30)
        elif sub.time == "YEARLY":
            end_date = start_date + timedelta(days=365)
        elif sub.time == "LIFETIME":
            end_date = start_date + timedelta(days=36500)
        else:
            end_date = start_date + timedelta(days=30)

        # 4. Create UserSubscribed with dates
        user_sub_in = UserSubscribedCreate(
            user_id=user.id, 
            subs_id=sub.id,
            start_date=start_date,
            end_date=end_date
        )
        user_sub = user_sup_crud.create(db, obj_in=user_sub_in)
        
        # 5. Update user's subscription_id field
        user.subscription_id = sub.id
        db.add(user)
        
        # 6. Increment Subscription Quantity
        sub.current_subs_quantity += 1
        db.add(sub)
        
        db.commit()
        db.refresh(sub)
        db.refresh(user)
        
        return user_sub

subscription_service = SubscriptionService()
