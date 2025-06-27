#!/bin/bash

echo "🚀 Starting Travel Planner Backend with Database Integration"

# Stop any running Uvicorn processes
echo "🛑 Stopping any running Uvicorn processes..."
pkill -f uvicorn || true

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