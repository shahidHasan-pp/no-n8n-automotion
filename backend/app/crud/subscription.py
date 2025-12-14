from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.subscription import Subscription
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate

class CRUDSubscription(CRUDBase[Subscription, SubscriptionCreate, SubscriptionUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Subscription]:
        return db.query(Subscription).filter(Subscription.name == name).first()

subscription = CRUDSubscription(Subscription)
