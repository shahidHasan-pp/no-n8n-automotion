
import requests
from app.core.config import settings
from .base import MessagingStrategy
from app.utils.logger import get_logger

logger = get_logger(__name__)

class WhatsappStrategy(MessagingStrategy):
    def send(self, to: str, content: str, link: str = None, extra_data: dict = None) -> bool:
        logger.info(f"[Whatsapp] Sending to {to}")
        
        if not settings.WHATSAPP_ACCESS_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
            logger.warning("[Whatsapp] Credentials not set, skipping API call.")
            return True

        url = f"https://graph.facebook.com/v20.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        full_text = content
        if link:
            full_text += f"\n\nLink: {link}"
            
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {
                "body": full_text
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code in [200, 201]:
                logger.info(f"[Whatsapp] Successfully sent to {to}")
                return True
            else:
                logger.error(f"[Whatsapp] Failed to send: {response.text}")
                return False
        except Exception as e:
            logger.error(f"[Whatsapp] Exception: {e}")
            return False
