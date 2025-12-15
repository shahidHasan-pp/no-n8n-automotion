@echo off
echo ========================================
echo Starting Backend on 0.0.0.0:8000
echo ========================================
cd backend
call .venv\Scripts\activate
start cmd /k "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
cd ..

echo.
echo ========================================
echo Starting Frontend on 0.0.0.0:3000
echo ========================================
cd frontend
start cmd /k "npm start"
cd ..

echo.
echo ========================================
echo Both servers are starting...
echo.
echo Backend:  http://192.168.5.12:8000
echo Frontend: http://192.168.5.12:3000
echo.
echo Share this URL with your lead:
echo http://192.168.5.12:3000
echo ========================================
pause
