@echo off
REM Start Python Backend and Next.js Frontend

echo 🚀 Starting NTUC Workforce Intelligence Scraper
echo ================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 18+
    exit /b 1
)

echo.
echo 📦 Starting Python Backend (Port 8000)...
start "Python Backend" cmd /k "cd backend-py && python main.py"

echo ⏳ Waiting for Python backend to initialize...
timeout /t 5 /nobreak >nul

echo.
echo 🌐 Starting Next.js Frontend (Port 3000)...
start "Next.js Frontend" cmd /k "npm run dev"

echo.
echo ✅ Services Started!
echo    - Python Backend: http://localhost:8000
echo    - Next.js Frontend: http://localhost:3000
echo    - API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C in each window to stop services
pause
