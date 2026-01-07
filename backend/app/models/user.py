
from sqlalchemy import Column, String, BigInteger, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from .base_model import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    username = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    phone_number = Column(String(50), nullable=True)
    
    # Platform flags
    quizard = Column(Boolean, default=False)
    wordly = Column(Boolean, default=False)
    arcaderush = Column(Boolean, default=False)
    
    # Foreign Keys
    messenger_id = Column(BigInteger, ForeignKey("messengers.id"), nullable=True)
    subscription_id = Column(BigInteger, ForeignKey("subscriptions.id"), nullable=True)

    # Relationships
    messenger = relationship("Messenger", back_populates="users")
    subscription = relationship("Subscription", back_populates="users")
    
    # Back ref for PlayedQuiz and Messages
    quizzes = relationship("PlayedQuiz", back_populates="user")
    messages = relationship("Message", back_populates="user")
