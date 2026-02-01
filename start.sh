#!/bin/bash

# Start Python Backend and Next.js Frontend

echo "🚀 Starting NTUC Workforce Intelligence Scraper"
echo "================================================"

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+"
    exit 1
fi

# Start Python backend
echo ""
echo "📦 Starting Python Backend (Port 8000)..."
cd backend-py
python main.py &
PYTHON_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for Python backend to initialize..."
sleep 5

# Start Next.js frontend
echo ""
echo "🌐 Starting Next.js Frontend (Port 3000)..."
npm run dev &
NEXTJS_PID=$!

echo ""
echo "✅ Services Started!"
echo "   - Python Backend: http://localhost:8000"
echo "   - Next.js Frontend: http://localhost:3000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Trap Ctrl+C and kill both processes
trap "echo ''; echo '🛑 Stopping services...'; kill $PYTHON_PID $NEXTJS_PID; exit" INT

# Wait for processes
wait
