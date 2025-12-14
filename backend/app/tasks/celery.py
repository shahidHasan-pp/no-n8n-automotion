from app.core.celery_app import celery_app
from app.api import deps
from app.services.messaging import messaging_service
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@celery_app.task(name="send_notification_task")
def send_notification_task(user_id: int):
    """
    Background task to run the daily logic check and send notification if applicable.
    """
    logger.info(f"Starting background check for user {user_id}")
    
    # We need a new session for the background task
    db = next(deps.get_db())
    try:
        result = messaging_service.process_daily_check(db, user_id)
        logger.info(f"Background check result for user {user_id}: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in background task for user {user_id}: {e}")
    finally:
        db.close()