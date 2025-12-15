"""
Telegram Bot Service - Handles message polling and user onboarding
Implements getUpdates polling and processes /start commands
"""

import requests
import time
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.core.config import settings
from app.utils.logger import get_logger
from app.crud.user import user as user_crud
from app.crud.messenger import messenger as messenger_crud
from app.database.session import SessionLocal

logger = get_logger(__name__)


class TelegramBotService:
    """
    Service for handling Telegram bot operations including:
    - Polling for updates (getUpdates)
    - Processing /start commands
    - User onboarding and validation
    """
    
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.last_update_id = 0
        
    def get_updates(self, offset: Optional[int] = None, timeout: int = 30) -> List[Dict[str, Any]]:
        """
        Poll for new updates from Telegram
        
        Args:
            offset: Update ID to start from (for acknowledging processed updates)
            timeout: Long polling timeout in seconds
            
        Returns:
            List of update objects
        """
        if not self.bot_token or self.bot_token == "dummy_telegram_bot_token":
            logger.warning("[Telegram Bot] Using dummy token, skipping getUpdates")
            return []
            
        url = f"{self.base_url}/getUpdates"
        params = {
            "timeout": timeout,
            "allowed_updates": ["message"]  # Only interested in messages
        }
        
        if offset is not None:
            params["offset"] = offset
            
        try:
            response = requests.get(url, params=params, timeout=timeout + 5)
            response.raise_for_status()
            
            data = response.json()
            if data.get("ok"):
                return data.get("result", [])
            else:
                logger.error(f"[Telegram Bot] API error: {data}")
                return []
                
        except requests.RequestException as e:
            logger.error(f"[Telegram Bot] Request failed: {e}")
            return []
    
    def process_updates(self, db: Session) -> int:
        """
        Process all pending updates
        
        Returns:
            Number of updates processed
        """
        updates = self.get_updates(offset=self.last_update_id + 1 if self.last_update_id > 0 else None)
        
        if not updates:
            return 0
            
        processed_count = 0
        
        for update in updates:
            try:
                update_id = update.get("update_id")
                message = update.get("message")
                
                if not message:
                    continue
                    
                # Extract message details
                chat_id = message.get("chat", {}).get("id")
                user_id_telegram = message.get("from", {}).get("id")
                text = message.get("text", "")
                
                if not chat_id or not text:
                    continue
                
                # Process /start command
                if text.startswith("/start"):
                    self._handle_start_command(db, chat_id, user_id_telegram, text)
                    processed_count += 1
                
                # Update last processed ID
                if update_id > self.last_update_id:
                    self.last_update_id = update_id
                    
            except Exception as e:
                logger.error(f"[Telegram Bot] Error processing update: {e}")
                continue
        
        return processed_count
    
    def _handle_start_command(self, db: Session, chat_id: int, telegram_user_id: int, text: str):
        """
        Handle /start <username> command
        
        Flow:
        1. Parse username from command
        2. Validate user exists in database
        3. Store telegram_chat_id mapping
        4. Send confirmation/error message
        """
        parts = text.split(maxsplit=1)
        
        if len(parts) < 2:
            # No username provided
            self.send_message(
                chat_id=chat_id,
                text="❌ Invalid command format.\n\nUsage: /start <your_username>\n\nExample: /start john_doe"
            )
            return
        
        username = parts[1].strip()
        
        # Validate user exists
        user = user_crud.get_by_username(db, username=username)
        
        if not user:
            self.send_message(
                chat_id=chat_id,
                text=f"❌ Username '{username}' not found in our system.\n\nPlease register on our platform first or check your username spelling."
            )
            logger.info(f"[Telegram Bot] Failed login attempt for username: {username}")
            return
        
        # Get or create messenger profile
        if user.messenger_id:
            messenger_profile = messenger_crud.get(db, id=user.messenger_id)
        else:
            # Create new messenger profile
            messenger_profile = messenger_crud.create(db, obj_in={
                "mail": {},
                "telegram": {},
                "whatsapp": {},
                "discord": {}
            })
            # Link to user
            user_crud.update(db, db_obj=user, obj_in={"messenger_id": messenger_profile.id})
        
        # Update telegram information
        telegram_data = {
            "chat_id": chat_id,
            "user_id": telegram_user_id,
            "username": username,
            "linked_at": time.time()
        }
        
        updated_data = {
            "telegram": telegram_data
        }
        
        messenger_crud.update(db, db_obj=messenger_profile, obj_in=updated_data)
        
        # Send success message
        self.send_message(
            chat_id=chat_id,
            text=f"✅ Successfully linked to account: {user.username}\n\n"
                 f"👤 Name: {user.full_name or 'N/A'}\n"
                 f"📧 Email: {user.email}\n\n"
                 f"You will now receive notifications via Telegram!"
        )
        
        logger.info(f"[Telegram Bot] User {username} (ID: {user.id}) linked Telegram chat_id: {chat_id}")
    
    def send_message(self, chat_id: int, text: str, parse_mode: str = None) -> bool:
        """
        Send a message to a Telegram chat
        
        Args:
            chat_id: Telegram chat ID
            text: Message text
            parse_mode: Optional formatting (Markdown or HTML)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.bot_token or self.bot_token == "dummy_telegram_bot_token":
            logger.info(f"[Telegram Bot] DUMMY MODE - Would send to {chat_id}: {text}")
            return True
            
        url = f"{self.base_url}/sendMessage"
        
        payload = {
            "chat_id": chat_id,
            "text": text
        }
        
        if parse_mode:
            payload["parse_mode"] = parse_mode
            
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get("ok"):
                logger.info(f"[Telegram Bot] Message sent to chat_id {chat_id}")
                return True
            else:
                logger.error(f"[Telegram Bot] Failed to send: {data}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"[Telegram Bot] Send failed: {e}")
            return False
    
    def get_bot_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the bot"""
        if not self.bot_token or self.bot_token == "dummy_telegram_bot_token":
            return {"username": "DummyBot", "first_name": "Dummy Bot"}
            
        url = f"{self.base_url}/getMe"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get("ok"):
                return data.get("result")
            return None
            
        except requests.RequestException as e:
            logger.error(f"[Telegram Bot]GetMe failed: {e}")
            return None


# Singleton instance
telegram_bot_service = TelegramBotService()
