"""
Enhanced Telegram Strategy - Uses stored chat_id for sending
Part of the Messaging Strategy Pattern
"""

import requests
from typing import Optional
from app.core.config import settings
from .base import MessagingStrategy
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TelegramStrategy(MessagingStrategy):
    """
    Telegram message sender implementation
    
    This strategy handles sending messages via Telegram Bot API.
    It expects the chat_id to be provided in the 'to' parameter or extra_data.
    """
    
    def send(self, to: str, content: str, link: str = None, extra_data: dict = None) -> bool:
        """
        Send a message via Telegram
        
        Args:
            to: Telegram chat_id (can be string or int)
            content: Message text
            link: Optional link to append
            extra_data: Optional dict containing additional data
            
        Returns:
            True if successful, False otherwise
        """
        # Extract chat_id from 'to' parameter or extra_data
        chat_id = to
        
        if extra_data and 'chat_id' in extra_data:
            chat_id = extra_data['chat_id']
        
        if not chat_id:
            logger.error("[Telegram] No chat_id provided")
            return False
            
        logger.info(f"[Telegram] Sending to chat_id: {chat_id}")
        
        # Check if token is configured
        if not settings.TELEGRAM_BOT_TOKEN or settings.TELEGRAM_BOT_TOKEN == "dummy_telegram_bot_token":
            logger.warning(f"[Telegram] DUMMY MODE - Would send to {chat_id}: {content}")
            return True
            
        # Build API URL
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        
        # Construct message text
        full_text = content
        if link:
            full_text += f"\n\n🔗 {link}"
        
        # Prepare payload
        payload = {
            "chat_id": str(chat_id),  # Ensure it's a string
            "text": full_text,
            "parse_mode": "HTML"  # Support basic formatting
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"[Telegram] Successfully sent to {chat_id}")
                return True
            else:
                error_data = response.json()
                logger.error(f"[Telegram] Failed to send: {error_data}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"[Telegram] Request exception: {e}")
            return False
        except Exception as e:
            logger.error(f"[Telegram] Unexpected error: {e}")
            return False


class TelegramAdapter:
    """
    Adapter pattern implementation for Telegram
    
    This adapter wraps the TelegramStrategy and provides
    additional convenience methods for common operations.
    """
    
    def __init__(self):
        self.strategy = TelegramStrategy()
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_notification(self, chat_id: int, message: str, link: Optional[str] = None) -> bool:
        """
        Send a notification message
        
        Args:
            chat_id: Telegram chat ID
            message: Notification text
            link: Optional link
            
        Returns:
            True if successful
        """
        return self.strategy.send(to=str(chat_id), content=message, link=link)
    
    def send_alert(self, chat_id: int, alert_text: str) -> bool:
        """
        Send an alert message with special formatting
        
        Args:
            chat_id: Telegram chat ID
            alert_text: Alert message
            
        Returns:
            True if successful
        """
        formatted_message = f"🚨 <b>ALERT</b> 🚨\n\n{alert_text}"
        return self.strategy.send(
            to=str(chat_id),
            content=formatted_message,
            extra_data={"parse_mode": "HTML"}
        )
    
    def send_with_buttons(self, chat_id: int, text: str, buttons: list) -> bool:
        """
        Send a message with inline keyboard buttons
        
        Args:
            chat_id: Telegram chat ID
            text: Message text
            buttons: List of button configurations
            
        Returns:
            True if successful
        """
        if not self.bot_token or self.bot_token == "dummy_telegram_bot_token":
            logger.info(f"[Telegram Adapter] DUMMY MODE - Would send buttons to {chat_id}")
            return True
            
        url = f"{self.base_url}/sendMessage"
        
        # Build inline keyboard
        keyboard = {
            "inline_keyboard": [
                [{"text": btn["text"], "callback_data": btn["data"]} for btn in row]
                for row in buttons
            ]
        }
        
        payload = {
            "chat_id": str(chat_id),
            "text": text,
            "reply_markup": keyboard
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"[Telegram Adapter] Failed to send buttons: {e}")
            return False
