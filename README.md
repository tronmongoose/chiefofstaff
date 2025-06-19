# Personal AI Agent

A LangGraph-powered AI agent that can handle weather queries, flight searches, travel recommendations, and general conversation.

## 🚀 Features

- **Weather Tool**: Get real-time weather information for any location
- **Flight Search**: Search for flights between airports with pricing
- **Airport Information**: Get details about airports using IATA codes
- **Travel Recommendations**: Get activities and points of interest for cities
- **Todo List**: Access and display your todo list
- **General Conversation**: Natural language responses for non-tool queries
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

## 📁 Project Structure

```bash
my-langgraph-project/
│
├── main.py          # Main LangGraph agent code
├── tools.py         # Tool definitions (weather, flights, travel)
├── state.py         # Shared AgentState type
├── nodes/           # Graph nodes
│   ├── planner.py   # Task planning and tool call generation
│   └── executor.py  # Tool execution and response generation
├── .env             # API keys (not committed)
├── env_template.txt # Environment variables template
└── requirements.txt # Python dependencies
```

## 🧠 How It Works

The agent uses a simple two-node graph:

1. **Planner Node**: 
   - Analyzes user input
   - Generates appropriate tool calls for weather/flight/travel queries
   - Handles general conversation

2. **Executor Node**:
   - Executes tool calls
   - Generates natural language responses
   - Manages tool results

## 🚀 Getting Started

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your API keys:**
   Create a `.env` file with:
   ```
   OPENAI_API_KEY=sk-...
   AMADEUS_API_KEY=your-amadeus-api-key
   AMADEUS_API_SECRET=your-amadeus-api-secret
   OPENWEATHER_API_KEY=your-openweather-key
   ```
   
   See `env_template.txt` for the complete template.

3. **Run the agent:**
   ```bash
   python3 main.py
   ```

## 💬 Example Usage

```
You: What's the weather in San Diego?
AI: The weather in San Diego is 72°F with clear sky.

You: Search for flights from LAX to JFK on 2024-03-15
AI: Found 15 flights from LAX to JFK on 2024-03-15:
1. AA - $245.50
2. DL - $267.80
3. UA - $289.90

You: Tell me about JFK airport
AI: Airport: John F. Kennedy International Airport (JFK)
Location: New York, United States

You: What are some activities in Paris?
AI: Travel recommendations for Paris:
1. Eiffel Tower Skip-the-Line Tour - $45.00
2. Louvre Museum Guided Tour - $65.00
3. Seine River Cruise - $25.00

You: Show me my todo list
AI: Erik's todo list:
1) Build agent
2) Test LangGraph
3) Deploy system
```

## 🛫 Amadeus API Tools

The agent now includes powerful travel tools powered by the Amadeus API:

- **Flight Search**: Search for flights with pricing and airline information
- **Airport Info**: Get detailed information about airports worldwide
- **Travel Recommendations**: Discover activities and attractions in cities

### Getting Amadeus API Credentials

1. Visit [Amadeus for Developers](https://developers.amadeus.com/)
2. Create a free account
3. Create a new application to get your API key and secret
4. Add them to your `.env` file

## 📝 Development Phases

### Phase 1: Basic Setup
- Set up project structure
- Implement basic tools (weather, todo)
- Create initial graph structure

### Phase 2: Graph Refinement
- Simplified graph to two nodes
- Improved tool call handling
- Fixed recursion issues
- Added proper error handling

### Phase 3: Travel Integration
- Added Amadeus API integration
- Implemented flight search capabilities
- Added airport information tool
- Added travel recommendations tool

## ⚠️ Notes
- The agent uses GPT-4 for optimal performance
- Weather data comes from OpenWeather API
- Flight and travel data comes from Amadeus API
- Todo list is currently hardcoded (can be expanded to use a database)

## 📝 Version Control
- **Do NOT commit your `.env` file**
- Add to `.gitignore`:
  ```
  .env
  __pycache__/
  ```
