
from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.models.enums import MessengerType
from app.crud import message as message_crud
from app.schemas.messenger import MessageCreate
from app.utils.logger import get_logger

from .strategies.base import MessagingStrategy
from .strategies.email import EmailStrategy
from .strategies.whatsapp import WhatsappStrategy
from .strategies.telegram import TelegramStrategy
from .strategies.discord import DiscordStrategy

logger = get_logger(__name__)

class MessagingService:
    def __init__(self):
        self._strategies: Dict[MessengerType, MessagingStrategy] = {
            MessengerType.MAIL: EmailStrategy(),
            MessengerType.WHATSAPP: WhatsappStrategy(),
            MessengerType.TELEGRAM: TelegramStrategy(),
            MessengerType.DISCORD: DiscordStrategy(),
        }

    def send_message(self, db: Session, messenger_type: MessengerType, to: str, text: str, link: str = None, user_id: int = None) -> bool:
        
        extra_data = {}
        target = to

        # If we have a user_id, try to fetch better contact info from Messenger profile
        if user_id:
            from app.models.user import User as UserModel
            # Eager load messenger
            user = db.query(UserModel).filter(UserModel.id == user_id).first()
            if user and user.messenger:
                msg_profile = user.messenger
                
                if messenger_type == MessengerType.TELEGRAM:
                    # Expect lookup in 'telegram' JSON column: {"chat_id": 123}
                    if msg_profile.telegram and isinstance(msg_profile.telegram, dict):
                        chat_id = msg_profile.telegram.get("chat_id")
                        if chat_id:
                            target = str(chat_id)
                            
                elif messenger_type == MessengerType.DISCORD:
                    # Expect lookup in 'discord' JSON column: {"dm_channel_id": "...", "user_id": "..."}
                    if msg_profile.discord and isinstance(msg_profile.discord, dict):
                        dm_channel_id = msg_profile.discord.get("dm_channel_id")
                        discord_user_id = msg_profile.discord.get("user_id")
                        
                        if dm_channel_id:
                            target = str(dm_channel_id)
                        
                        if discord_user_id:
                            extra_data['user_id'] = str(discord_user_id)
                            extra_data['create_dm'] = True
                            
                elif messenger_type == MessengerType.WHATSAPP:
                    # Validating phone from profile if needed, but usually 'to' from user.phone_number is fine
                    if msg_profile.whatsapp and isinstance(msg_profile.whatsapp, dict):
                        phone = msg_profile.whatsapp.get("phone")
                        if phone:
                            target = phone

        strategy = self._strategies.get(messenger_type)
        if not strategy:
            logger.error(f"No strategy found for {messenger_type}")
            return False
            
        success = strategy.send(target, text, link, extra_data=extra_data)
        
        # Log to DB via CRUD
        try:
            msg_data = MessageCreate(
                text=text,
                link=link,
                messenger_type=messenger_type,
                user_id=user_id
            )
            message_crud.create(db, obj_in=msg_data)
        except Exception as e:
            logger.error(f"Failed to log message to DB: {e}")
            
        return success

    def process_daily_check(self, db: Session, user_id: int) -> dict:
        """
        Check if user should receive a notification based on their game state.
        This logic simulates a business rule check.
        """
        # Circular import prevention if necessary, but ideally user_crud matches schemas
        from app.crud import user as user_crud
        
        user = user_crud.get(db, id=user_id)
        if not user:
            return {"status": "error", "message": "User not found"}
        
        # 1. Calculate current score (sum of all quiz scores for this user)
        # Note: Accessing relationship directly. If lazy loading issue, might need eager load in CRUD.
        current_score = sum([q.score for q in user.quizzes]) if user.quizzes else 0
        
        # 2. Define Winning Threshold
        WINNING_THRESHOLD = 50 
        
        # 3. Calculate Max Possible Remaining Score
        TOTAL_QUIZZES_ALLOWED = 5
        MAX_SCORE_PER_QUIZ = 10
        
        quizzes_taken = len(user.quizzes)
        quizzes_remaining = TOTAL_QUIZZES_ALLOWED - quizzes_taken
        
        if quizzes_remaining < 0:
            quizzes_remaining = 0
            
        max_possible_remaining_points = quizzes_remaining * MAX_SCORE_PER_QUIZ
        
        total_potential_score = current_score + max_possible_remaining_points
        
        if total_potential_score < WINNING_THRESHOLD:
            logger.info(f"User {user.username} cannot win (Potential: {total_potential_score} < Threshold: {WINNING_THRESHOLD}). Skipping notification.")
            return {"status": "skipped", "reason": "Impossible to win"}
            
        # 4. If possible to win, send notification
        # Check user's preferred messenger
        messenger_type = MessengerType.MAIL # Default
        receiver = user.email

        # Logic to pick best messenger
        # Priority: Telegram > WhatsApp > Discord > Email (Custom logic assumption)
        # Check if user has connected services
        has_telegram = False
        has_whatsapp = False
        has_discord = False
        
        if user.messenger:
            if user.messenger.telegram and user.messenger.telegram.get("chat_id"):
                has_telegram = True
            if user.messenger.whatsapp and user.messenger.whatsapp.get("phone"):
                has_whatsapp = True
            if user.messenger.discord and (user.messenger.discord.get("dm_channel_id") or user.messenger.discord.get("user_id")):
                has_discord = True
        
        if has_telegram:
            messenger_type = MessengerType.TELEGRAM
            receiver = str(user.messenger.telegram.get("chat_id")) # derived in send_message anyway, but good to be explicit
        elif has_whatsapp:
            messenger_type = MessengerType.WHATSAPP
            receiver = user.messenger.whatsapp.get("phone")
        elif user.phone_number: # Fallback to user phone if no explicit whatsapp profile but phone exists
            messenger_type = MessengerType.WHATSAPP
            receiver = user.phone_number
        elif has_discord:
            messenger_type = MessengerType.DISCORD
            receiver = "lookup_in_service" # send_message will resolve this if user_id is passed
            
        message_text = f"You are doing great! You have {current_score} points. You need {WINNING_THRESHOLD - current_score} more to win!"
        
        sent = self.send_message(db, messenger_type, receiver, message_text, user_id=user.id)
        
        if sent:
             return {"status": "success", "message": "Notification sent"}
        else:
             return {"status": "error", "message": "Failed to send notification"}

messaging_service = MessagingService()
