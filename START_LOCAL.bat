@echo off
echo ========================================
echo   SENTINEL AI - LOCAL STARTUP (No Docker)
echo ========================================

echo.
echo Starting Backend (FastAPI)...
start "Sentinel AI Backend" cmd /k "cd /d %~dp0backend && ..\.venv\Scripts\python.exe -m uvicorn main:app --port 8000 --env-file ..\.env"

echo.
echo Starting Frontend (Next.js)...
start "Sentinel AI Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo   ✅ SENTINEL AI STARTED LOCALLY!
echo ========================================
echo Access Sentinel AI at:
echo   API Docs:  http://localhost:8000/docs
echo   Dashboard: http://localhost:3000
echo.
echo Demo credentials:
echo   Email:     admin@acmecorp.com
echo   Password:  password123
echo.
echo Close the two new command prompt windows to stop the servers.
pause
