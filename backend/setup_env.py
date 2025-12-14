
content = """PROJECT_NAME="Notification Service"
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_SERVER=localhost
MYSQL_PORT=3306
MYSQL_DB=purplepatch-messenger

DATABASE_URL=mysql+pymysql://root:password@localhost:3306/purplepatch-messenger

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
"""
with open('.env', 'w') as f:
    f.write(content.strip())
print(".env file created successfully.")
