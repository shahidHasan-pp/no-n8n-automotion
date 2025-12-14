from datetime import datetime, timezone
import asyncio
import json
from app.tasks.celery import celery_app
from app.database.session import SessionLocal
from app.crud.post import PostCRUD
from app.crud.social_platform import SocialPlatformCRUD
from app.core.mock_platforms import MockPlatformFactory, PlatformError
from app.models.enums import PostStatus
from app.utils.logger import get_logger

logger = get_logger(__name__)

@celery_app.task
def publish_post_task(post_id: int):
    pass