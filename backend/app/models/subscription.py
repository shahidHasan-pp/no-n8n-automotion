
from sqlalchemy import Column, String, Integer, JSON, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from .base_model import BaseModel
from .enums import QuizType, SubscriptionType, SubscriptionLength, PlatformType

class Subscription(BaseModel):
    __tablename__ = "subscriptions"
    
    name = Column(String(255), nullable=False)
    type = Column(SQLEnum(SubscriptionType), nullable=True)
    time = Column(SQLEnum(SubscriptionLength), nullable=True)
    platform = Column(SQLEnum(PlatformType), nullable=True)
    offer = Column(String(255), nullable=True)
    prize = Column(String(255), nullable=True)
    remark = Column(JSON, nullable=True, default=[])
    current_subs_quantity = Column(Integer, default=0)
    
    amount = Column(Integer, nullable=True)  # Price/amount
    link = Column(String(512), nullable=True)  # Payment/registration link
    
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
