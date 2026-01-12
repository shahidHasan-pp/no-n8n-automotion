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
                    if update_id and update_id > self.last_update_id:
                        self.last_update_id = update_id
                    continue
                    
                # Extract message details
                chat_id = message.get("chat", {}).get("id")
                telegram_user_id = message.get("from", {}).get("id")
                telegram_username_handle = message.get("from", {}).get("username", "") 
                text = message.get("text", "").strip()
                
                if not chat_id or not text:
                    continue
                
                # Use unified handler
                self.handle_message(db, chat_id, telegram_user_id, telegram_username_handle, text)
                processed_count += 1
                
                # Update last processed ID
                if update_id and update_id > self.last_update_id:
                    self.last_update_id = update_id
                    
            except Exception as e:
                logger.error(f"[Telegram Bot] Error processing update: {e}")
                continue
        
        return processed_count
    
    def handle_message(self, db: Session, chat_id: int, telegram_user_id: int, telegram_username_handle: str, text: str):
        """
        Unified message handler for both polling and webhooks.
        Processes commands and linking attempts.
        """
        text = text.strip()
        if not text:
            return

        # Check for linking attempt
        # Logic: Treat text as potential username. 
        # If it starts with /start, strip it. If just text, use it as is.
        potential_username = text
        if text.startswith("/start"):
            parts = text.split(maxsplit=1)
            if len(parts) > 1:
                potential_username = parts[1].strip()
            else:
                # Just /start with no username
                self.send_message(
                    chat_id=chat_id,
                    text=f"👋 Welcome! To link your account, please use /start followed by your username.\n"
                         f"Example: `/start your_username`"
                )
                return
        
        if potential_username:
            self._handle_user_linking(db, chat_id, telegram_user_id, telegram_username_handle, potential_username)
    
    def _handle_user_linking(self, db: Session, chat_id: int, telegram_user_id: int, telegram_username_handle: str, provided_username: str):
        """
        Handle user account linking
        """
        try:
            # Check if user exists in DB
            user = user_crud.get_by_username(db, username=provided_username)
            
            if not user:
                logger.info(f"[Telegram Bot] Username '{provided_username}' not found in DB.")
                self.send_message(
                    chat_id=chat_id,
                    text="আপনি এখনো রেজিস্টার করেননি।\nসার্ভিস চালু করতে এখনই রেজিস্ট্রেশন করুন।"
                )
                return
            
            messenger_profile = None
            if user.messenger_id:
                messenger_profile = messenger_crud.get(db, id=user.messenger_id)

            had_previous_telegram_link = False
            if messenger_profile and messenger_profile.telegram and isinstance(messenger_profile.telegram, dict) and messenger_profile.telegram.get("chat_id"):
                 had_previous_telegram_link = True
                 existing_chat_id = messenger_profile.telegram.get("chat_id")
                 if str(existing_chat_id) == str(chat_id):
                    # Already linked to the same account.
                    logger.info(f"[Telegram Bot] User {provided_username} already linked to chat_id {chat_id}.")
                    self.send_message(
                        chat_id=chat_id,
                        text="আপনি ইতোমধ্যেই আমাদের সিস্টেমে নিবন্ধিত আছেন।\nআমাদের সার্ভিস সম্পর্কিত সকল বিস্তারিত তথ্য এখানে পেয়ে যাবেন।"
                    )
                    return
            
            telegram_data = {
                "chat_id": chat_id,
                "user_id": telegram_user_id,
                "username": telegram_username_handle, 
                "linked_at": time.time()
            }
            
            # Ensure Messenger Profile Exists
            if not messenger_profile:
                logger.info(f"[Telegram Bot] Creating new messenger profile for User {user.id}")
                messenger_profile = messenger_crud.create(db, obj_in={
                    "mail": {},
                    "telegram": {},
                    "whatsapp": {},
                    "discord": {}
                })
                user.messenger_id = messenger_profile.id
                db.add(user)
                db.commit()
                db.refresh(user)
            
            # Update Telegram Data
            messenger_profile.telegram = telegram_data
            
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(messenger_profile, "telegram")
            
            db.add(messenger_profile)
            db.commit()
            
            if had_previous_telegram_link:
                logger.info(f"[Telegram Bot] SUCCESS: User {provided_username} updated Telegram chat_id to: {chat_id}")
                self.send_message(
                    chat_id=chat_id,
                    text="আপনি ইতোমধ্যেই আমাদের সাথে যুক্ত আছেন।\nআমাদের সার্ভিস সম্পর্কিত সকল বিস্তারিত তথ্য এখানে পেয়ে যাবেন।"
                )
            else:
                logger.info(f"[Telegram Bot] SUCCESS: User {provided_username} linked Telegram chat_id: {chat_id}")
                self.send_message(
                    chat_id=chat_id,
                    text="অভিনন্দন! আপনার অ্যাকাউন্ট সফলভাবে যুক্ত করা হয়েছে।\nএখন থেকে আপনি সকল আপডেট ও নোটিফিকেশন এখানে পাবেন।\
                        \n\nখেলতে ক্লিক করুন- https://quizard.live/?qcid=246"
                )
                
        except Exception as e:
            logger.error(f"[Telegram Bot] Exception in _handle_user_linking: {e}")
            db.rollback()
    
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
