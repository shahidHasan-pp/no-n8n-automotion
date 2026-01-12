
from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, validator
from app.models.enums import QuizType, SubscriptionType, SubscriptionLength, PlatformType
from .base import BaseSchema

# Subscription Schemas matches the single table requirement
class SubscriptionBase(BaseModel):
    name: str
    type: Optional[SubscriptionType] = None
    time: Optional[SubscriptionLength] = None
    platform: Optional[PlatformType] = None
    offer: Optional[str] = None
    prize: Optional[str] = None
    remark: Optional[List[Any]] = []
    amount: Optional[int] = None
    link: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    @validator('remark', pre=True)
    def default_remark_if_none(cls, v):
        if v is None:
            return []
        return v

    @validator('type', pre=True)
    def upper_case_type(cls, v):
        if isinstance(v, str):
            return v.upper()
        return v
        
    @validator('time', pre=True)
    def upper_case_time(cls, v):
        if isinstance(v, str):
            return v.upper()
        return v

    @validator('platform', pre=True)
    def lower_case_platform(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(SubscriptionBase):
    pass

class Subscription(SubscriptionBase, BaseSchema):
    current_subs_quantity: Optional[int] = 0
