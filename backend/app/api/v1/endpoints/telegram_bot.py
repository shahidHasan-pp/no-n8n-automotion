"""
Telegram Bot Endpoints
Handles webhook and polling operations
"""

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database.session import get_db
from app.services.messaging.telegram_bot import telegram_bot_service
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/webhook", summary="Telegram Webhook Endpoint")
async def telegram_webhook(
    update: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint for receiving Telegram updates
    
    This can be used instead of polling if you configure a webhook with Telegram
    """
    logger.info(f"[Telegram Webhook] Received update: {update.get('update_id')}")
    
    try:
        # Process single update
        message = update.get("message")
        if not message:
            return {"status": "ignored", "reason": "no message"}
            
        chat_id = message.get("chat", {}).get("id")
        telegram_user_id = message.get("from", {}).get("id")
        text = message.get("text", "")
        
        if text.startswith("/start"):
            telegram_bot_service._handle_start_command(db, chat_id, telegram_user_id, text)
            return {"status": "processed", "command": "start"}
            
        return {"status": "ignored", "reason": "not a command"}
        
    except Exception as e:
        logger.error(f"[Telegram Webhook] Error: {e}")
        return {"status": "error", "message": str(e)}


@router.post("/poll-updates", summary="Manually trigger update polling")
async def poll_telegram_updates(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Manually trigger Telegram bot update polling
    
    This endpoint can be called periodically by a cron job or scheduler
    """
    def process_in_background():
        with SessionLocal() as session:
            count = telegram_bot_service.process_updates(session)
            logger.info(f"[Telegram Poll] Processed {count} updates")
    
    background_tasks.add_task(process_in_background)
    
    return {
        "status": "queued",
        "message": "Update processing queued in background"
    }


@router.get("/bot-info", summary="Get Telegram bot information")
async def get_bot_info():
    """
    Get information about the configured Telegram bot
    """
    info = telegram_bot_service.get_bot_info()
    
    if info:
        return {
            "status": "success",
            "bot": info
        }
    else:
        return {
            "status": "error",
            "message": "Failed to fetch bot info"
        }


@router.get("/polling-status", summary="Get current polling status")
async def get_polling_status():
    """
    Get the current status of the Telegram polling service
    """
    return {
        "last_update_id": telegram_bot_service.last_update_id,
        "bot_token_configured": bool(
            telegram_bot_service.bot_token and 
            telegram_bot_service.bot_token != "dummy_telegram_bot_token"
        )
    }


# Import for SessionLocal
from app.database.session import SessionLocal
