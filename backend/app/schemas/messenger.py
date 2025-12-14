
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.enums import MessengerType
from .base import BaseSchema

# Messenger Info Schemas
class MessengerBase(BaseModel):
    mail: Optional[str] = None
    telegram: Optional[str] = None
    whatsapp: Optional[str] = None
    discord: Optional[str] = None

class MessengerCreate(MessengerBase):
    pass

class MessengerUpdate(MessengerBase):
    pass

class Messenger(MessengerBase, BaseSchema):
    pass

# Message Log Schemas
class MessageBase(BaseModel):
    sender: str
    receiver: str
    text: str
    link: Optional[str] = None
    messenger_type: MessengerType
    user_id: Optional[int] = None

class MessageCreate(MessageBase):
    pass

class Message(MessageBase, BaseSchema):
    time: datetime
