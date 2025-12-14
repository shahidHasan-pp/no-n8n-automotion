
from typing import Optional
from pydantic import BaseModel
from .base import BaseSchema
from .subscription import Subscription

class QuizBase(BaseModel):
    score: int = 0
    time: Optional[int] = None
    user_id: int
    subs_id: Optional[int] = None

class QuizCreate(QuizBase):
    pass

class QuizUpdate(QuizBase):
    pass

class Quiz(QuizBase, BaseSchema):
    subscription: Optional[Subscription] = None
