@echo off
title Congress Trade Tracker
color 0B

echo ============================================================
echo  Congress Trade Tracker
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.11+
    pause
    exit /b 1
)

REM Check Node
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)

REM Activate venv if it exists
if exist "backend\venv\Scripts\activate.bat" (
    call backend\venv\Scripts\activate.bat
) else (
    echo WARNING: No venv found. Using system Python.
    echo Run: cd backend ^&^& python -m venv venv ^&^& venv\Scripts\activate ^&^& pip install -r requirements.txt
    echo.
)

REM Start backend
echo [1/2] Starting FastAPI backend on http://localhost:8000 ...
start "Congress Tracker — Backend" cmd /k "cd /d %~dp0backend && python main.py"

REM Give backend 3 seconds to start
timeout /t 3 /nobreak >nul

REM Start frontend
echo [2/2] Starting React frontend on http://localhost:3000 ...
start "Congress Tracker — Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ============================================================
echo  Dashboard: http://localhost:3000
echo  API docs:  http://localhost:8000/docs
echo ============================================================
echo.
echo Both windows are running. Close them to stop the app.
pause
