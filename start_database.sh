#!/bin/bash

echo "🚀 Starting PostgreSQL database with Docker Compose..."

# Start the database
docker-compose up -d postgres

echo "⏳ Waiting for database to be ready..."
sleep 10

echo "📊 Starting pgAdmin..."
docker-compose up -d pgadmin

echo "🔧 Installing database dependencies..."
pip install sqlalchemy psycopg2-binary alembic

echo "🗄️ Running database migrations..."
alembic upgrade head

echo "✅ Database setup complete!"
echo ""
echo "📋 Database Information:"
echo "   Host: localhost"
echo "   Port: 5432"
echo "   Database: travel_planner"
echo "   Username: travel_user"
echo "   Password: travel_password"
echo ""
echo "🌐 pgAdmin: http://localhost:8080"
echo "   Email: admin@travelplanner.com"
echo "   Password: admin123"
echo ""
echo "🔗 Connection URL: postgresql://travel_user:travel_password@localhost:5432/travel_planner" 