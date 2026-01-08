
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

class NotificationContextType(str, enum.Enum):
    TOP_RANKERS = "top_rankers"
    INSPIRING_TOP_10_30 = "inspiring_top_10_30"
    SOFT_REMINDER = "soft_reminder"
    CHANNEL_PROMO = "channel_promo"
    CHANNEL_CONGRATS_TOP_5 = "channel_congrats_top_5"

class MessageScenarioType(str, enum.Enum):
    UNSUBSCRIBED_REMINDER = "unsubscribed_reminder"
    DAILY_SCORE_UPDATE = "daily_score_update"
    EVE_SCORE_RANKING = "eve_score_ranking"
    SUBSCRIPTION_EXPIRY = "subscription_expiry"
    INACTIVE_SUBSCRIBER = "inactive_subscriber"
    DAILY_PLAY_REMINDER = "daily_play_reminder"
    DAILY_WINNER_CONGRATS = "daily_winner_congrats"
    DAILY_REFERRAL_PROMO = "daily_referral_promo"
    WEEKLY_WINNER_LIST_PROMO = "weekly_winner_list_promo"
    WINNING_POSITION_WARNING = "winning_position_warning"
