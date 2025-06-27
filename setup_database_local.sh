#!/bin/bash

echo "🗄️ Setting up PostgreSQL Database Locally"

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed. Please install PostgreSQL first."
    echo "   On macOS: brew install postgresql"
    echo "   On Ubuntu: sudo apt-get install postgresql postgresql-contrib"
    echo "   On Windows: Download from https://www.postgresql.org/download/"
    exit 1
fi

# Check if PostgreSQL service is running
if ! pg_isready -q; then
    echo "❌ PostgreSQL service is not running. Please start PostgreSQL first."
    echo "   On macOS: brew services start postgresql"
    echo "   On Ubuntu: sudo systemctl start postgresql"
    exit 1
fi

echo "✅ PostgreSQL is running"

# Create database and user
echo "🔧 Creating database and user..."

# Create user (ignore if already exists)
psql -d postgres -c "CREATE USER travel_user WITH PASSWORD 'travel_password';" 2>/dev/null || true

# Create database (ignore if already exists)
psql -d postgres -c "CREATE DATABASE travel_planner OWNER travel_user;" 2>/dev/null || true

# Grant privileges
psql -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE travel_planner TO travel_user;"

echo "✅ Database setup complete!"

# Install Python dependencies
echo "🔧 Installing Python dependencies..."
pip install sqlalchemy psycopg2-binary alembic

# Initialize Alembic
echo "🗄️ Initializing Alembic..."
alembic init alembic 2>/dev/null || true

# Create initial migration
echo "📝 Creating initial migration..."
alembic revision --autogenerate -m "Initial migration"

# Run migration
echo "🚀 Running migration..."
alembic upgrade head

echo ""
echo "✅ Database setup complete!"
echo ""
echo "📋 Database Information:"
echo "   Host: localhost"
echo "   Port: 5432"
echo "   Database: travel_planner"
echo "   Username: travel_user"
echo "   Password: travel_password"
echo ""
echo "🔗 Connection URL: postgresql://travel_user:travel_password@localhost:5432/travel_planner"
echo ""
echo "🚀 You can now start the backend with: ./start_backend_with_db.sh"

docker compose up -d
docker ps 