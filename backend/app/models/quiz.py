
from sqlalchemy import Column, BigInteger, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base_model import BaseModel

class Quiz(BaseModel):
    __tablename__ = "quizzes"

    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    subs_id = Column(BigInteger, ForeignKey("subscriptions.id"), nullable=True) 
    
    score = Column(Integer, default=0)
    time = Column(Integer, nullable=True) # Time taken or timestamp? Assuming time taken or similar metric.
    
    # Relationships
    user = relationship("User", back_populates="quizzes")
    subscription = relationship("Subscription")
