
from celery import shared_task
from app.core.celery_app import celery_app
from app.services.messaging import messaging_service
from app.models.enums import MessengerType
from app.database.session import SessionLocal

@shared_task
def send_notification_task(messenger_type_str: str, text: str, link: str = None, user_id: int = None):
    """
    Celery task to send message asynchronously.
    """
    db = SessionLocal()
    try:
        # Convert string back to Enum
        # If user_id is provided, we might need to fetch user to get receiver?
        # But send_message now expects 'to' logic to be handled or passed?
        # Wait, I updated send_message to take 'to'.
        # If I don't pass 'to' here, it will fail.
        # But the API endpoint doesn't know 'to' anymore because Schema removed it.
        # So we MUST fetch user email/phone from user_id if present.
        
        from app.crud import user as user_crud
        receiver = "unknown"
        if user_id:
             user = user_crud.user.get(db, id=user_id)
             if user:
                 if messenger_type_str == "whatsapp" and user.phone_number:
                     receiver = user.phone_number
                 else:
                     receiver = user.email
        
        messenger_type = MessengerType(messenger_type_str)
        messaging_service.send_message(
            db=db,
            messenger_type=messenger_type,
            to=receiver,
            text=text,
            link=link,
            user_id=user_id
        )
    finally:
        db.close()
