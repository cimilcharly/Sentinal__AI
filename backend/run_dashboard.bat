@echo off
echo =======================================================
echo    Starting ThreatSentinel ^| Hybrid AI SOC Framework
echo =======================================================

echo.
echo [0/3] Activating Virtual Environment...
if exist ..\.venv\Scripts\activate.bat (
    call ..\.venv\Scripts\activate.bat
    echo   - Virtual environment activated successfully.
) else (
    echo   - [WARNING] Virtual environment ..\.venv not found. Running globally.
)

echo [1/3] Starting Real-Time Email Ingestor (Background)...
start /b python insider_threat_system\email_ingestor.py

echo [2/3] Starting Live Threat Simulator (Background)...
start /b python live_simulator.py

echo [3/3] Launching Dashboard UI...
streamlit run streamlit_app.py

pause
