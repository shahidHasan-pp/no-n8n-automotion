from celery import shared_task
from app.api import deps
from app.services.messaging import messaging_service
from app.models.enums import MessengerType, MessageScenarioType
from app.database.session import SessionLocal

@shared_task(name="run_messaging_scenario")
def run_messaging_scenario(scenario_type_str: str, messenger_type_str: str = "telegram"):
    """
    Celery task to run a specific messaging scenario.
    """
    db = SessionLocal()
    try:
        scenario_type = MessageScenarioType(scenario_type_str)
        messenger_type = MessengerType(messenger_type_str)
        
        result = messaging_service.send_scenario_messages(db, scenario_type, messenger_type)
        return result
    finally:
        db.close()
