@echo off
REM AI Meeting Assistant - Docker Build Script for Windows
echo 🐳 Building AI Meeting Assistant Backend Docker Image

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo [INFO] Docker is installed and running

REM Build the Docker image
echo [INFO] Building Docker image...
docker build -t ai-meeting-backend:latest .

if %errorlevel% neq 0 (
    echo [ERROR] Docker build failed!
    pause
    exit /b 1
)

echo [SUCCESS] Docker image built successfully!

REM Test the image
echo [INFO] Testing Docker image...
docker run --rm -d --name ai-meeting-test -p 5000:5000 -e DATABASE_URL="postgresql://test:test@localhost:5432/test" -e SECRET_KEY="test-secret-key" ai-meeting-backend:latest

REM Wait a moment for the container to start
timeout /t 5 /nobreak >nul

REM Check if container is running
docker ps | findstr ai-meeting-test >nul
if %errorlevel% equ 0 (
    echo [SUCCESS] Container is running!
    
    REM Test health endpoint
    echo [INFO] Testing health endpoint...
    timeout /t 10 /nobreak >nul
    
    curl -f http://localhost:5000/api/health >nul 2>&1
    if %errorlevel% equ 0 (
        echo [SUCCESS] Health endpoint is responding!
    ) else (
        echo [WARNING] Health endpoint not responding (this is expected without database)
    )
    
    REM Stop the test container
    echo [INFO] Stopping test container...
    docker stop ai-meeting-test
    echo [SUCCESS] Test container stopped
) else (
    echo [ERROR] Container failed to start!
    docker logs ai-meeting-test
    pause
    exit /b 1
)

echo [SUCCESS] Docker build and test completed successfully!
echo [INFO] Image: ai-meeting-backend:latest
echo [INFO] Ready for deployment to Render!

echo.
echo 🚀 Next Steps:
echo 1. Push your code to GitHub
echo 2. Create a new Web Service on Render
echo 3. Connect your GitHub repository
echo 4. Set the root directory to 'backend'
echo 5. Choose 'Docker' as the runtime
echo 6. Add your environment variables
echo 7. Deploy!

pause
