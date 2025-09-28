@echo off
echo ========================================
echo Starting MeetingAI Backend Server
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "app.py" (
    echo Error: Please run this script from the backend directory
    pause
    exit /b 1
)

echo Starting backend server...
echo Server will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

REM Start the Flask app
python app.py

pause
