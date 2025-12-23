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

    success = messaging_service.send_message(db, messenger_type, receiver, text, link, user_id=user.id)
    
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

@router.post("/send-bulk")
def send_bulk_notifications(
    messenger_type: MessengerType,
    text: str,
    link: str = None,
    has_subscription: bool = None,
    subscription_id: int = None,
    db: Session = Depends(deps.get_db),
    background_tasks: BackgroundTasks = None
) -> Any:
    """
    Send bulk notifications filtered by subscription status or specific subscription.
    """
    from app.crud import user as user_crud
    
    # Re-use user_crud.get_with_filters but we might need to add subscription_id filtering support to it,
    # or just query here. For simplicity, let's query here or update CRUD.
    # To avoid changing CRUD repeatedly, let's just query efficiently here.
    
    from app.models.user import User
    query = db.query(User)
    
    if has_subscription is not None:
         if has_subscription:
            query = query.filter(User.subscription_id.isnot(None))
         else:
            query = query.filter(User.subscription_id.is_(None))
            
    if subscription_id:
        query = query.filter(User.subscription_id == subscription_id)
        
    users = query.all()
    count = 0
    
    for user in users:
        # Determine receiver based on type
        receiver = user.email # Default
        if messenger_type == MessengerType.WHATSAPP:
             receiver = user.phone_number
             
        # Call service (synchronous for now, ideally queue this)
        if receiver:
             messaging_service.send_message(db, messenger_type, receiver, text, link, user_id=user.id)
             count += 1
             
    return {"status": "success", "queued_count": count}


@router.post("/send-channel")
def send_channel_notification(
    text: str,
    messenger_type: MessengerType = MessengerType.TELEGRAM,
    link: str = None,
    channel_id: str = None, # Optional override
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Send a notification to a specific Channel/Group.
    Currently defaults to TELEGRAM_CHANNEL_ID from env if valid.
    """
    from app.core.config import settings
    
    target = channel_id
    
    # Resolve target based on messenger type
    if messenger_type == MessengerType.TELEGRAM:
        if not target:
            target = settings.TELEGRAM_CHANNEL_ID
        
        if not target:
             raise HTTPException(status_code=400, detail="No Telegram Channel ID configured (check .env TELEGRAM_CHANNEL_ID)")
             
        # Basic formatting check
        target = target.strip()
            
    elif messenger_type == MessengerType.DISCORD:
         if not target:
             # Placeholder for a DISCORD_CHANNEL_ID if we had one
             target = "" 
         if not target:
             raise HTTPException(status_code=400, detail="Discord Channel ID not provided")

    success = messaging_service.send_message(db, messenger_type, target, text, link, user_id=None)
    
    if success:
        return {"status": "success", "message": f"Notification sent to {target}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send notification to channel")
