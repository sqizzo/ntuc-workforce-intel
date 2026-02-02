#!/bin/bash
# Start the Python backend server with venv
echo "Activating virtual environment..."
source venv/Scripts/activate
echo "Starting FastAPI server..."
python main.py
