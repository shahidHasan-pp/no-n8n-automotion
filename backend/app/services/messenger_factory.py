from abc import ABC, abstractmethod
from typing import Dict, Any

class MessengerService(ABC):
    @abstractmethod
    def send_message(self, recipient: str, message: str) -> bool:
        """Send a message to the recipient."""
        pass

class EmailMessenger(MessengerService):
    def send_message(self, recipient: str, message: str) -> bool:
        # Dummy implementation for Email
        print(f"[Email] Sending to {recipient}: {message}")
        return True

class WhatsAppMessenger(MessengerService):
    def send_message(self, recipient: str, message: str) -> bool:
        # Dummy implementation for WhatsApp
        print(f"[WhatsApp] Sending to {recipient}: {message}")
        return True

class TelegramMessenger(MessengerService):
    def send_message(self, recipient: str, message: str) -> bool:
        # Dummy implementation for Telegram
        print(f"[Telegram] Sending to {recipient}: {message}")
        return True

class DiscordMessenger(MessengerService):
    def send_message(self, recipient: str, message: str) -> bool:
        # Dummy implementation for Discord
        print(f"[Discord] Sending to {recipient}: {message}")
        return True

class MessengerFactory:
    """
    Factory pattern to create MessengerService instances.
    Used to decouple the creation logic from the usage logic.
    """
    _messengers: Dict[str, MessengerService] = {
        "mail": EmailMessenger(),
        "whatsapp": WhatsAppMessenger(),
        "telegram": TelegramMessenger(),
        "discord": DiscordMessenger(),
    }

    @classmethod
    def get_messenger(cls, type: str) -> MessengerService:
        messenger = cls._messengers.get(type)
        if not messenger:
            raise ValueError(f"Unknown messenger type: {type}")
        return messenger
