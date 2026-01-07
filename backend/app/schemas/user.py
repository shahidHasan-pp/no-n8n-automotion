
from typing import Optional
from pydantic import BaseModel, EmailStr, validator
from .base import BaseSchema
from .messenger import Messenger
from .subscription import Subscription

class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    quizard: bool = False
    wordly: bool = False
    arcaderush: bool = False

    @validator('email', 'full_name', 'phone_number', pre=True)
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

    @validator('quizard', 'wordly', 'arcaderush', pre=True)
    def default_bool(cls, v):
        if v is None:
            return False
        return v

class UserCreate(UserBase):
    messenger_id: Optional[int] = None
    # Optionally accept creating messenger/subscription inline, but for now keep it simple via IDs or update later.

class UserUpdate(UserBase):
    password: Optional[str] = None # Not handling auth yet, but standard pattern.
    messenger_id: Optional[int] = None

class UserCheck(BaseModel):
    username: str

class UserPlatformUpdate(BaseModel):
    username: str
    platform: str

class User(UserBase, BaseSchema):
    messenger_id: Optional[int] = None
    messenger: Optional[Messenger] = None
    active_subscriptions_count: int = 0  # Count of active subscriptions from user_subscribed table
    
    class Config:
        from_attributes = True
