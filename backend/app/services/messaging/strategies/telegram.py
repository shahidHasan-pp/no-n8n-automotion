
import requests
from app.core.config import settings
from .base import MessagingStrategy
from app.utils.logger import get_logger

logger = get_logger(__name__)

class TelegramStrategy(MessagingStrategy):
    def send(self, to: str, content: str, link: str = None, extra_data: dict = None) -> bool:
        # 'to' is expected to be the chat_id here
        logger.info(f"[Telegram] Sending to {to}")
        
        if not settings.TELEGRAM_BOT_TOKEN:
            logger.warning("[Telegram] Token not set, skipping API call.")
            return True
            
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        
        full_text = content
        if link:
            full_text += f"\n\nLink: {link}"

        payload = {
            "chat_id": to,
            "text": full_text
            # "parse_mode": "Markdown" # Optional
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info(f"[Telegram] Successfully sent to {to}")
                return True
            else:
                logger.error(f"[Telegram] Failed to send: {response.text}")
                return False
        except Exception as e:
            logger.error(f"[Telegram] Exception: {e}")
            return False
