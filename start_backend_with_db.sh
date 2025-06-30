#!/bin/bash

echo "🚀 Starting Travel Planner Backend with Database Integration"

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -ti:$port > /dev/null 2>&1; then
        echo "🛑 Port $port is in use. Killing processes..."
        lsof -ti:$port | xargs kill -9
        sleep 2
        # Double check
        if lsof -ti:$port > /dev/null 2>&1; then
            echo "❌ Failed to free port $port. Please check manually."
            exit 1
        fi
        echo "✅ Port $port is now free."
    else
        echo "✅ Port $port is available."
    fi
}

# Stop any running Uvicorn processes
echo "🛑 Stopping any running Uvicorn processes..."
pkill -f uvicorn || true

# Check and free port 8000 if needed
check_port 8000

# Start database if not running
echo "🗄️ Checking database status..."
if ! docker-compose ps postgres | grep -q "Up"; then
    echo "📊 Starting PostgreSQL database..."
    docker-compose up -d postgres
    echo "⏳ Waiting for database to be ready..."
    sleep 10
fi

# Install database dependencies if needed
echo "🔧 Installing database dependencies..."
pip install sqlalchemy psycopg2-binary alembic

# Run database migrations
echo "🗄️ Running database migrations..."
alembic upgrade head

# Start the backend with asyncio event loop
echo "🚀 Starting backend with asyncio event loop..."
python -m uvicorn backend:app --host 0.0.0.0 --port 8000 --reload 