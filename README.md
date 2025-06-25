# Personal AI Agent

A LangGraph-powered AI agent that can handle weather queries, flight searches, travel recommendations, wallet management, and general conversation.

## 🛠️ Recent Troubleshooting & Dependency Updates

- **Coinbase CDP SDK Import Error:** Fixed `ImportError: cannot import name 'CdpClient' from 'cdp'` by uninstalling the incorrect `cdp` package and installing the correct `cdp-sdk` package (`cdp-sdk==1.15.0`).
- **NumPy/ChromaDB Compatibility:** Resolved `AttributeError: np.float_ was removed in the NumPy 2.0 release` by pinning NumPy to a compatible version. Later, installing `langchain_chroma` upgraded NumPy to 2.3.1, which is compatible with the latest ChromaDB.
- **ChromaDB Integration:** Added `langchain_chroma==0.2.4` to requirements for Python 3.13 compatibility.
- **Backend/Frontend Port Mismatch:** Fixed frontend connection errors by restarting the backend on port 8000 to match the frontend's expectations.
- **General:** Updated `requirements.txt` to reflect all dependency changes. Backend and wallet/payment features are now fully operational. Only minor warning: LangChain memory deprecation (not blocking).

## 🚀 Features

- **Weather Tool**: Get real-time weather information for any location
- **Flight Search**: Search for flights between airports with pricing and airline details
- **Airport Information**: Get detailed information about airports using IATA codes
- **Travel Recommendations**: Get activities and points of interest for popular cities
- **Wallet Management**: Check cryptocurrency balances from Coinbase CDP API
- **Todo List**: Access and display your todo list
- **General Conversation**: Natural language responses for non-tool queries
- **Memory System**: Maintains conversation history across sessions
- **Vector Retrieval**: RAG system with knowledge base integration
- **Simple Architecture**: Clean, maintainable code structure

## 🛠️ Tech Stack

| Component        | Version  | Purpose                |
|------------------|----------|------------------------|
| Python           | 3.11+    | Core language          |
| LangGraph        | 0.0.33+  | Agent state graph      |
| langchain-openai | 0.3.23+  | OpenAI LLM integration |
| openai           | 1.86.0+  | Direct OpenAI SDK      |
| python-dotenv    | 1.0.1+   | API key management     |
| amadeus          | 8.1.0+   | Flight & travel API    |
| chromadb         | 0.4.24+  | Vector database        |
| requests         | 2.31.0+  | HTTP requests          |

## 📁 Project Structure

```bash
my-langgraph-project/
│
├── main.py              # Main LangGraph agent code
├── agent_tools.py       # Tool definitions (weather, flights, travel, wallet)
├── wallet.py            # Coinbase CDP API integration
├── state.py             # Shared AgentState type
├── memory.py            # Conversation memory system
├── retrieval.py         # Vector store and RAG system
├── nodes/               # Graph nodes
│   ├── planner.py       # Task planning and tool call generation
│   └── executor.py      # Tool execution and response generation
├── tools/               # Tool modules
│   ├── __init__.py      # Package initialization
│   └── payment.py       # Wallet and payment tools
├── .env                 # API keys (not committed)
├── env_template.txt     # Environment variables template
├── test_tools.py        # Test script for all tools
├── knowledge.txt        # Knowledge base for RAG
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
   OPENAI_API_KEY=sk-...
   AMADEUS_API_KEY=your-amadeus-api-key
   AMADEUS_API_SECRET=your-amadeus-api-secret
   OPENWEATHER_API_KEY=your-openweather-key
   COINBASE_API_KEY=your-coinbase-api-key
   COINBASE_API_SECRET=your-coinbase-api-secret
   ```
   
   See `env_template.txt` for the complete template.

4. **Test the tools (optional):**
   ```bash
   python3 test_tools.py
   ```

5. **Run the agent:**
   ```bash
   python3 main.py
   ```

## 💬 Example Usage

```
You: What's the weather in San Francisco?
AI: The weather in San Francisco is 60.64°F with few clouds.

You: Search for flights from LAX to JFK on 2025-07-15
AI: Found 58 flights from LAX to JFK on 2025-07-15:
1. F9 - $107.85
2. B6 - $129.35
3. AS - $136.68
4. AS - $136.68
5. B6 - $137.95

You: Tell me about LAX airport
AI: Airport: LOS ANGELES INTL (LAX)
Location: LOS ANGELES, UNITED STATES OF AMERICA

You: What are some activities in Paris?
AI: Travel recommendations for Paris:
Popular attractions in Paris: Eiffel Tower, Louvre Museum, Notre-Dame Cathedral, 
Champs-Élysées, Arc de Triomphe, Seine River Cruise, Palace of Versailles

You: Show me my todo list
AI: Erik's todo list:
1) Build agent
2) Test LangGraph
3) Deploy system

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

### Wallet Tool Usage

The `check_wallet_balance` tool automatically routes queries containing:
- "wallet", "balance", "crypto", "bitcoin", "ethereum", "coinbase", "account"

Example queries that will trigger wallet balance checking:
- "Check my wallet balance"
- "What's my crypto balance?"
- "Show me my Coinbase account"
- "How much Bitcoin do I have?"
