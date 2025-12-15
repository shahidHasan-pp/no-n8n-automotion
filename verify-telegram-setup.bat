@echo off
echo ========================================
echo Telegram Bot Implementation Verification
echo ========================================
echo.

cd backend
call .venv\Scripts\activate

echo Checking imports...
python -c "from app.services.messaging.telegram_bot import telegram_bot_service; print('✓ telegram_bot_service')"
if errorlevel 1 goto error

python -c "from app.services.messaging.strategies.telegram import TelegramStrategy, TelegramAdapter; print('✓ TelegramStrategy and TelegramAdapter')"
if errorlevel 1 goto error

python -c "from app.api.v1.endpoints import telegram_bot; print('✓ telegram_bot endpoints')"
if errorlevel 1 goto error

python -c "from app.workers.telegram_polling import TelegramPollingWorker; print('✓ TelegramPollingWorker')"
if errorlevel 1 goto error

echo.
echo ========================================
echo ✓ All imports successful!
echo ========================================
echo.
echo Next steps:
echo 1. Add your bot token to backend\.env:
echo    TELEGRAM_BOT_TOKEN=your_token_here
echo.
echo 2. Start the backend:
echo    uvicorn app.main:app --reload
echo.
echo 3. Start the polling worker (in another terminal):
echo    python -m app.workers.telegram_polling
echo.
echo 4. Test with Telegram:
echo    /start your_username
echo.
echo See TELEGRAM_QUICKSTART.md for detailed instructions.
echo ========================================
pause
goto end

:error
echo.
echo ========================================
echo ✗ Import failed!
echo ========================================
echo Check the error message above.
pause

:end
cd ..
