@echo off
echo Starting Aura Cafe AR Platform...
echo ---------------------------------------
echo.

:: 1. Force Kill any existing Python servers to avoid "Ghost" errors
echo [CLEANUP] Stopping any old AI processes...
taskkill /F /IM python.exe /T 2>nul
:: Wait a second for cleanup
timeout /t 2 >nul

:: 2. Start the Python AI Backend in a new window with LIVE output
echo [SERVER] Launching 3D AI Backend...
start "Aura AI Backend Studio" cmd /k "python server.py"

:: 3. Start the Website Server
echo [WEBSITE] Checking for Python or Node...
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [FOUND] Python - Starting website at http://localhost:8000
    start "" "http://localhost:8000"
    python -m http.server 8000
) else (
    where npx >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo [FOUND] Node/NPX - Starting website at http://localhost:3000
        start "" "http://localhost:3000"
        npx -y serve -p 3000
    ) else (
        echo [ERROR] Neither Python nor Node.js found.
        echo Please install Python to run this project.
        pause
    )
)
