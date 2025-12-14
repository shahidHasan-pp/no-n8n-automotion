
from sqlalchemy import Column, String, BigInteger, Text, Enum as SQLEnum, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base_model import BaseModel
from .enums import MessengerType

class Messenger(BaseModel):
    __tablename__ = "messengers"

    # Store info for services
    mail = Column(JSON, nullable=True, default=[])
    telegram = Column(JSON, nullable=True, default=[])
    whatsapp = Column(JSON, nullable=True, default=[])
    discord = Column(JSON, nullable=True, default=[])
    
    # Relationships
    users = relationship("User", back_populates="messenger")


class Message(BaseModel):
    __tablename__ = "messages"

    # sender and receiver removed as per requirement
    # sender = Column(String(255), nullable=False)
    # receiver = Column(String(255), nullable=False)
    text = Column(Text, nullable=False)
    link = Column(String(512), nullable=True)
    time = Column(DateTime(timezone=True), server_default=func.now())
    messenger_type = Column(SQLEnum(MessengerType), nullable=False) # To know which platform was used
    
    # Optional: Link to user if possible
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="messages")
