@echo off
REM OpenPoke Startup Script for Windows
REM Starts both backend and frontend services concurrently

echo.
echo 🌴 OpenPoke Startup Script
echo.

REM Check if .env exists
if not exist .env (
    echo ❌ Error: .env file not found
    echo Please copy .env.example to .env and configure your API keys:
    echo   copy .env.example .env
    exit /b 1
)

REM Check if virtual environment exists
if not exist .venv (
    echo ⚠️  Virtual environment not found. Creating one...
    python -m venv .venv
    echo ✓ Virtual environment created
)

REM Check if backend dependencies are installed
if not exist .venv\Scripts\uvicorn.exe (
    echo ⚠️  Backend dependencies not installed. Installing...
    call .venv\Scripts\activate.bat
    pip install -r server\requirements.txt
    echo ✓ Backend dependencies installed
)

REM Check if frontend dependencies are installed
if not exist web\node_modules (
    echo ⚠️  Frontend dependencies not installed. Installing...
    npm install --prefix web
    echo ✓ Frontend dependencies installed
)

echo.
echo Starting services...
echo.

REM Start backend server
echo 🚀 Starting FastAPI backend on http://localhost:8001
start "OpenPoke Backend" cmd /c "call .venv\Scripts\activate.bat && python -m server.server --reload"

REM Wait a moment for backend to start
timeout /t 2 /nobreak > nul

REM Start frontend server
echo 🚀 Starting Next.js frontend on http://localhost:3000
start "OpenPoke Frontend" cmd /c "npm run dev --prefix web"

echo.
echo ✓ Both services are starting...
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 🌴 OpenPoke is running!
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8001
echo 📚 API Docs: http://localhost:8001/docs
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Close the terminal windows to stop the services
echo.
pause
