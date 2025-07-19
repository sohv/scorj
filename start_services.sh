#!/bin/bash

# ResumeRoast Startup Script
# This script starts both the backend and frontend services

echo "Starting ResumeRoast Services..."
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ".env file not found. Please create it with your API keys."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if required packages are installed
echo "Checking dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

# Function to start backend
start_backend() {
    echo "Starting Backend (FastAPI)..."
    cd backend
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    echo "Backend started on http://localhost:8000 (PID: $BACKEND_PID)"
}

# Function to start frontend
start_frontend() {
    echo "Starting Frontend (Streamlit)..."
    cd streamlit_app
    streamlit run app.py --server.port 8501 &
    FRONTEND_PID=$!
    cd ..
    echo "Frontend started on http://localhost:8501 (PID: $FRONTEND_PID)"
}

# Function to cleanup processes
cleanup() {
    echo ""
    echo "Shutting down services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "Backend stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "Frontend stopped"
    fi
    echo "ResumeRoast services stopped."
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start services
start_backend
sleep 2
start_frontend

echo ""
echo "ResumeRoast is now running!"
echo "Backend API: http://localhost:8000"
echo "Frontend UI: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=================================="

# Wait for services to be interrupted
wait
