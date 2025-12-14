
from typing import Optional
from pydantic import BaseModel, EmailStr
from .base import BaseSchema
from .messenger import Messenger
from .subscription import Subscription

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    phone_number: Optional[str] = None

class UserCreate(UserBase):
    messenger_id: Optional[int] = None
    subscription_id: Optional[int] = None
    # Optionally accept creating messenger/subscription inline, but for now keep it simple via IDs or update later.

class UserUpdate(UserBase):
    password: Optional[str] = None # Not handling auth yet, but standard pattern.
    messenger_id: Optional[int] = None
    subscription_id: Optional[int] = None

class User(UserBase, BaseSchema):
    messenger_id: Optional[int] = None
    subscription_id: Optional[int] = None
    messenger: Optional[Messenger] = None
    subscription: Optional[Subscription] = None
    active_subscriptions_count: int = 0  # Count of active subscriptions from user_subscribed table
    
    class Config:
        from_attributes = True
