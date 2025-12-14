
import enum

class QuizType(str, enum.Enum):
    QUIZ = "quiz"
    TOURNAMENT = "tournament"

class SubscriptionType(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class SubscriptionLength(str, enum.Enum):
    MIN_1 = "1min"
    MIN_3 = "3min"
    MIN_5 = "5min"
    MIN_10 = "10min"
    MIN_30 = "30min"

class MessengerType(str, enum.Enum):
    MAIL = "mail"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    DISCORD = "discord"

class PlatformStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
