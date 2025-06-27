# Database Integration Setup

This document describes the PostgreSQL database integration for the Travel Planner backend.

## Overview

The system now uses PostgreSQL with SQLAlchemy ORM for persistent storage of travel plans, replacing the previous in-memory storage. This ensures data persistence across server restarts and provides better scalability.

## Database Schema

### Plans Table

```sql
CREATE TABLE plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_wallet VARCHAR(42) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    budget INTEGER NOT NULL,
    plan_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'generated' CHECK (status IN ('generated', 'confirmed', 'cancelled')),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Fields:**
- `id`: Unique identifier (UUID)
- `user_wallet`: User's wallet address (42 characters)
- `destination`: Travel destination
- `budget`: Budget in USD (integer)
- `plan_data`: Complete plan data as JSONB
- `created_at`: Creation timestamp
- `status`: Plan status (generated/confirmed/cancelled)
- `updated_at`: Last update timestamp (auto-updated)

**Indexes:**
- `idx_plans_user_wallet`: For fast user plan lookups
- `idx_plans_created_at`: For chronological sorting
- `idx_plans_status`: For status-based filtering

## Quick Start

### 1. Start Database

```bash
# Start PostgreSQL and pgAdmin
./start_database.sh
```

### 2. Start Backend with Database

```bash
# Start backend with database integration
./start_backend_with_db.sh
```

### 3. Verify Setup

```bash
# Check database connection
curl http://localhost:8000/health

# Test plan generation
curl -X POST http://localhost:8000/generate_plan \
  -H "Content-Type: application/json" \
  -d '{"destination": "Paris", "budget": 2000, "user_wallet": "0x1234567890123456789012345678901234567890"}'
```

## Database Management

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs postgres

# Stop services
docker-compose down

# Stop and remove volumes (WARNING: This deletes all data)
docker-compose down -v
```

### Using pgAdmin

1. Open http://localhost:8080
2. Login with:
   - Email: `admin@travelplanner.com`
   - Password: `admin123`
3. Add server:
   - Host: `postgres`
   - Port: `5432`
   - Database: `travel_planner`
   - Username: `travel_user`
   - Password: `travel_password`

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## API Changes

The API endpoints maintain the same contract but now use persistent storage:

### `/generate_plan` (POST)
- **Before**: Stored plan in memory
- **After**: Saves plan to database with status "generated"
- **Response**: Same structure, plan_id now from database UUID

### `/confirm_plan` (POST)
- **Before**: Updated in-memory plan status
- **After**: Updates database plan status to "confirmed"
- **Response**: Same structure

### `/get_user_plans/{user_wallet}` (GET)
- **Before**: Retrieved from in-memory user_plans mapping
- **After**: Queries database for all plans by user_wallet
- **Response**: Same structure, includes database timestamps

## Database Configuration

### Environment Variables

```bash
# Database connection (defaults shown)
DATABASE_URL=postgresql://travel_user:travel_password@localhost:5432/travel_planner
```

### Connection Pooling

The database uses SQLAlchemy connection pooling:
- **Pool Size**: 10 connections
- **Max Overflow**: 20 additional connections
- **Pool Recycle**: 1 hour
- **Pool Pre-ping**: Enabled for connection validation

## Data Persistence

### What's Stored

1. **Complete Plan Data**: All flight, hotel, activity details as JSONB
2. **User Associations**: Plans linked to wallet addresses
3. **Status Tracking**: Plan lifecycle (generated → confirmed → cancelled)
4. **Timestamps**: Creation and update times with timezone support

### Data Recovery

- **Automatic**: Data persists across server restarts
- **Backup**: Use PostgreSQL backup tools
- **Migration**: Alembic handles schema changes

## Performance Considerations

### Indexes
- User wallet lookups are indexed for fast retrieval
- Created_at is indexed for chronological sorting
- Status is indexed for filtering

### JSONB Benefits
- Efficient storage of complex plan data
- Queryable JSON fields
- Better performance than TEXT storage

### Connection Pooling
- Reuses database connections
- Reduces connection overhead
- Handles concurrent requests efficiently

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check if PostgreSQL is running
   docker-compose ps postgres
   
   # Check logs
   docker-compose logs postgres
   ```

2. **Migration Errors**
   ```bash
   # Reset migrations
   alembic downgrade base
   alembic upgrade head
   ```

3. **Permission Denied**
   ```bash
   # Check database permissions
   docker-compose exec postgres psql -U travel_user -d travel_planner
   ```

### Debugging

```bash
# Enable SQL logging
# Set echo=True in database.py engine creation

# Check database contents
docker-compose exec postgres psql -U travel_user -d travel_planner -c "SELECT * FROM plans;"

# Monitor connections
docker-compose exec postgres psql -U travel_user -d travel_planner -c "SELECT * FROM pg_stat_activity;"
```

## Security Considerations

1. **Connection Security**: Use SSL in production
2. **Password Management**: Use environment variables
3. **Access Control**: Limit database access
4. **Data Encryption**: Consider encrypting sensitive data

## Production Deployment

### Environment Setup
```bash
# Production database URL
DATABASE_URL=postgresql://user:password@host:port/database

# SSL configuration
DATABASE_SSL_MODE=require
```

### Backup Strategy
```bash
# Automated backups
pg_dump travel_planner > backup.sql

# Restore
psql travel_planner < backup.sql
```

### Monitoring
- Monitor connection pool usage
- Track query performance
- Set up database alerts
- Monitor disk space usage

## Migration from In-Memory Storage

The system automatically handles the transition:
1. New plans are saved to database
2. Existing in-memory data is not migrated
3. API responses maintain compatibility
4. Frontend requires no changes

## Future Enhancements

1. **User Authentication**: Add user accounts table
2. **Plan Sharing**: Add sharing permissions
3. **Analytics**: Add usage tracking
4. **Caching**: Add Redis for performance
5. **Sharding**: Scale across multiple databases 