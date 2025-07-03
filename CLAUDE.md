# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a AI travel planning agent with cryptocurrency wallet integration. It consists of:

- **Backend**: FastAPI server with LangGraph agent, PostgreSQL database, and vector store
- **Frontend**: Next.js app with TypeScript and Tailwind CSS
- **Agent**: Multi-tool AI assistant supporting weather, flights, travel recommendations, and crypto wallets
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **Containerization**: Docker Compose for local development

## Development Commands

### Backend Development
```bash
# Start backend only (requires manual database setup)
./start_backend.sh

# Start backend with automatic database setup
./start_backend_with_db.sh

# Start PostgreSQL database only
./start_database.sh

# Setup database locally (without Docker)
./setup_database_local.sh

# Run backend manually
uvicorn backend:app --reload --host 0.0.0.0 --port 8000 --loop asyncio

# Run standalone agent
python main.py

# Run Streamlit interface
streamlit run streamlit_app.py
```

### Frontend Development
```bash
cd travel-frontend
npm install
npm run dev       # Development server with Turbopack
npm run build     # Production build
npm run start     # Production server
npm run lint      # ESLint linting
```

### Database Operations
```bash
# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Migration description"

# Start PostgreSQL with Docker
docker-compose up -d postgres

# Start pgAdmin
docker-compose up -d pgadmin
```

### Testing
```bash
# Test all agent tools
python test_tools.py

# Run specific test files
python tests/test_endpoints.py
python tests/test_planner.py
python tests/demo_verification.py

# Manual testing
python final_demo_test.py
```

## Architecture

### Backend Components

**FastAPI Server** (`backend.py`)
- RESTful API with CORS middleware
- Endpoints for plan generation, wallet management, and IPFS operations
- Database integration with SQLAlchemy

**LangGraph Agent** (`main.py`)
- State machine with planner and executor nodes
- Memory system for conversation history
- Vector store for document retrieval

**Database Layer**
- PostgreSQL with SQLAlchemy ORM
- Alembic for migrations
- Models: `Plan` with JSONB storage for flexible plan data

**Agent Tools** (`agent_tools.py`)
- Weather API integration (OpenWeather)
- Flight search (Amadeus API)
- Airport information
- Travel recommendations
- Cryptocurrency wallet management (Coinbase CDP)
- IPFS operations

### Frontend Components

**Next.js App** (`travel-frontend/`)
- App Router with TypeScript
- Tailwind CSS for styling
- React Context for state management (`PlanContext`)
- Global components: Header, Loading Bar, Error Alert

**Key Pages**
- Home (`/`) - Main interface
- Dashboard (`/dashboard`) - Plan management
- Review (`/review`) - Plan review and confirmation

### Database Schema

**Plans Table**
- `id`: UUID primary key
- `user_wallet`: Ethereum wallet address (42 chars)
- `destination`: Travel destination
- `budget`: Budget in integer format
- `plan_data`: JSONB for flexible plan storage
- `status`: Enum ('generated', 'confirmed', 'cancelled')
- Timestamps: `created_at`, `updated_at`

## API Configuration

Required environment variables in `.env`:
```
OPENAI_API_KEY=sk-...
AMADEUS_API_KEY=your-amadeus-api-key
AMADEUS_API_SECRET=your-amadeus-api-secret
OPENWEATHER_API_KEY=your-openweather-key
COINBASE_API_KEY=your-coinbase-api-key
COINBASE_API_SECRET=your-coinbase-api-secret
DATABASE_URL=postgresql://travel_user:travel_password@localhost:5432/travel_planner
```

## Critical Implementation Details

### Event Loop Requirement
Always use `--loop asyncio` when starting the backend to ensure compatibility with CDP wallet operations and IPFS:
```bash
uvicorn backend:app --reload --host 0.0.0.0 --port 8000 --loop asyncio
```

### Database Connection
- Default PostgreSQL connection: `postgresql://travel_user:travel_password@localhost:5432/travel_planner`
- pgAdmin interface: `http://localhost:8080` (admin@travelplanner.com / admin123)
- Docker containers: `postgres` (port 5432), `pgadmin` (port 8080)

### Port Configuration
- Backend: 8000
- Frontend: 3000 (dev), 8501 (Streamlit)
- Database: 5432
- pgAdmin: 8080

## Development Patterns

### Agent Node Structure
The LangGraph agent uses a two-node architecture:
1. **Planner Node** (`nodes/planner.py`) - Analyzes input and generates tool calls
2. **Executor Node** (`nodes/executor.py`) - Executes tools and formats responses

### Tool Implementation
Tools are defined in `agent_tools.py` with specific patterns:
- Weather queries: "weather", "temperature", "forecast"
- Flight searches: "flights", "fly", "airport codes"
- Travel recommendations: "activities", "attractions", "things to do"
- Wallet operations: "wallet", "balance", "crypto", "bitcoin"

### Database Service Layer
Use `db_service.py` for database operations:
- `PlanService` class for plan CRUD operations
- Session management with `get_db()` dependency
- Proper error handling and validation

## Troubleshooting

### Common Issues
1. **ChromaDB Errors**: Delete `chroma_db/` directory and restart backend
2. **Port 8000 Busy**: Scripts automatically kill existing processes
3. **Database Connection**: Ensure PostgreSQL is running via Docker or locally
4. **Frontend API Errors**: Verify backend is running on port 8000

### Dependency Issues
- NumPy compatibility resolved with version pinning
- CDP SDK: Use `cdp-sdk==1.15.0`, not `cdp`
- ChromaDB: Use `langchain_chroma==0.2.4` for Python 3.13

## File Structure Context

```
├── backend.py              # FastAPI server
├── main.py                 # LangGraph agent
├── agent_tools.py          # Tool definitions
├── models.py               # SQLAlchemy models
├── database.py             # Database connection
├── db_service.py           # Database operations
├── wallet.py               # Coinbase CDP integration
├── travel_graph.py         # Specialized travel planner
├── nodes/                  # LangGraph nodes
├── tools/                  # Tool modules
├── tests/                  # Test files
├── travel-frontend/        # Next.js app
├── alembic/                # Database migrations
└── docker-compose.yml      # PostgreSQL setup
```

Key files for modifications:
- Add new tools: `agent_tools.py`, `tools/`
- Modify agent logic: `nodes/planner.py`, `nodes/executor.py`
- Database changes: `models.py` → create migration → run `alembic upgrade head`
- API endpoints: `backend.py`
- Frontend pages: `travel-frontend/src/app/`