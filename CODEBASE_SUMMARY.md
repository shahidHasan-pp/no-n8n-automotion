# 📱 Notification Service - Comprehensive Codebase Summary

## 🎯 What is This Application?

This is a **context-aware, multi-channel notification service** that sends messages to users across multiple communication platforms including **Telegram, Discord, WhatsApp, and Email**. The application is designed using professional software design patterns and provides both automated business logic-based notifications and manual notification capabilities.

---

## 🏗️ Architecture Overview

### Core Design Philosophy
The application follows **Modern Software Design Patterns**:
- **Strategy Pattern**: Different messaging channels (Telegram, Email, WhatsApp, Discord) are implemented as interchangeable strategies
- **Adapter Pattern**: Provides convenience wrappers around messaging strategies
- **Factory Pattern**: Instantiates the correct messenger strategy based on type
- **Separation of Concerns**: Clean separation between API, business logic, data access, and external services

---

## 🔧 How Does It Work?

### 1. **User Management System**
Users in the system have:
- **Profile Information**: username, email, phone number, full name
- **Messenger Profile**: Stores connection details for each platform (chat IDs, phone numbers, etc.)
- **Subscription**: Can be linked to subscription plans
- **Quiz Tracking**: Records quiz scores for gamification/notification logic

### 2. **Messaging Flow**

```
┌─────────────────────────────────────────────────────────────┐
│                    User Request Layer                        │
│  (Frontend UI / API Endpoints / Background Workers)          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              MessagingService (Orchestrator)                 │
│  - Routes messages to appropriate strategy                   │
│  - Handles business logic (should user receive message?)     │
│  - Logs messages to database                                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┬─────────────┐
          │               │               │             │
          ▼               ▼               ▼             ▼
    ┌─────────┐    ┌─────────┐    ┌─────────┐   ┌─────────┐
    │Telegram │    │ Discord │    │WhatsApp │   │  Email  │
    │Strategy │    │Strategy │    │Strategy │   │Strategy │
    └─────────┘    └─────────┘    └─────────┘   └─────────┘
          │               │               │             │
          └───────────────┴───────────────┴─────────────┘
                          │
                          ▼
              External Messaging APIs
       (Telegram Bot API, Discord API, etc.)
```

### 3. **Message Sending Process**

**Step-by-step flow:**

1. **Request Initiated**: Via API endpoint, Celery task, or background worker
2. **User Lookup**: System retrieves user details from database
3. **Contact Resolution**: 
   - Checks user's messenger profile for platform-specific contact info
   - For Telegram: Uses stored `chat_id`
   - For Discord: Uses `dm_channel_id` or `user_id`
   - For WhatsApp: Uses phone number
   - For Email: Uses email address
4. **Strategy Selection**: Chooses the appropriate messaging strategy
5. **Message Delivery**: Strategy sends message via platform API
6. **Logging**: Message details saved to database for audit trail

### 4. **User Onboarding (Telegram Example)**

For platforms like Telegram that require user authorization:

```
User in Telegram → /start username → Bot receives command
                                      ↓
                          Bot validates username in database
                                      ↓
                          Stores chat_id in user's messenger profile
                                      ↓
                          Sends confirmation to user
                                      ↓
                          User can now receive notifications
```

This is powered by:
- **TelegramBotService**: Polls for updates, processes commands
- **Telegram Worker**: Background process that continuously polls
- **API Endpoints**: Manual polling trigger and webhook support

---

## 📦 Technology Stack

### Backend Technologies
| Technology | Purpose | Version/Details |
|------------|---------|-----------------|
| **FastAPI** | Web framework | Modern async Python framework |
| **SQLAlchemy** | ORM | Database abstraction layer |
| **Alembic** | Migrations | Database schema versioning |
| **MySQL** | Database | Main data store (MySQL 8.0) |
| **Redis** | Queue/Cache | Message broker for Celery |
| **Celery** | Task Queue | Async task processing with `gevent` pool |
| **Pydantic** | Validation | Data validation and settings |
| **PyMySQL** | Driver | MySQL database driver |
| **Requests** | HTTP Client | API calls to external services |

### Frontend Technologies
| Technology | Purpose |
|------------|---------|
| **React** | UI Framework (v19.2.3) |
| **React Router** | Navigation (v7.10.1) |
| **React Scripts** | Build tooling (v5.0.1) |

### Infrastructure
| Component | Details |
|-----------|---------|
| **Docker Compose** | Multi-container orchestration |
| **CORS Middleware** | Cross-origin support for frontend |
| **Environment Config** | `.env` based configuration |

---

## 🗂️ Project Structure

```
no-n8n-automotion/
│
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── main.py                  # FastAPI app entry + middleware
│   │   ├── config.py                # Configuration settings
│   │   │
│   │   ├── api/v1/                  # API Layer (v1)
│   │   │   ├── router.py           # Main router
│   │   │   └── endpoints/
│   │   │       ├── notifications.py # Notification endpoints
│   │   │       ├── telegram_bot.py  # Telegram bot endpoints
│   │   │       ├── user.py          # User CRUD endpoints
│   │   │       ├── messenger.py     # Messenger profile endpoints
│   │   │       └── subscription.py  # Subscription endpoints
│   │   │
│   │   ├── services/                # Business Logic Layer
│   │   │   ├── messaging/
│   │   │   │   ├── service.py       # Main messaging orchestrator
│   │   │   │   ├── telegram_bot.py  # Telegram bot service (polling, commands)
│   │   │   │   └── strategies/      # Strategy Pattern Implementation
│   │   │   │       ├── base.py      # MessagingStrategy interface
│   │   │   │       ├── telegram.py  # Telegram strategy + adapter
│   │   │   │       ├── discord.py   # Discord strategy
│   │   │   │       ├── whatsapp.py  # WhatsApp strategy
│   │   │   │       └── email.py     # Email strategy (Gmail API)
│   │   │   │
│   │   │   └── subscription_service.py
│   │   │
│   │   ├── crud/                    # Data Access Layer
│   │   │   ├── user.py             # User CRUD operations
│   │   │   ├── messenger.py        # Messenger CRUD
│   │   │   ├── message.py          # Message logging
│   │   │   └── subscription.py     # Subscription CRUD
│   │   │
│   │   ├── models/                  # SQLAlchemy Models
│   │   │   ├── user.py             # User model
│   │   │   ├── messenger.py        # Messenger + Message models
│   │   │   ├── subscription.py     # Subscription model
│   │   │   ├── quiz.py             # Quiz model
│   │   │   └── enums.py            # Enumerations
│   │   │
│   │   ├── schemas/                 # Pydantic Schemas
│   │   │   ├── user.py
│   │   │   ├── messenger.py
│   │   │   └── subscription.py
│   │   │
│   │   ├── tasks/                   # Celery Tasks
│   │   │   └── notification.py     # Async notification task
│   │   │
│   │   ├── workers/                 # Background Workers
│   │   │   └── telegram_polling.py # Continuous Telegram polling
│   │   │
│   │   ├── core/                    # Core Utilities
│   │   │   ├── celery_app.py       # Celery configuration
│   │   │   ├── config.py           # Settings loader
│   │   │   ├── middleware.py       # JWT middleware (placeholder)
│   │   │   └── exceptions.py       # Exception handlers
│   │   │
│   │   ├── database/
│   │   │   └── session.py          # DB session management
│   │   │
│   │   └── utils/
│   │       └── logger.py           # Logging utilities
│   │
│   ├── alembic/                     # Database Migrations
│   ├── requirements.txt
│   └── .env                         # Environment variables
│
├── frontend/                        # React Frontend
│   ├── src/
│   │   ├── App.js                  # Main app routing
│   │   ├── pages/
│   │   │   ├── Users.js            # User list with search/filter
│   │   │   ├── UserDetail.js       # User details view
│   │   │   ├── MessagingCenterPage.js # Send notifications UI
│   │   │   ├── Messages.js         # Message history
│   │   │   ├── Subscriptions.js    # Subscription management
│   │   │   └── Quizzes.js          # Quiz management
│   │   │
│   │   └── components/
│   │       └── Navbar.js           # Navigation bar
│   │
│   └── package.json
│
├── docker-compose.yml               # Docker orchestration
└── README.md                        # Main documentation
```

---

## 🗃️ Database Schema

### Core Tables

**1. users**
```sql
- id (Primary Key)
- username (Unique)
- email (Unique)
- full_name
- phone_number
- quiz_ids (JSON array)
- messenger_id (Foreign Key → messengers)
- subscription_id (Foreign Key → subscriptions)
```

**2. messengers**
```sql
- id (Primary Key)
- mail (JSON) - Email configuration
- telegram (JSON) - {"chat_id": 123, "user_id": 456, "username": "...", "linked_at": ...}
- whatsapp (JSON) - {"phone": "+1234567890"}
- discord (JSON) - {"dm_channel_id": "...", "user_id": "..."}
```

**3. messages**
```sql
- id (Primary Key)
- text
- link
- time (Timestamp)
- messenger_type (ENUM: mail, telegram, whatsapp, discord)
- user_id (Foreign Key → users)
```

**4. subscriptions**
```sql
- id (Primary Key)
- name
- type (ENUM: STANDARD, PREMIUM, LOGIC)
- time (ENUM: MONTHLY, YEARLY, LIFETIME)
- offer
- prize
- remark (JSON)
- current_subs_quantity
- amount
- link
- start_date
- end_date
```

**5. quizzes**
```sql
- id (Primary Key)
- user_id (Foreign Key)
- score
- quiz_type (ENUM: quiz, tournament)
```

---

## 🔑 Key Features

### 1. **Multi-Channel Messaging**
- ✅ Telegram (via Bot API + polling/webhook)
- ✅ Discord (via Bot + DM channels)
- ✅ WhatsApp (via Meta Business API)
- ✅ Email (via Gmail API)

### 2. **Intelligent Message Routing**
- Automatically selects best channel for user
- Priority: Telegram → WhatsApp → Discord → Email
- Fallback mechanisms if primary channel unavailable

### 3. **Business Logic Integration**
- **Daily Check System**: Evaluates if user should receive notification
- **Score Tracking**: Monitors quiz performance
- **Winning Threshold Logic**: Sends encouragement if user can still win
- Example: "You have 30 points. You need 20 more to win!"

### 4. **User Onboarding**
- Platform-specific onboarding flows (e.g., `/start` for Telegram)
- Username validation against database
- Secure chat ID storage
- Confirmation messages

### 5. **Manual & Automated Notifications**
- **Manual**: Admin can send via API or UI
- **Bulk**: Send to all users or filtered by subscription
- **Triggered**: Business logic-based automatic notifications
- **Async Processing**: Via Celery for high-volume scenarios

### 6. **Frontend Dashboard**
- User management (search, filter, pagination)
- Subscription tracking
- Message center for sending notifications
- Message history viewing
- Quiz management

### 7. **Advanced Search & Filtering**
- Search by username, email, phone
- Filter by subscription status
- Filter by message context
- Pagination (configurable items per page)

---

## 🚀 How to Run

### Prerequisites
- MySQL (localhost:3306)
- Redis (localhost:6379)
- Python 3.10+
- Node.js & NPM

### Backend Setup
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# Configure .env file with API tokens
# Run migrations
.\.venv\Scripts\alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload

# Start Celery worker (separate terminal)
celery -A app.core.celery_app.celery_app worker --loglevel=info -P gevent

# Start Telegram polling worker (separate terminal, optional)
python -m app.workers.telegram_polling --interval 5
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Docker Setup (Alternative)
```bash
docker-compose up
```

---

## 🔌 API Endpoints

### Notifications
```
POST /api/v1/notifications/send-manual
  - Send notification to specific user
  - Params: user_id, messenger_type, text, link

POST /api/v1/notifications/trigger-logic-check
  - Trigger business logic check for user
  - Params: user_id

POST /api/v1/notifications/send-bulk
  - Send bulk notifications
  - Params: messenger_type, text, link, has_subscription, subscription_id
```

### Telegram Bot
```
GET  /api/v1/telegram/bot-info
POST /api/v1/telegram/poll-updates
GET  /api/v1/telegram/polling-status
POST /api/v1/telegram/webhook
```

### Users
```
GET  /api/v1/users/
POST /api/v1/users/
GET  /api/v1/users/{user_id}
PUT  /api/v1/users/{user_id}
```

### Subscriptions
```
GET  /api/v1/subscriptions/
POST /api/v1/subscriptions/
GET  /api/v1/subscriptions/{subscription_id}
```

---

## 🛡️ Configuration

### Environment Variables (.env)
```bash
# Database
MYSQL_USER=user
MYSQL_PASSWORD=password
MYSQL_SERVER=localhost
MYSQL_PORT=3306
MYSQL_DB=notification_db

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Messaging APIs
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
DISCORD_BOT_TOKEN=your_discord_bot_token
WHATSAPP_ACCESS_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
GMAIL_ACCESS_TOKEN=your_gmail_token
```

---

## 🎯 Use Cases

### Use Case 1: Daily Engagement Notifications
System automatically checks each user's quiz progress and sends motivational messages if they still have a chance to win.

### Use Case 2: Subscription Updates
When subscriptions expire or new offers are available, bulk notifications sent to all subscribed users via their preferred channel.

### Use Case 3: Multi-Channel User Outreach
Admin can send announcements via messaging center UI, and system automatically routes to each user's preferred/available channel.

### Use Case 4: User Onboarding
New users link their Telegram/Discord accounts via bot commands, enabling seamless notification delivery.

---

## 🎨 Design Patterns Used

### 1. **Strategy Pattern**
```python
class MessagingStrategy(ABC):
    @abstractmethod
    def send(self, to, content, link, extra_data) -> bool:
        pass

class TelegramStrategy(MessagingStrategy):
    def send(self, to, content, link, extra_data):
        # Telegram-specific implementation
        
class EmailStrategy(MessagingStrategy):
    def send(self, to, content, link, extra_data):
        # Email-specific implementation
```

**Benefit**: Easy to add new channels without changing existing code

### 2. **Adapter Pattern**
```python
class TelegramAdapter:
    def __init__(self):
        self.strategy = TelegramStrategy()
    
    def send_notification(self, chat_id, message, link):
        return self.strategy.send(...)
    
    def send_alert(self, chat_id, alert_text):
        # Convenience method with special formatting
```

**Benefit**: Provides higher-level, platform-specific convenience methods

### 3. **Dependency Injection**
FastAPI endpoints use `Depends()` for database sessions and services

**Benefit**: Testability and loose coupling

---

## 🔒 Security Features

- ✅ Environment variables for sensitive tokens
- ✅ `.env` files gitignored
- ✅ User validation before storing contact info
- ✅ CORS middleware for frontend protection
- ✅ Exception handling to prevent data leaks
- ✅ Dummy token mode for testing without real APIs

---

## 📊 Monitoring & Logging

- Comprehensive logging via `app.utils.logger`
- All messages logged to database with timestamp
- Real-time worker logs for debugging
- API request/response tracking

---

## 🌟 Unique Selling Points

1. **Channel Agnostic**: Same code works for any messaging platform
2. **Business Logic Integration**: Not just a notification sender, includes conditional logic
3. **User Preference Detection**: Automatically selects best available channel
4. **Bidirectional**: Users can interact with bot (commands, onboarding)
5. **Scalable**: Celery queue for async processing
6. **Modern Stack**: FastAPI, React, Docker-ready

---

## 🛠️ Technologies Deep Dive

### Why These Technologies?

**FastAPI**
- Async support for high performance
- Automatic API documentation (Swagger UI)
- Modern Python type hints
- Fast development

**SQLAlchemy + Alembic**
- Database-agnostic ORM
- Version-controlled schema changes
- Complex relationship handling

**Celery + Redis**
- Distributed task processing
- Retry mechanisms
- Scheduled tasks support

**React**
- Component-based UI
- Rich ecosystem
- Fast rendering

**Docker Compose**
- Easy multi-service orchestration
- Environment consistency
- One-command deployment

---

## 📈 Future Enhancements (Based on TODO in Code)

- [ ] Webhook support for production (currently polling-based)
- [ ] Message templates system
- [ ] Retry logic for failed messages
- [ ] Admin analytics dashboard
- [ ] SMS channel integration
- [ ] Multi-language support
- [ ] Message scheduling
- [ ] User preferences UI (choose preferred channel)

---

## 🧪 Testing

### Dummy Mode
Set tokens to `dummy_*` values to test without real API calls:
```bash
TELEGRAM_BOT_TOKEN=dummy_telegram_bot_token
```

All operations will log to console instead of calling external APIs.

---

## 📝 Summary

This is a **professional-grade, multi-channel notification service** built with:

✅ **Modern Architecture**: Clean separation, design patterns, scalable  
✅ **Multiple Channels**: Telegram, Discord, WhatsApp, Email  
✅ **Smart Routing**: Automatic channel selection based on user availability  
✅ **Business Logic**: Conditional notifications based on user state  
✅ **Full Stack**: React frontend + FastAPI backend  
✅ **Production Ready**: Docker, Celery, migrations, logging  
✅ **Extensible**: Easy to add new channels or features  

**Core Value**: Provides a unified API to send context-aware notifications across multiple platforms without worrying about individual platform complexities.
