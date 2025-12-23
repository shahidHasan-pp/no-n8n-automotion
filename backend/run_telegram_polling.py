 import time
import sys
import os
import signal
from sqlalchemy.orm import Session

# Add the parent directory to sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.session import SessionLocal
from app.services.messaging.telegram_bot import telegram_bot_service
from app.utils.logger import get_logger

logger = get_logger("telegram_poller")

def run_polling():
    """
    Standalone script to pool Telegram updates.
    Useful when not using Celery/Redis.
    """
    logger.info("Starting Telegram Polling Service...")
    
    # Ensure checking works
    bot_info = telegram_bot_service.get_bot_info()
    if bot_info:
        logger.info(f"Connected to Bot: {bot_info.get('first_name')} (@{bot_info.get('username')})")
    else:
        logger.error("Failed to connect to Telegram Bot. Check your token in .env")
        return

    while True:
        try:
            with SessionLocal() as db:
                count = telegram_bot_service.process_updates(db)
                if count > 0:
                    logger.info(f"Processed {count} updates")
        except Exception as e:
            logger.error(f"Error in polling loop: {e}")
        
        # Sleep to avoid hitting rate limits too hard (Telegram allows long polling, but a small sleep is good)
        time.sleep(2)

if __name__ == "__main__":
    try:
        run_polling()
    except KeyboardInterrupt:
        logger.info("Polling service stopped by user.")
