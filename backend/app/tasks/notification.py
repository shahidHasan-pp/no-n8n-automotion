
from celery import shared_task
from app.core.celery_app import celery_app
from app.services.messaging import messaging_service
from app.models.enums import MessengerType
from app.database.session import SessionLocal

@shared_task
def send_notification_task(messenger_type_str: str, sender: str, receiver: str, text: str, link: str = None, user_id: int = None):
    """
    Celery task to send message asynchronously.
    """
    db = SessionLocal()
    try:
        # Convert string back to Enum
        messenger_type = MessengerType(messenger_type_str)
        messaging_service.send_message(
            db=db,
            messenger_type=messenger_type,
            sender=sender,
            receiver=receiver,
            text=text,
            link=link,
            user_id=user_id
        )
    finally:
        db.close()
