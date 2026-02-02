
from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Notification Service"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: Union[List[str], str] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if v == "*":
            return ["*"]
        if isinstance(v, str) and not v.startswith("["):
            if not v.strip():
                return []
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    MYSQL_USER: str = "admin"
    MYSQL_PASSWORD: str = "D3xt3r&0013"
    MYSQL_SERVER: str = "103.174.50.155"
    MYSQL_PORT: str = "3306"
    MYSQL_DB: str = "notification_service_db"
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/purplepatch_messenger"
    #"mysql+pymysql://admin:D3xt3r%260013@103.174.50.155:3306/notification_service_db"

    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: str, values: dict) -> str:
        if isinstance(v, str) and v:
            return v
        return DATABASE_URL
        #return f"mysql+pymysql://{values.get('MYSQL_USER')}:{values.get('MYSQL_PASSWORD')}@{values.get('MYSQL_SERVER')}:{values.get('MYSQL_PORT')}/{values.get('MYSQL_DB')}"

    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    # Messaging Service Credentials
    GMAIL_ACCESS_TOKEN: str = ""
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHANNEL_ID: str = ""
    DISCORD_BOT_TOKEN: str = ""
    
    # Wehooks (if needed)
    DISCORD_WEBHOOK_URL: str = ""

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
