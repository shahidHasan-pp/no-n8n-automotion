
from sqlalchemy import Column, BigInteger, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base_model import BaseModel

class UserSubscribed(BaseModel):
    __tablename__ = "user_subscribed"

    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    subs_id = Column(BigInteger, ForeignKey("subscriptions.id"), nullable=False)
    
    start_date = Column(DateTime(timezone=True), nullable=True)  # When subscription starts
    end_date = Column(DateTime(timezone=True), nullable=True)    # When subscription expires

class PlayedQuiz(BaseModel):
    __tablename__ = "played_quizzes"

    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    subs_id = Column(BigInteger, ForeignKey("subscriptions.id"), nullable=True) 
    
    score = Column(Integer, default=0)
    time = Column(Integer, nullable=True) # Time taken or timestamp? Assuming time taken or similar metric.
    
    # Relationships
    user = relationship("User", back_populates="quizzes")
    subscription = relationship("Subscription")
