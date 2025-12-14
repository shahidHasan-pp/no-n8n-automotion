
from sqlalchemy.orm import Session
from app.crud import subscription as subscription_crud
from app.models.subscription import Subscription
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate

class SubscriptionService:
    def get_user_subscription(self, db: Session, user_id: int) -> Subscription:
        # This assumes logic to find subscription by user_id, 
        # normally via user relationship or if Subscription had user_id. 
        # But based on current model User->Subscription ID.
        pass 
        # Logic to help add things to subs_list etc.
        # Since I haven't implemented explicit backref lookup helper in CRUD yet, 
        # this might just be a placeholder for business logic validation.

    def add_package_to_user(self, db: Session, subscription_id: int, package_details: dict) -> Subscription:
        sub = subscription_crud.get(db, subscription_id)
        if not sub:
            raise ValueError("Subscription holder not found")
        
        # Update logic: append to subs_list (which is a list of dicts/enums)
        current_list = list(sub.subs_list) if sub.subs_list else []
        current_list.append(package_details)
        
        # SQLAlchemy JSON change tracking can be tricky, reassigning helps
        update_data = SubscriptionUpdate(subs_list=current_list)
        return subscription_crud.update(db, db_obj=sub, obj_in=update_data)

subscription_service = SubscriptionService()
