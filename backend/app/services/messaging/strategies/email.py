
import requests
import json
import base64
from app.core.config import settings
from .base import MessagingStrategy
from app.utils.logger import get_logger

logger = get_logger(__name__)

class EmailStrategy(MessagingStrategy):
    def send(self, to: str, content: str, link: str = None, extra_data: dict = None) -> bool:
        logger.info(f"[Email] Sending to {to}")
        
        if not settings.GMAIL_ACCESS_TOKEN:
            logger.warning("[Email] GMAIL_ACCESS_TOKEN not set, skipping API call.")
            return True # Pretend success for dev

        url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
        headers = {
            "Authorization": f"Bearer {settings.GMAIL_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Prepare RFC2822 email
        # Subject: Notification from PurplePatch
        # To: {to}
        # Body: {content} \n Link: {link}
        
        message_body = f"Subject: Notification from PurplePatch\nTo: {to}\n\n{content}"
        if link:
            message_body += f"\n\nLink: {link}"
            
        encoded_message = base64.urlsafe_b64encode(message_body.encode("utf-8")).decode("utf-8")
        
        payload = {
            "raw": encoded_message
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info(f"[Email] Successfully sent to {to}")
                return True
            else:
                logger.error(f"[Email] Failed to send: {response.text}")
                return False
        except Exception as e:
            logger.error(f"[Email] Exception: {e}")
            return False
