from fastapi import APIRouter
from app.api.v1.endpoints import user, subscription, messenger, quiz, notifications, telegram_bot

api_router = APIRouter()

api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(subscription.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(messenger.router, prefix="/messengers", tags=["messengers"])
api_router.include_router(quiz.router, prefix="/quizzes", tags=["quizzes"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(telegram_bot.router, prefix="/telegram", tags=["telegram-bot"])
