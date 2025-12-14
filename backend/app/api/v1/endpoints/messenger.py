
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import messenger as messenger_crud, message as message_crud
from app.schemas.messenger import (
    Messenger, MessengerCreate, MessengerUpdate,
    Message, MessageCreate
)
from app.tasks.notification import send_notification_task

router = APIRouter()

# Messenger Profile
@router.post("/", response_model=Messenger)
def create_messenger_profile(profile_in: MessengerCreate, db: Session = Depends(deps.get_db)) -> Any:
    return messenger_crud.create(db, obj_in=profile_in)

@router.get("/{id}", response_model=Messenger)
def read_messenger_profile(id: int, db: Session = Depends(deps.get_db)) -> Any:
    item = messenger_crud.get(db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Messenger profile not found")
    return item

# Messages
@router.post("/send", response_model=dict)
def send_message(msg_in: MessageCreate, background_tasks: BackgroundTasks, db: Session = Depends(deps.get_db)) -> Any:
    """
    Send a message via the specified messenger type.
    This triggers a Celery task.
    """
    # Trigger Celery Task
    send_notification_task.delay(
        messenger_type_str=msg_in.messenger_type,
        sender=msg_in.sender,
        receiver=msg_in.receiver,
        text=msg_in.text,
        link=msg_in.link,
        user_id=msg_in.user_id
    )
    
    return {"message": "Message queued for sending"}

@router.get("/history/", response_model=List[Message])
def read_message_history(db: Session = Depends(deps.get_db), skip: int = 0, limit: int = 100) -> Any:
    return message_crud.get_multi(db, skip=skip, limit=limit)
