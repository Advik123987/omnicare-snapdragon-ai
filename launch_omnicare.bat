@echo off
title OmniCare AI - Snapdragon HP PC Clinical Edge Station
color 0B

echo ==============================================================================
echo   OMNICARE AI - SNAPDRAGON HP PC CLINICAL EDGE STATION
echo   Target: HP OmniBook X / EliteBook Ultra (Snapdragon(R) X Elite)
echo   NPU Acceleration: Qualcomm Hexagon(TM) Processor (45.0 TOPS)
echo   Security: HP Wolf Security Hardware Root-of-Trust Encrypted Vault
echo ==============================================================================
echo.

cd /d "%~dp0backend"

echo [*] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Error: Python not found in PATH. Please install Python 3.10+
    pause
    exit /b 1
)

echo [*] Freeing port 8000 if occupied by stale process...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING 2^>nul') do taskkill /f /pid %%a >nul 2>&1

echo [*] Launching OmniCare AI FastAPI Backend on Hexagon NPU...
start "OmniCare Backend" python main.py

echo [*] Waiting 4 seconds for server initialization...
timeout /t 4 /nobreak >nul

echo [*] Launching Clinical Cockpit in default browser...
start http://localhost:8000

echo.
echo ==============================================================================
echo [✓] OmniCare AI Clinical Workstation is Active!
echo ==============================================================================
echo     • Live Clinical Cockpit:  http://localhost:8000
echo     • Evaluator Showcase:     http://localhost:8000/showcase/
echo     • 10-Slide Pitch Deck:    http://localhost:8000/pitch-deck
echo     • Direct Offline File:    file:///%~dp0frontend/index.html
echo.
echo Press any key to close this launcher window (backend continues in background)...
pause >nul
