from app.core.celery_app import celery_app
from app.services.sync_service import sync_service
from app.database.session import SessionLocal
from app.utils.logger import get_logger

logger = get_logger(__name__)

@celery_app.task(name="sync_external_data")
def sync_external_data():
    """
    Celery task to trigger the synchronization of external data from the quiz platform.
    """
    logger.info("Celery task 'sync_external_data' started.")
    db = None
    try:
        db = SessionLocal()
        sync_service.sync_from_updates_api(db)
        logger.info("Celery task 'sync_external_data' completed successfully.")
    except Exception as e:
        logger.error(f"Celery task 'sync_external_data' failed: {e}", exc_info=True)
    finally:
        if db:
            db.close()

