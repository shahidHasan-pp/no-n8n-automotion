
import abc
from typing import Any, Dict
from sqlalchemy.orm import Session
from app.models.enums import MessengerType
from app.crud import message as message_crud
from app.schemas.messenger import MessageCreate
from app.utils.logger import get_logger

logger = get_logger(__name__)

class MessagingStrategy(abc.ABC):
    @abc.abstractmethod
    def send(self, to: str, content: str, link: str = None) -> bool:
        pass

class EmailStrategy(MessagingStrategy):
    def send(self, to: str, content: str, link: str = None) -> bool:
        logger.info(f"[Email] Sending to {to}: {content} (Link: {link})")
        # Dummy Implementation
        return True

class WhatsappStrategy(MessagingStrategy):
    def send(self, to: str, content: str, link: str = None) -> bool:
        logger.info(f"[Whatsapp] Sending to {to}: {content} (Link: {link})")
        # Dummy Implementation
        return True

class TelegramStrategy(MessagingStrategy):
    def send(self, to: str, content: str, link: str = None) -> bool:
        logger.info(f"[Telegram] Sending to {to}: {content} (Link: {link})")
        # Dummy Implementation
        return True

class DiscordStrategy(MessagingStrategy):
    def send(self, to: str, content: str, link: str = None) -> bool:
        logger.info(f"[Discord] Sending to {to}: {content} (Link: {link})")
        # Dummy Implementation
        return True

class MessagingService:
    def __init__(self):
        self._strategies: Dict[MessengerType, MessagingStrategy] = {
            MessengerType.MAIL: EmailStrategy(),
            MessengerType.WHATSAPP: WhatsappStrategy(),
            MessengerType.TELEGRAM: TelegramStrategy(),
            MessengerType.DISCORD: DiscordStrategy(),
        }

    def send_message(self, db: Session, messenger_type: MessengerType, sender: str, receiver: str, text: str, link: str = None, user_id: int = None) -> bool:
        strategy = self._strategies.get(messenger_type)
        if not strategy:
            logger.error(f"No strategy found for {messenger_type}")
            return False
            
        success = strategy.send(receiver, text, link)
        
        # Log to DB
        try:
            msg_data = MessageCreate(
                sender=sender,
                receiver=receiver,
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
        Logic: User needs X points to win. Check if remaining quizzes can provide X points.
        If yes -> Send notification (e.g., 'Keep playing!').
        If no -> Do not send notification (Impossible to win).
        """
        # Circular import prevention
        from app.crud import user as user_crud
        from app.crud import quiz as quiz_crud
        
        user = user_crud.get(db, id=user_id)
        if not user:
            return {"status": "error", "message": "User not found"}
        
        # 1. Calculate current score (sum of all quiz scores for this user)
        # Note: Assuming 'quizzes' relationship is populated or we query it.
        # This is simplified. Real logic might need a more complex query.
        current_score = sum([q.score for q in user.quizzes]) if user.quizzes else 0
        
        # 2. Define Winning Threshold (Dummy constant for now, or from Subscription?)
        WINNING_THRESHOLD = 50 
        
        # 3. Calculate Max Possible Remaining Score
        # Assume total quizzes possible is 5. User has taken len(user.quizzes).
        # Max score per quiz is 10.
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
        
        # Logic to pick best messenger (simplified)
        if user.phone_number:
            messenger_type = MessengerType.WHATSAPP
            receiver = user.phone_number
            
        message_text = f"You are doing great! You have {current_score} points. You need {WINNING_THRESHOLD - current_score} more to win!"
        
        sent = self.send_message(db, messenger_type, "System", receiver, message_text, user_id=user.id)
        
        if sent:
             return {"status": "success", "message": "Notification sent"}
        else:
             return {"status": "error", "message": "Failed to send notification"}

messaging_service = MessagingService()
