# API Flow Analysis - PurplePatch Messenger Service

## 1. Frontend API Calls (React Components)

### **Users Module** (`src/pages/Users.js`)
| Action | Method | Endpoint Called | Purpose |
|--------|--------|----------------|---------|
| Load Users | GET | `/api/v1/users/` | Fetch all users on page load |
| Create User | POST | `/api/v1/users/` | Submit new user form (username, email, full_name, phone) |
| Update User | PUT | `/api/v1/users/{id}` | Update existing user details |
| Show Context | GET | `/api/v1/messengers/{messenger_id}` | Fetch messenger profile details for a user |

### **Subscriptions Module** (`src/pages/Subscriptions.js`)
| Action | Method | Endpoint Called | Purpose |
|--------|--------|----------------|---------|
| Load Subscriptions | GET | `/api/v1/subscriptions/` | Fetch all subscription packages on page load |
| Create Subscription | POST | `/api/v1/subscriptions/` | Submit new subscription package form |

### **Quiz (Subscribe) Module** (`src/pages/Quizzes.js`)
| Action | Method | Endpoint Called | Purpose |
|--------|--------|----------------|---------|
| Load Packages | GET | `/api/v1/subscriptions/` | Populate dropdown with available packages |
| Subscribe User | POST | `/api/v1/quizzes/subscribe` | Link a user to a subscription package |

### **Messages Module** (`src/pages/Messages.js`)
| Action | Method | Endpoint Called | Purpose |
|--------|--------|----------------|---------|
| Load Messages | GET | `/api/v1/messengers/messages` | Fetch all message history logs |
| Refresh | GET | `/api/v1/messengers/messages` | Reload message list on button click |

---

## 2. Backend API Endpoints

### **Users API** (`/api/v1/users`)
| Endpoint | Method | Request Body | Response | Description |
|----------|--------|--------------|----------|-------------|
| `/` | GET | - | `List[User]` | Retrieve all users (paginated: skip, limit) |
| `/` | POST | `UserCreate` | `User` | Create a new user |
| `/{user_id}` | GET | - | `User` | Get user by ID |
| `/{user_id}` | PUT | `UserUpdate` | `User` | Update user details |

**Request/Response Schemas:**
```json
// UserCreate
{
  "username": "string",
  "email": "string",
  "full_name": "string",
  "phone_number": "string" (optional)
}

// User (Response)
{
  "id": integer,
  "username": "string",
  "email": "string",
  "full_name": "string",
  "phone_number": "string",
  "messenger_id": integer,
  "subscription_id": integer,
  "quiz_ids": [],
  "created_at": "datetime",
  "modified_at": "datetime"
}
```

### **Subscriptions API** (`/api/v1/subscriptions`)
| Endpoint | Method | Request Body | Response | Description |
|----------|--------|--------------|----------|-------------|
| `/` | GET | - | `List[Subscription]` | Retrieve all subscription packages |
| `/` | POST | `SubscriptionCreate` | `Subscription` | Create a new subscription package |
| `/{sub_id}` | GET | - | `Subscription` | Get subscription by ID |

**Request/Response Schemas:**
```json
// SubscriptionCreate
{
  "name": "string",
  "type": "STANDARD" | "PREMIUM" | "LOGIC",
  "time": "MONTHLY" | "YEARLY" | "LIFETIME",
  "offer": "string" (optional),
  "prize": "string" (optional),
  "remark": [] (optional),
  "start_date": "datetime" (optional),
  "end_date": "datetime" (optional)
}

// Subscription (Response)
{
  "id": integer,
  "name": "string",
  "type": "STANDARD" | "PREMIUM" | "LOGIC",
  "time": "MONTHLY" | "YEARLY" | "LIFETIME",
  "offer": "string",
  "prize": "string",
  "current_subs_quantity": integer,
  "created_at": "datetime",
  "modified_at": "datetime"
}
```

### **Quizzes API** (`/api/v1/quizzes`)
| Endpoint | Method | Request Body | Response | Description |
|----------|--------|--------------|----------|-------------|
| `/subscribe` | POST | `{username, subscription_name}` | `UserSubscribed` | Subscribe a user to a package |
| `/` | GET | - | `List[Quiz]` | Get all quiz results |
| `/` | POST | `QuizCreate` | `Quiz` | Create a quiz result |

**Request/Response Schemas:**
```json
// Subscribe Request
{
  "username": "string",
  "subscription_name": "string"
}

// UserSubscribed (Response)
{
  "id": integer,
  "user_id": integer,
  "subs_id": integer,
  "created_at": "datetime",
  "modified_at": "datetime"
}
```

### **Messengers API** (`/api/v1/messengers`)
| Endpoint | Method | Request Body | Response | Description |
|----------|--------|--------------|----------|-------------|
| `/` | POST | `MessengerCreate` | `Messenger` | Create a messenger profile |
| `/{id}` | GET | - | `Messenger` | Get messenger profile by ID |
| `/messages` | GET | - | `List[Message]` | Get all message history |
| `/send` | POST | `MessageCreate` | `{message}` | Queue a message for sending (Celery) |

**Request/Response Schemas:**
```json
// Messenger (Response)
{
  "id": integer,
  "mail": ["email@example.com"],
  "whatsapp": ["+1234567890"],
  "telegram": ["@username"],
  "discord": ["user#1234"],
  "created_at": "datetime",
  "modified_at": "datetime"
}

// Message (Response)
{
  "id": integer,
  "messenger_type": "mail" | "whatsapp" | "telegram" | "discord",
  "text": "string",
  "link": "string" (optional),
  "time": "datetime",
  "created_at": "datetime",
  "modified_at": "datetime"
}
```

---

## 3. Frontend-to-Backend API Mapping

### Users Page → Backend
```
[Users.js]
  ├─ useEffect() → GET /api/v1/users/
  ├─ handleSubmit() → POST /api/v1/users/
  ├─ handleUpdate() → PUT /api/v1/users/{id}
  └─ showContext() → GET /api/v1/messengers/{messenger_id}
```

### Subscriptions Page → Backend
```
[Subscriptions.js]
  ├─ useEffect() → GET /api/v1/subscriptions/
  └─ handleSubmit() → POST /api/v1/subscriptions/
```

### Quiz (Subscribe) Page → Backend
```
[Quizzes.js]
  ├─ useEffect() → GET /api/v1/subscriptions/ (for dropdown)
  └─ handleSubmit() → POST /api/v1/quizzes/subscribe
```

### Messages Page → Backend
```
[Messages.js]
  ├─ useEffect() → GET /api/v1/messengers/messages
  └─ onClick(Refresh) → GET /api/v1/messengers/messages
```

---

## 4. Backend API → Database Interactions

### **Users Endpoints** → Database
| Endpoint | CRUD Operation | Tables Accessed | SQL Operation |
|----------|----------------|-----------------|---------------|
| `GET /users/` | READ | `users` | `SELECT * FROM users LIMIT {limit} OFFSET {skip}` |
| `POST /users/` | CREATE | `users` | `INSERT INTO users (...) VALUES (...)` |
| `PUT /users/{id}` | UPDATE | `users` | `UPDATE users SET ... WHERE id = {id}` |
| `GET /users/{id}` | READ | `users` | `SELECT * FROM users WHERE id = {id}` |

**CRUD Layer:** `app/crud/user.py` → `CRUDUser`  
**Model:** `app/models/user.py` → `User`

### **Subscriptions Endpoints** → Database
| Endpoint | CRUD Operation | Tables Accessed | SQL Operation |
|----------|----------------|-----------------|---------------|
| `GET /subscriptions/` | READ | `subscriptions` | `SELECT * FROM subscriptions LIMIT {limit} OFFSET {skip}` |
| `POST /subscriptions/` | CREATE | `subscriptions` | `INSERT INTO subscriptions (...) VALUES (...)` |
| `GET /subscriptions/{id}` | READ | `subscriptions` | `SELECT * FROM subscriptions WHERE id = {id}` |

**CRUD Layer:** `app/crud/subscription.py` → `CRUDSubscription`  
**Model:** `app/models/subscription.py` → `Subscription`  
**Special Methods:**
- `get_by_name(name)` - Used by Quiz subscribe endpoint

### **Quizzes Endpoints** → Database
| Endpoint | CRUD Operation | Tables Accessed | SQL Operation |
|----------|----------------|-----------------|---------------|
| `POST /quizzes/subscribe` | CREATE + UPDATE | `user_subscribed`, `subscriptions`, `users` | 1. `SELECT * FROM users WHERE username = {username}`<br>2. `SELECT * FROM subscriptions WHERE name = {name}`<br>3. `INSERT INTO user_subscribed (user_id, subs_id) VALUES (...)`<br>4. `UPDATE subscriptions SET current_subs_quantity = current_subs_quantity + 1 WHERE id = {subs_id}` |
| `GET /quizzes/` | READ | `quizzes` | `SELECT * FROM quizzes` |
| `POST /quizzes/` | CREATE | `quizzes` | `INSERT INTO quizzes (...) VALUES (...)` |

**CRUD Layer:** 
- `app/crud/quiz.py` → `CRUDQuiz`, `CRUDUserSubscribed`
- `app/crud/user.py` → `get_by_username()`
- `app/crud/subscription.py` → `get_by_name()`

**Models:** 
- `app/models/quiz.py` → `Quiz`, `UserSubscribed`

### **Messengers Endpoints** → Database
| Endpoint | CRUD Operation | Tables Accessed | SQL Operation |
|----------|----------------|-----------------|---------------|
| `GET /messengers/{id}` | READ | `messengers` | `SELECT * FROM messengers WHERE id = {id}` |
| `POST /messengers/` | CREATE | `messengers` | `INSERT INTO messengers (...) VALUES (...)` |
| `GET /messengers/messages` | READ | `messages` | `SELECT * FROM messages LIMIT {limit} OFFSET {skip}` |
| `POST /messengers/send` | CREATE (async) | `messages` | Queued via Celery task → Eventually `INSERT INTO messages (...)` |

**CRUD Layer:** 
- `app/crud/messenger.py` → `CRUDMessenger`
- `app/crud/messenger.py` → `CRUDMessage`

**Models:** 
- `app/models/messenger.py` → `Messenger`, `Message`

**Background Tasks:**
- `POST /messengers/send` triggers Celery task `send_notification_task`

---

## 5. Database Schema Summary

### Tables & Relationships
```
users
├─ id (PK)
├─ username
├─ email
├─ messenger_id (FK → messengers.id)
└─ subscription_id (FK → subscriptions.id)

messengers
├─ id (PK)
├─ mail (JSON)
├─ whatsapp (JSON)
├─ telegram (JSON)
└─ discord (JSON)

subscriptions
├─ id (PK)
├─ name
├─ type (ENUM: STANDARD, PREMIUM, LOGIC)
├─ time (ENUM: MONTHLY, YEARLY, LIFETIME)
├─ offer
├─ prize
└─ current_subs_quantity (increments on subscribe)

user_subscribed (Many-to-Many: users ↔ subscriptions)
├─ id (PK)
├─ user_id (FK → users.id)
└─ subs_id (FK → subscriptions.id)

quizzes
├─ id (PK)
├─ user_id (FK → users.id)
├─ subs_id (FK → subscriptions.id)
├─ score
└─ time

messages
├─ id (PK)
├─ messenger_type (ENUM: mail, whatsapp, telegram, discord)
├─ text
├─ link
└─ time
```

---

## 6. Special Business Logic

### **User Subscription Flow** (`POST /quizzes/subscribe`)
1. **Input**: `username` (string), `subscription_name` (string)
2. **Process**:
   - Lookup user by username
   - Lookup subscription by name (or fallback to ID)
   - Create `UserSubscribed` record
   - **Increment** `subscriptions.current_subs_quantity`
3. **Output**: `UserSubscribed` object

### **Message Sending Flow** (`POST /messengers/send`)
1. **Input**: `MessageCreate` (messenger_type, text, link, user_id)
2. **Process**:
   - Queue Celery task `send_notification_task`
   - Task resolves user's messenger details
   - Sends message via appropriate channel (Mail, WhatsApp, etc.)
   - Logs message to `messages` table
3. **Output**: Immediate response `{"message": "Message queued"}`

---

## 7. API Base URL
- **Backend**: `http://localhost:8000`
- **Frontend**: `http://localhost:3000`
- **API Prefix**: `/api/v1`

## 8. Authentication
- **Current Status**: No authentication implemented
- **Future**: Add JWT/OAuth for protected routes

## 9. CORS Configuration
- **Allowed Origins**: `http://localhost:3000` (Development)
- **Middleware**: Starlette CORS Middleware
