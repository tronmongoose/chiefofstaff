#!/bin/bash

# Stop any running Uvicorn processes
echo "Stopping any running Uvicorn processes..."
pkill -f 'uvicorn'

# Wait for processes to fully terminate
sleep 2

echo "Starting backend with asyncio event loop..."
uvicorn backend:app --reload --host 0.0.0.0 --port 8000 --loop asyncio 