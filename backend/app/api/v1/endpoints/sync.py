from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.services.sync_service import sync_service
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/trigger-sync", status_code=202)
def trigger_sync(db: Session = Depends(deps.get_db)):
    # alternate of /endpoints/webhook
    logger.info("Manual synchronization triggered via API.")
    sync_service.sync_from_updates_api(db)
    return {"message": "Synchronization process started."}