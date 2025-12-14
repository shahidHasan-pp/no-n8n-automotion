# Notification Service

A context-aware messaging service sending notifications via Email, WhatsApp, Telegram, and Discord.

## Tech Stack
- **Backend**: FastAPI, SQLAlchemy, Celery, Alembic
- **Database**: MySQL
- **Frontend**: React
- **Queue**: Redis (for Celery)

## Design Patterns
- **Strategy Pattern**: Used for different messenger implementations (Email, WhatsApp, etc.).
- **Factory Pattern**: Used to instantiate the correct messenger strategy.

## Setup

### Prerequisites
- MySQL (running on localhost:3306)
- Redis (running on localhost:6379)
- Node.js & NPM
- Python 3.10+

### Backend Setup
1.  Navigate to `backend`:
    ```bash
    cd backend
    ```
2.  Create virtual environment and install dependencies:
    ```bash
    python -m venv .venv
    .\.venv\Scripts\activate
    pip install -r requirements.txt
    ```
3.  Configure `.env` (already set up for localhost).
4.  Run Migrations:
    ```bash
    .\.venv\Scripts\alembic upgrade head
    ```
5.  Run Server:
    ```bash
    uvicorn app.main:app --reload
    ```
6.  Run Celery Worker (in new terminal):
    ```bash
    celery -A app.core.celery_app.celery_app worker --loglevel=info -P gevent
    ```
    *(Note: on Windows, install `gevent` if needed or use `-P solo`)*

### Frontend Setup
1.  Navigate to `frontend`:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start React App:
    ```bash
    npm start
    ```
