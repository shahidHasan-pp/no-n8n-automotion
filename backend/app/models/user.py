
from sqlalchemy import Column, String, BigInteger, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base_model import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    username = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone_number = Column(String(50), nullable=True)
    
    quiz_ids = Column(JSON, nullable=True, default=[])
    
    # Foreign Keys
    messenger_id = Column(BigInteger, ForeignKey("messengers.id"), nullable=True)
    subscription_id = Column(BigInteger, ForeignKey("subscriptions.id"), nullable=True)

    # Relationships
    messenger = relationship("Messenger", back_populates="users")
    subscription = relationship("Subscription", back_populates="users")
    
    # Back ref for Quiz and Messages
    quizzes = relationship("Quiz", back_populates="user")
    messages = relationship("Message", back_populates="user")
