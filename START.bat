@echo off
REM Windows startup script for InsiderThreat-AI SaaS

echo.
echo ========================================
echo   SENTINEL AI - STARTUP
echo ========================================
echo.

echo Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker from https://www.docker.com/
    pause
    exit /b 1
)

echo Checking Docker Compose...
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker Compose is not installed
    pause
    exit /b 1
)

echo.
echo Starting Sentinel AI services...
echo   - PostgreSQL database
echo   - Redis cache
echo   - FastAPI backend (port 8000)
echo   - Next.js frontend (port 3000)
echo.

docker-compose down 2>nul

echo.
echo Pulling latest images...
docker-compose pull

echo.
echo Starting services (this may take 30 seconds)...
docker-compose up -d

echo.
echo Waiting for services to be ready...
timeout /t 5 /nobreak

echo.
echo Initializing database...
docker exec insider_threat_api python backend/init_db.py

echo.
echo ========================================
echo   ✅ SENTINEL AI STARTED!
echo ========================================
echo.
echo Access Sentinel AI at:
echo   API Docs:  http://localhost:8000/docs
echo   Dashboard: http://localhost:3000
echo.
echo Demo credentials:
echo   Email:     admin@acmecorp.com
echo   Password:  password123
echo.
echo To view logs:
echo   docker-compose logs -f backend
echo.
echo To stop services:
echo   docker-compose down
echo.
echo.
