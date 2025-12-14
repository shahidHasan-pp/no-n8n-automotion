from typing import Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.api import deps
from app.services.messaging import messaging_service
from app.models.enums import MessengerType
from app.crud import user as user_crud

router = APIRouter()

@router.post("/send-manual")
def send_manual_notification(
    user_id: int,
    messenger_type: MessengerType,
    text: str,
    link: str = None,
    db: Session = Depends(deps.get_db),
    background_tasks: BackgroundTasks = None
) -> Any:
    """
    Manually trigger a notification for a user.
    """
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # In a real scenario, we might want to run this in background
    # background_tasks.add_task(messaging_service.send_message, db, messenger_type, "System", user.email, text, link, user.id)
    
    # Using the service directly for immediate response in this demo
    # Note: receiver is dummy for now, depends on messenger_type (email vs phone)
    receiver = user.email if messenger_type == MessengerType.MAIL else user.phone_number
    if not receiver:
         # Fallback or error if no contact info
         receiver = "unknown"

    success = messaging_service.send_message(db, messenger_type, "System", receiver, text, link, user.id)
    
    if success:
        return {"status": "success", "message": "Notification sent"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send notification")

@router.post("/trigger-logic-check")
def trigger_logic_check(
    user_id: int,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Trigger the business logic check (simulate daily run).
    Checks if user should receive a message based on score/winning probability.
    """
    # This will be implemented in the MessagingService or a new BusinessLogicService
    result = messaging_service.process_daily_check(db, user_id)
    return result
