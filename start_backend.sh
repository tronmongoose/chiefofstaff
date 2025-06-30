#!/bin/bash

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -ti:$port > /dev/null 2>&1; then
        echo "Port $port is in use. Killing processes..."
        lsof -ti:$port | xargs kill -9
        sleep 2
        # Double check
        if lsof -ti:$port > /dev/null 2>&1; then
            echo "Failed to free port $port. Please check manually."
            exit 1
        fi
        echo "Port $port is now free."
    else
        echo "Port $port is available."
    fi
}

# Stop any running Uvicorn processes
echo "Stopping any running Uvicorn processes..."
pkill -f 'uvicorn' || true

# Check and free port 8000 if needed
check_port 8000

echo "Starting backend with asyncio event loop..."
uvicorn backend:app --reload --host 0.0.0.0 --port 8000 --loop asyncio 