@echo off
echo ========================================
echo MeetingAI Database Connection Fix
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "app.py" (
    echo Error: Please run this script from the backend directory
    pause
    exit /b 1
)

echo Starting database connection fix...
echo.

REM Run the fix script
python fix_database_connection.py

echo.
echo ========================================
echo Fix completed!
echo ========================================
echo.
echo If the fix was successful, you can now start the backend with:
echo   python start_backend.py
echo   or
echo   python app.py
echo.
pause
