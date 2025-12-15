# Quick Start: Testing Telegram Bot

## Prerequisites
- Python 3.8+ installed
- Backend running
- Telegram account

## Step 1: Get Your Bot Token

1. Open Telegram
2. Search for `@BotFather`
3. Send: `/newbot`
4. Follow prompts to create bot
5. Copy the token (looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

## Step 2: Configure Environment

Edit `backend/.env`:
```env
# Replace with your actual token
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
```

For testing without a real bot:
```env
TELEGRAM_BOT_TOKEN=dummy_telegram_bot_token
```

## Step 3: Start Services

### Terminal 1 - Backend
```bash
cd backend
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/Mac
uvicorn app.main:app --reload
```

### Terminal 2 - Telegram Polling Worker
```bash
cd backend
.venv\Scripts\activate
python -m app.workers.telegram_polling --interval 5
```

## Step 4: Link Your Telegram Account

1. Open Telegram app
2. Search for your bot (use the @username you set with BotFather)
3. Click "Start" or send this command:
   ```
   /start your_username
   ```
   Replace `your_username` with your actual username from the platform

**Example:**
```
/start john_doe
```

## Step 5: Verify Connection

You should get a response like:
```
✅ Successfully linked to account: john_doe

👤 Name: John Doe
📧 Email: john@example.com

You will now receive notifications via Telegram!
```

If you get an error:
```
❌ Username 'xyz' not found in our system.

Please register on our platform first or check your username spelling.
```
This means the username doesn't exist in your database.

## Step 6: Test Sending Messages

### Option A: Via API (Swagger UI)
1. Go to http://localhost:8000/docs
2. Find `POST /api/v1/notifications/send-manual`
3. Fill in:
   - `user_id`: Your user ID
   - `messenger_type`: telegram
   - `text`: Hello from the platform!
   - `link`: (optional) https://example.com
4. Execute

### Option B: Via Python
```python
from app.services.messaging.service import messaging_service

messaging_service.send_message(
    messenger_type="telegram",
    text="Test message!",
    link="https://example.com",
    user_id=1  # Replace with actual user ID
)
```

### Option C: Via curl
```bash
curl -X POST "http://localhost:8000/api/v1/notifications/send-manual?user_id=1&messenger_type=telegram&text=Hello!&link=https://example.com"
```

## Monitoring

### Check Polling Status
```bash
curl http://localhost:8000/api/v1/telegram/polling-status
```

### Check Bot Info
```bash
curl http://localhost:8000/api/v1/telegram/bot-info
```

### View Logs
Watch the terminal running the polling worker for real-time logs:
```
[Telegram Bot] User john_doe (ID: 1) linked Telegram chat_id: 123456789
[Telegram Worker] Processed 1 updates
```

## Common Issues

### Issue: "TELEGRAM_BOT_TOKEN not set"
**Solution**: Check your `.env` file has the token and restart the backend

### Issue: "Username not found"
**Solution**: 
1. Make sure user exists in database
2. Check spelling (case-sensitive)
3. Create a test user via API first

### Issue: Bot doesn't respond
**Solution**:
1. Check polling worker is running
2. Verify bot token is correct
3. Check logs for errors
4. Try manual polling: `POST /api/v1/telegram/poll-updates`

### Issue: Messages not sending
**Solution**:
1. Verify user has linked Telegram (/start command completed)
2. Check `messenger.telegram` column has `chat_id`
3. Test bot token: `GET /api/v1/telegram/bot-info`

## Next: Create Test Users

If you don't have users in your database:

```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe"
  }'
```

## Production Deployment

For production:
1. Use webhook instead of polling (more efficient)
2. Set up HTTPS endpoint
3. Configure webhook with Telegram:
   ```bash
   curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://your-domain.com/api/v1/telegram/webhook"
   ```
4. Remove polling worker
5. Use proper secret management for tokens

## Useful Commands

```bash
# Start polling worker with custom interval
python -m app.workers.telegram_polling --interval 10

# Check what updates are pending
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates"

# Get last update for debugging 
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates?offset=-1&limit=1"
```

## Success! What's Next?

✅ Telegram bot is working
⬜ Implement scheduled notifications
⬜ Add Email support
⬜ Add WhatsApp support
⬜ Add Discord support
⬜ Implement retry logic
⬜ Add message templates
⬜ Build admin dashboard for message management
