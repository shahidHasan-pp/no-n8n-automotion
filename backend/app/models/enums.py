
import enum

class QuizType(str, enum.Enum):
    QUIZ = "quiz"
    TOURNAMENT = "tournament"

class SubscriptionType(str, enum.Enum):
    STANDARD = "STANDARD"
    PREMIUM = "PREMIUM"
    LOGIC = "LOGIC"

class SubscriptionLength(str, enum.Enum):
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"
    LIFETIME = "LIFETIME"

class MessengerType(str, enum.Enum):
    MAIL = "mail"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    DISCORD = "discord"

class PlatformStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class PlatformType(str, enum.Enum):
    QUIZARD = "quizard"
    WORDLY = "wordly"
    ARCADERUSH = "arcaderush"
