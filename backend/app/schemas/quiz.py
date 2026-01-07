
from typing import Optional
from pydantic import BaseModel
from .base import BaseSchema
from .subscription import Subscription

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserSubscribedBase(BaseModel):
    user_id: int
    subs_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class UserSubscribedCreate(UserSubscribedBase):
    pass

class UserSubscribed(UserSubscribedBase, BaseSchema):
    pass

class PlayedQuizBase(BaseModel):
    score: int = 0
    time: Optional[int] = None
    user_id: int
    subs_id: Optional[int] = None

class PlayedQuizCreate(PlayedQuizBase):
    pass

class PlayedQuizUpdate(PlayedQuizBase):
    pass

class PlayedQuiz(PlayedQuizBase, BaseSchema):
    subscription: Optional[Subscription] = None

class WebhookQuizCreate(BaseModel):
    username: str
    subs: str
    score: int = 0
    time: Optional[int] = None

class WebhookUserSubscribedCreate(BaseModel):
    username: str
    subs: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
