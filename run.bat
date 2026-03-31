@echo off
REM ========================================
REM  Food3D — Run Script (Windows)
REM  Uses uv for dependency management
REM ========================================

echo.
echo  ╔══════════════════════════════════════╗
echo  ║   Food3D — AI 3D Model Generator    ║
echo  ╚══════════════════════════════════════╝
echo.

REM Check if uv is installed
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] uv is not installed. Installing via pip...
    pip install uv
)

REM Sync dependencies
echo [1/2] Syncing dependencies with uv...
uv sync
if %errorlevel% neq 0 (
    echo [!] uv sync failed. Trying uv pip install...
    uv pip install -r requirements.txt
)

echo.
echo [2/2] Starting Food3D server...
echo      http://localhost:8000
echo.

REM Run the server
uv run python app.py

pause
