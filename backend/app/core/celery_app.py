
from celery import Celery
from app.core.config import settings

celery_app = Celery("worker", broker=settings.CELERY_BROKER_URL)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Dhaka",
    enable_utc=True,
    include=["app.tasks.celery", "app.tasks.scenario"],
)

from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    "unsubscribed-reminder-daily": {
        "task": "run_messaging_scenario",
        "schedule": crontab(hour=11, minute=0), # 11 AM
        "args": ("unsubscribed_reminder", "telegram"),
    },
    "subscription-expiry-check": {
        "task": "run_messaging_scenario",
        "schedule": crontab(hour=9, minute=0), # 9 AM
        "args": ("subscription_expiry", "telegram"),
    },
    "daily-play-reminder-10am": {
        "task": "run_messaging_scenario",
        "schedule": crontab(hour=10, minute=0),
        "args": ("daily_play_reminder", "telegram"),
    },
    "daily-referral-promo-12pm": {
        "task": "run_messaging_scenario",
        "schedule": crontab(hour=12, minute=0),
        "args": ("daily_referral_promo", "telegram"),
    },
    "eve-rank-status-10pm": {
        "task": "run_messaging_scenario",
        "schedule": crontab(hour=22, minute=0),
        "args": ("eve_score_ranking", "telegram"),
    },
    "winning-warning-1030pm": {
        "task": "run_messaging_scenario",
        "schedule": crontab(hour=22, minute=30),
        "args": ("winning_position_warning", "telegram"),
    },
    "daily-winner-congrats-12am": {
        "task": "run_messaging_scenario",
        "schedule": crontab(hour=0, minute=5), # 12:05 AM
        "args": ("daily_winner_congrats", "telegram"),
    },
    "inactive-subscriber-check": {
        "task": "run_messaging_scenario",
        "schedule": crontab(hour=15, minute=0), # 3 PM
        "args": ("inactive_subscriber", "telegram"),
    },
    "weekly-streak-check": {
        "task": "run_messaging_scenario",
        "schedule": crontab(hour=11, minute=30), # 11:30 AM
        "args": ("weekly_winner_list_promo", "telegram"),
    },
}
