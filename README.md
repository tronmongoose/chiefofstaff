# Project Status

**This project is complete and ready for hackathon demo with full Coinbase CDP integration.**

- All setup, troubleshooting, and launch instructions are included below.
- Both backend and frontend are fully integrated and tested with real wallet connections.
- Chroma database reset and dependency pinning are documented.
- Coinbase Developer Platform integration complete with real wallet addresses.
- Reputation system with demo data generation for consistent hackathon presentations.
- Thank you to all contributors and testers!

---

# Personal AI Agent

A LangGraph-powered AI travel booking agent with Coinbase CDP wallet integration, x402 payment system, and comprehensive reputation tracking for hackathon demonstration.

## 🛠️ Recent Troubleshooting & Dependency Updates

- **Coinbase CDP SDK Import Error:** Fixed `ImportError: cannot import name 'CdpClient' from 'cdp'` by uninstalling the incorrect `cdp` package and installing the correct `cdp-sdk` package (`cdp-sdk==1.15.0`).
- **NumPy/ChromaDB Compatibility:** Resolved `AttributeError: np.float_ was removed in the NumPy 2.0 release` by pinning NumPy to a compatible version. Later, installing `langchain_chroma` upgraded NumPy to 2.3.1, which is compatible with the latest ChromaDB.
- **ChromaDB Integration:** Added `langchain_chroma==0.2.4` to requirements for Python 3.13 compatibility.
- **Backend/Frontend Port Mismatch:** Fixed frontend connection errors by restarting the backend on port 8000 to match the frontend's expectations.
- **General:** Updated `requirements.txt` to reflect all dependency changes. Backend and wallet/payment features are now fully operational. Only minor warning: LangChain memory deprecation (not blocking).

## 🚀 Features

- **Coinbase CDP Wallet Integration**: Real wallet connections with Coinbase Developer Platform
- **x402 Payment System**: Crypto payments for travel bookings with USDC
- **Reputation System**: Comprehensive IPFS-based reputation tracking with demo data
- **Weather Tool**: Get real-time weather information for any location
- **Flight Search**: Search for flights between airports with pricing and airline details
- **Airport Information**: Get detailed information about airports using IATA codes
- **Travel Recommendations**: Get activities and points of interest for popular cities
- **Database Integration**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **Frontend**: Next.js with TypeScript, Tailwind CSS, and real wallet connectivity
- **Memory System**: Maintains conversation history across sessions
- **Vector Retrieval**: RAG system with knowledge base integration
- **Production Ready**: Docker containerization and deployment scripts

## 🛠️ Tech Stack

| Component        | Version  | Purpose                |
|------------------|----------|------------------------|
| Python           | 3.11+    | Core language          |
| FastAPI          | 0.104.0+ | Web framework          |
| LangGraph        | 0.0.33+  | Agent state graph      |
| PostgreSQL       | 15+      | Primary database       |
| SQLAlchemy       | 2.0+     | ORM                    |
| Alembic          | 1.13+    | Database migrations    |
| Next.js          | 14+      | Frontend framework     |
| TypeScript       | 5+       | Type safety            |
| Tailwind CSS     | 3+       | Styling framework      |
| Coinbase CDP     | 1.15.0   | Wallet integration     |
| Wagmi            | 2.12+    | Web3 React hooks       |
| Viem             | 2.21+    | Ethereum library       |
| OpenAI           | 1.86.0+  | AI/LLM integration     |
| Amadeus          | 8.1.0+   | Flight & travel API    |
| ChromaDB         | 0.4.24+  | Vector database        |
| Docker           | 24+      | Containerization       |

## 📁 Project Structure

```bash
my-langgraph-project/
│
├── backend.py           # FastAPI server with x402 middleware
├── main.py              # LangGraph agent code
├── agent_tools.py       # Tool definitions (weather, flights, travel, wallet)
├── wallet.py            # Coinbase CDP API integration
├── models.py            # SQLAlchemy database models
├── database.py          # Database connection and setup
├── db_service.py        # Database service layer
├── reputation_models.py # Reputation system data models
├── x402_middleware.py   # x402 payment middleware
├── pinata_service.py    # IPFS storage service
├── nodes/               # Graph nodes
│   ├── planner.py       # Task planning and tool call generation
│   └── executor.py      # Tool execution and response generation
├── tools/               # Tool modules
│   ├── __init__.py      # Package initialization
│   └── payment.py       # Wallet and payment tools
├── travel-frontend/     # Next.js frontend application
│   ├── src/
│   │   ├── app/         # Next.js App Router pages
│   │   ├── components/  # React components
│   │   ├── context/     # React context providers
│   │   └── providers/   # Wallet providers
│   ├── package.json     # Frontend dependencies
│   └── tailwind.config.js
├── alembic/             # Database migrations
├── docker-compose.yml   # PostgreSQL and pgAdmin setup
├── .env                 # API keys (not committed)
├── env_template.txt     # Environment variables template
├── test_tools.py        # Test script for all tools
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🧠 How It Works

The agent uses a sophisticated multi-component architecture:

1. **Planner Node**: 
   - Analyzes user input using pattern matching and LLM
   - Generates appropriate tool calls for specific queries
   - Handles flight searches, weather, travel recommendations, etc.
   - Falls back to general conversation for non-tool queries

2. **Executor Node**:
   - Executes tool calls with proper error handling
   - Generates natural language responses from tool results
   - Manages tool execution and response formatting

3. **Memory System**:
   - Maintains conversation history across sessions
   - Integrates with LangChain's memory components

4. **Retrieval System**:
   - Vector store for document retrieval
   - RAG capabilities for knowledge base queries

## 🚀 Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/tronmongoose/chiefofstaff.git
   cd chiefofstaff
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API keys:**
   Create a `.env` file with:
   ```
   # Core API Keys
   OPENAI_API_KEY=sk-...
   AMADEUS_CLIENT_ID=your-amadeus-client-id
   AMADEUS_CLIENT_SECRET=your-amadeus-client-secret
   OPENWEATHER_API_KEY=your-openweather-key
   
   # Coinbase CDP Integration
   CDP_API_KEY_ID=your-cdp-api-key-id
   CDP_API_KEY_SECRET=your-cdp-api-key-secret
   COINBASE_API_KEY=your-coinbase-api-key
   COINBASE_API_SECRET=your-coinbase-api-secret
   
   # Database Configuration
   DATABASE_URL=postgresql://travel_user:travel_password@localhost:5432/travel_planner
   
   # Payment Configuration
   TRAVEL_PAYMENT_WALLET_ADDRESS=your-wallet-address
   ```
   
   See `env_template.txt` for the complete template.

4. **Set up the database:**
   ```bash
   # Start PostgreSQL with Docker
   docker-compose up -d postgres
   
   # Run database migrations
   alembic upgrade head
   ```

5. **Start the backend:**
   ```bash
   # Use asyncio event loop for CDP compatibility
   uvicorn backend:app --reload --host 0.0.0.0 --port 8000 --loop asyncio
   ```

6. **Start the frontend:**
   ```bash
   cd travel-frontend
   npm install
   npm run dev
   ```

7. **Test the tools (optional):**
   ```bash
   python3 test_tools.py
   ```

## 💬 Example Usage

### Frontend Interface
1. **Connect Wallet**: Use Coinbase Wallet connection on the homepage
2. **Generate Travel Plan**: Enter destination and budget with connected wallet
3. **View Reputation**: Access reputation dashboard with wallet-based data
4. **Book Travel**: Complete bookings with crypto payments

### Backend API
```bash
# Generate travel plan
curl -X POST "http://localhost:8000/generate_plan" \
  -H "Content-Type: application/json" \
  -d '{"destination": "Paris", "budget": 2000, "user_wallet": "0x123...abc"}'

# Check reputation
curl "http://localhost:8000/api/reputation/0x123...abc"

# Get payment pricing
curl "http://localhost:8000/api/payments/pricing"
```

### Agent Tools
```
You: What's the weather in San Francisco?
AI: The weather in San Francisco is 60.64°F with few clouds.

You: Search for flights from LAX to JFK on 2025-07-15
AI: Found 58 flights from LAX to JFK on 2025-07-15:
1. F9 - $107.85
2. B6 - $129.35
3. AS - $136.68

You: Check my wallet balance
AI: Wallet Balances:
- Bitcoin Wallet (VAULT): 0.00123456 BTC
- Ethereum Wallet (VAULT): 0.5 ETH
- USDC Wallet (VAULT): 1000.00 USDC
```

## 🛫 Amadeus API Tools

The agent includes powerful travel tools powered by the Amadeus API:

- **Flight Search**: Search for flights with pricing and airline information
  - Supports IATA airport codes (LAX, JFK, LHR, etc.)
  - Returns pricing and airline details
  - Handles future dates for booking

- **Airport Info**: Get detailed information about airports worldwide
  - Provides airport names and locations
  - Supports all major international airports

- **Travel Recommendations**: Discover activities and attractions in cities
  - Covers popular destinations (Paris, London, New York, Tokyo, Rome)
  - Provides curated attraction lists

### Getting Amadeus API Credentials

1. Visit [Amadeus for Developers](https://developers.amadeus.com/)
2. Create a free account
3. Create a new application to get your API key and secret
4. Add them to your `.env` file

## 🧪 Testing

Run the comprehensive test suite to verify all tools are working:

```bash
python3 test_tools.py
```

This will test:
- ✅ Amadeus API credentials
- ✅ Flight search functionality
- ✅ Airport information retrieval
- ✅ Travel recommendations
- ✅ Weather tool
- ✅ Todo list tool

## 📝 Development Phases

### Phase 1: Basic Setup ✅
- Set up project structure
- Implement basic tools (weather, todo)
- Create initial graph structure

### Phase 2: Graph Refinement ✅
- Simplified graph to two nodes
- Improved tool call handling
- Fixed recursion issues
- Added proper error handling

### Phase 3: Travel Integration ✅
- Added Amadeus API integration
- Implemented flight search capabilities
- Added airport information tool
- Added travel recommendations tool
- Enhanced planner with pattern matching
- Added comprehensive testing

### Phase 4: Current State ✅
- All tools tested and working
- Robust error handling
- Clean codebase structure
- Comprehensive documentation
- Ready for production use

## 🔧 Available Tools

| Tool | Description | Example Query |
|------|-------------|---------------|
| `get_weather` | Real-time weather data | "What's the weather in Tokyo?" |
| `search_flights` | Flight search with pricing | "Search for flights from LAX to JFK on 2025-07-15" |
| `get_airport_info` | Airport details | "Tell me about LAX airport" |
| `get_travel_recommendations` | City attractions | "What are some activities in Paris?" |
| `get_todo_list` | Personal todo list | "Show me my todo list" |

## ⚠️ Notes
- The agent uses GPT-4 for optimal performance
- Weather data comes from OpenWeather API
- Flight and travel data comes from Amadeus API
- Todo list is currently hardcoded (can be expanded to use a database)
- Memory system maintains conversation context
- Vector store provides RAG capabilities

## 📝 Version Control
- **Do NOT commit your `.env` file**
- Add to `.gitignore`:
  ```
  .env
  __pycache__/
  chroma_db/
  ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `python3 test_tools.py`
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 💰 Wallet Management

The agent includes cryptocurrency wallet management powered by the Coinbase CDP API:

- **Balance Checking**: View all cryptocurrency account balances
  - Supports multiple account types (VAULT, TRADING, etc.)
  - Shows currency and value for each account
  - Handles API errors gracefully

### Getting Coinbase CDP API Credentials

1. Visit [Coinbase Developer Portal](https://developers.coinbase.com/)
2. Create a new application
3. Generate API credentials with appropriate permissions
4. Add them to your `.env` file

### Wallet Integration Features

**Frontend Wallet Connection:**
- Real Coinbase Wallet SDK integration
- Wagmi and Viem for Web3 functionality
- Automatic wallet address detection
- Connect/disconnect functionality

**Backend Wallet Tools:**
- CDP API integration for balance checking
- Wallet-based reputation tracking
- Payment processing capabilities
- IPFS reputation storage

**Supported Queries:**
- "Check my wallet balance"
- "What's my crypto balance?"
- "Show me my Coinbase account"
- "How much Bitcoin do I have?"

## Backend Setup

To run the backend server, always use the following command to ensure compatibility with CDP wallet operations and IPFS posting:

```bash
uvicorn backend:app --reload --host 0.0.0.0 --port 8000 --loop asyncio
```

This ensures the default asyncio event loop is used instead of uvloop, which is required for proper operation.

## Troubleshooting

**Chroma Database Errors:**
If you encounter `sqlite3.OperationalError` related to missing columns, delete your local Chroma database directory (usually `chroma_db/`) and restart the backend to rebuild the schema.

**Database Connection Issues:**
- Ensure PostgreSQL is running: `docker-compose up -d postgres`
- Check database URL in `.env` file
- Run migrations: `alembic upgrade head`

**Frontend Wallet Connection:**
- Ensure Coinbase Wallet extension is installed
- Check that wallet providers are properly configured
- Verify CDP API keys are set correctly

**x402 Payment Issues:**
- Verify wallet addresses are properly formatted
- Check payment wallet has sufficient USDC balance
- Ensure CDP API credentials are valid

## Full Local Setup & Troubleshooting Guide

### 1. Backend (FastAPI/Uvicorn)
- Always start the backend with the default asyncio event loop:
  ```bash
  uvicorn backend:app --reload --host 0.0.0.0 --port 8000 --loop asyncio
  ```
- Or use the provided script:
  ```bash
  ./start_backend.sh
  ```
  This script will:
  1. Stop any running Uvicorn processes
  2. Wait 2 seconds
  3. Start the backend with the correct event loop

### 2. Frontend (Streamlit)
- In a separate terminal, run:
  ```bash
  streamlit run streamlit_app.py
  ```
- If port 8501 is busy, terminate any running Streamlit processes:
  ```bash
  pkill -f streamlit
  streamlit run streamlit_app.py
  ```
- The app will be accessible at [http://localhost:8501](http://localhost:8501) and is configured to talk to the backend at [http://localhost:8000](http://localhost:8000).

### 3. Resetting the Chroma Database
- If you encounter `sqlite3.OperationalError` related to missing columns, delete your local Chroma database directory (usually `chroma_db/`) and restart the backend to rebuild the schema:
  ```bash
  rm -rf chroma_db
  ./start_backend.sh
  ```

### 4. General Notes
- Always use `--loop asyncio` for backend compatibility with CDP wallet and IPFS.
- No other changes are needed for the backend, Streamlit app, or IPFS logic.

# 🌟 x402 Travel Booking System

**The World's First Crypto-Payment Travel Booking Platform**

Experience the future of travel booking with instant, secure payments using the revolutionary x402 standard. No more credit cards, no more waiting - just seamless crypto payments.

[![Deploy to Production](https://img.shields.io/badge/Deploy-Production-green.svg)](./deploy.sh)
[![x402 Standard](https://img.shields.io/badge/x402-Standard-blue.svg)](https://x402.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 Revolutionary Features

- **⚡ Instant Crypto Payments** - Pay with USDC in seconds, not days
- **🔒 Blockchain Security** - Transparent, immutable payment records
- **🌍 Global Access** - No borders, no restrictions, just travel
- **🤖 AI-Powered Planning** - Intelligent travel recommendations
- **📱 Modern UI/UX** - Beautiful, responsive interface
- **🔧 Production Ready** - Enterprise-grade deployment

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx (443)   │───▶│  Frontend (3000) │    │  Backend (8000) │
│   SSL/TLS       │    │   Next.js       │    │   FastAPI       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   PostgreSQL    │    │     Redis       │
                       │   Database      │    │    Cache        │
                       └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for development)
- Python 3.11+ (for development)

### Local Development
```bash
# Clone the repository
git clone <your-repo>
cd my-langgraph-project

# Start the development environment
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Production Deployment
```bash
# Deploy to production
./deploy.sh

# Or deploy to specific cloud provider
./deploy.sh digitalocean  # DigitalOcean App Platform
./deploy.sh aws           # AWS ECS
./deploy.sh railway       # Railway
```

## 💳 x402 Payment Flow

Experience the revolutionary payment system:

1. **Plan Your Trip** - AI-powered travel planning (FREE)
2. **Search Flights** - 0.01 USDC per search
3. **Book Flights** - 0.10 USDC per booking
4. **Instant Confirmation** - Blockchain-verified

### Payment Example
```
Flight Search:    0.01 USDC
Flight Booking:   0.10 USDC
Hotel Booking:    0.10 USDC
Total Fees:       0.21 USDC
```

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework
- **LangGraph** - AI workflow orchestration
- **PostgreSQL** - Primary database
- **Redis** - Caching and sessions
- **Alembic** - Database migrations

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React Context** - State management

### Infrastructure
- **Docker** - Containerization
- **Nginx** - Reverse proxy & SSL
- **x402 Standard** - Crypto payments
- **Coinbase CDP** - Payment processing

## 📊 API Endpoints

### Core Travel Planning
- `POST /generate_plan` - Create AI travel plan
- `POST /confirm_plan` - Confirm and book plan
- `GET /get_user_plans/{wallet}` - Get user plans

### x402 Payment Endpoints
- `GET /api/payments/pricing` - Get payment pricing
- `POST /api/flights/book` - Book flight (requires payment)
- `GET /api/flights/search` - Search flights (requires payment)

### Health & Monitoring
- `GET /health` - Health check
- `GET /api/health` - API health status

## 🔧 Configuration

### Environment Variables
Copy `env.production.template` to `.env.production`:

```bash
# Database
DB_PASSWORD=your_secure_password
DATABASE_URL=postgresql://travel_user:${DB_PASSWORD}@postgres:5432/travel_planner

# APIs
OPENWEATHER_API_KEY=your_openweather_key
AMADEUS_CLIENT_ID=your_amadeus_client_id
AMADEUS_CLIENT_SECRET=your_amadeus_secret

# x402 Payments
TRAVEL_PAYMENT_WALLET_ADDRESS=your_wallet_address
COINBASE_API_KEY=your_coinbase_key
COINBASE_API_SECRET=your_coinbase_secret

# Frontend
NEXT_PUBLIC_API_URL=https://your-domain.com/api
NEXT_PUBLIC_APP_NAME=x402 Travel Planner
```

## 🗄️ Database Schema

### Plans Table
```sql
CREATE TABLE plans (
    id UUID PRIMARY KEY,
    user_wallet VARCHAR(42) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    budget INTEGER NOT NULL,
    plan_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'generated'
);
```

### Bookings Table
```sql
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    booking_id VARCHAR UNIQUE,
    plan_id UUID REFERENCES plans(id),
    flight_id VARCHAR,
    passenger_name VARCHAR,
    passenger_email VARCHAR,
    payment_method VARCHAR DEFAULT 'crypto',
    status VARCHAR DEFAULT 'pending_payment',
    payment_amount FLOAT,
    payment_currency VARCHAR DEFAULT 'USDC',
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 📈 Monitoring & Logging

### Structured Logging
- JSON-formatted logs for easy parsing
- Separate error and application logs
- Performance monitoring
- Payment event tracking

### Health Checks
- Application health: `/health`
- Database connectivity
- Redis connectivity
- Payment system status

### Metrics
- Request/response times
- Payment success rates
- Database query performance
- Error rates and types

## 🔒 Security

### Payment Security
- x402 standard compliance
- Blockchain verification
- Secure wallet integration
- Rate limiting

### Application Security
- HTTPS enforcement
- CORS configuration
- Input validation
- SQL injection prevention
- XSS protection

## 🚀 Deployment Options

### 1. DigitalOcean App Platform (Recommended)
- Simple deployment
- Built-in SSL
- Automatic scaling
- Managed databases

### 2. AWS ECS
- Enterprise-grade
- High availability
- Advanced monitoring
- Cost optimization

### 3. Railway
- Developer-friendly
- Quick setup
- Built-in CI/CD
- Automatic deployments

### 4. Local Production
- Full control
- Custom configuration
- Development testing
- Staging environment

## 🧪 Testing

### End-to-End Testing
```bash
# Run comprehensive user journey test
python test_user_journey.py
```

### API Testing
```bash
# Test API endpoints
python test_api_endpoints.py
```

### Payment Testing
```bash
# Test x402 payment flow
curl -X GET "http://localhost:8000/api/payments/pricing"
```

## 📚 Documentation

- [Deployment Guide](./DEPLOYMENT.md) - Complete deployment instructions
- [API Documentation](./API_DOCUMENTATION.md) - API reference
- [Database Setup](./DATABASE_SETUP.md) - Database configuration
- [x402 Standard](https://x402.org) - Payment protocol documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [./CLAUDE.md](./CLAUDE.md) - Development instructions
- **Deployment**: [./DEPLOYMENT.md](./DEPLOYMENT.md) - Production deployment guide
- **Phase 4 Completion**: [./PHASE_4_COMPLETION.md](./PHASE_4_COMPLETION.md) - Database integration details
- **Reputation System**: [./REPUTATION_SYSTEM_SUMMARY.md](./REPUTATION_SYSTEM_SUMMARY.md) - Reputation API documentation
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Email**: support@x402-travel.com

## 🌟 What's Next?

- [x] Coinbase CDP wallet integration
- [x] x402 payment system integration
- [x] Reputation system with IPFS storage
- [x] Next.js frontend with TypeScript
- [x] PostgreSQL database with migrations
- [x] Demo data generation for hackathon
- [ ] Multi-language support
- [ ] Mobile app development
- [ ] Advanced AI features
- [ ] More payment methods
- [ ] International expansion
- [ ] Partnership integrations

---

**🎉 Welcome to the future of travel booking!**

Experience seamless crypto payments, AI-powered planning, and global accessibility with the x402 Travel Booking System. This hackathon-ready project demonstrates the full potential of Coinbase Developer Platform integration with comprehensive reputation tracking and real wallet connectivity.

**🏆 Hackathon Ready Features:**
- Complete Coinbase CDP wallet integration
- Real-time reputation tracking with demo data
- x402 payment system for crypto bookings
- Production-ready Next.js frontend
- Comprehensive database schema with migrations
- Docker containerization for easy deployment
