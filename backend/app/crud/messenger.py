
from app.crud.base import CRUDBase
from app.models.messenger import Messenger, Message
from app.schemas.messenger import (
    MessengerCreate, MessengerUpdate,
    MessageCreate
)
# Message doesn't have an update schema, usually immutable log. Using MessageCreate as Update for generic generic, or create custom.
# Since generic requires UpdateSchemaType, I'll pass MessageCreate effectively or use None if type system allows, but for simplicity:

class CRUDMessenger(CRUDBase[Messenger, MessengerCreate, MessengerUpdate]):
    pass

class CRUDMessage(CRUDBase[Message, MessageCreate, MessageCreate]):
    pass

messenger = CRUDMessenger(Messenger)
message = CRUDMessage(Message)
