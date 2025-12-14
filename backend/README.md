# Backend Setup and Running Instructions

This document outlines the steps to set up and run the backend services for the AI Post Scheduler application.

## 1. Navigate to the Backend Dir & create and install python packages

First, change your current directory to the `backend` folder:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Connect to MySQL and Create Database

Connect to your MySQL server and create the necessary database:

```bash
mysql -u root -p
```
(Enter your MySQL password when prompted)

```sql
CREATE DATABASE social_scheduler;
```

## 3. Run the Backend Application

Start the FastAPI application using Uvicorn:

```bash
alembic revision --autogenerate -m "core db models"
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 4. Migrate DB and Seed Dummy Data (Optional)

To populate your database with sample data, run the provided SQL script:

```bash

mysql -u root -p social_scheduler < scripts/dummy_seed.sql
```
(Enter your MySQL password when prompted)

## 5. Start Redis Server

Ensure your Redis server is running:

```bash
sudo systemctl start redis-server
```

## 6. Run Celery Worker and Celery Beat

Start the Celery worker and Celery beat processes for background tasks and scheduling:

```bash
celery -A app.tasks.celery worker --loglevel=info &
```

```bash
celery -A app.tasks.celery beat --loglevel=info
```