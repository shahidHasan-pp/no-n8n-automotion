
from sqlalchemy import Column, String, Integer, JSON, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from .base_model import BaseModel
from .enums import QuizType, SubscriptionType, SubscriptionLength

class Subscription(BaseModel):
    __tablename__ = "subscriptions"
    
    name = Column(String(255), nullable=False)
    type = Column(SQLEnum(SubscriptionType), nullable=False)
    time = Column(SQLEnum(SubscriptionLength), nullable=False)
    offer = Column(String(255), nullable=True)
    prize = Column(String(255), nullable=True)
    remark = Column(JSON, nullable=True, default=[])
    
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    users = relationship("User", back_populates="subscription") 
