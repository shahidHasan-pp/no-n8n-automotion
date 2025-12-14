
from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel
from app.models.enums import QuizType, SubscriptionType, SubscriptionLength
from .base import BaseSchema

# Subscription Schemas matches the single table requirement
class SubscriptionBase(BaseModel):
    name: str
    type: SubscriptionType
    time: SubscriptionLength
    offer: Optional[str] = None
    prize: Optional[str] = None
    remark: List[Any] = []
    amount: Optional[int] = None
    link: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(SubscriptionBase):
    pass

class Subscription(SubscriptionBase, BaseSchema):
    current_subs_quantity: int = 0
