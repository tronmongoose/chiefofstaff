# Personal AI Agent

A LangGraph-powered AI agent that can handle weather queries, todo lists, and general conversation.

## 🚀 Features

- **Weather Tool**: Get real-time weather information for any location
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

## 📁 Project Structure

```bash
my-langgraph-project/
│
├── main.py          # Main LangGraph agent code
├── tools.py         # Tool definitions (weather, todo)
├── state.py         # Shared AgentState type
├── nodes/           # Graph nodes
│   ├── planner.py   # Task planning and tool call generation
│   └── executor.py  # Tool execution and response generation
├── .env             # API keys (not committed)
└── requirements.txt # Python dependencies
```

## 🧠 How It Works

The agent uses a simple two-node graph:

1. **Planner Node**: 
   - Analyzes user input
   - Generates appropriate tool calls for weather/todo queries
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
   OPENWEATHER_API_KEY=your-key-here
   ```

3. **Run the agent:**
   ```bash
   python3 main.py
   ```

## 💬 Example Usage

```
You: What's the weather in San Diego?
AI: The weather in San Diego is 72°F with clear sky.

You: Show me my todo list
AI: Erik's todo list:
1) Build agent
2) Test LangGraph
3) Deploy system

You: How are you today?
AI: I'm just a computer program, but I'm here and ready to help you! How can I assist you today?
```

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

### Phase 3: Current State
- Clean, working implementation
- Direct tool call generation
- Natural conversation handling
- Stable execution flow

## ⚠️ Notes
- The agent uses GPT-4 for optimal performance
- Weather data comes from OpenWeather API
- Todo list is currently hardcoded (can be expanded to use a database)

## 📝 Version Control
- **Do NOT commit your `.env` file**
- Add to `.gitignore`:
  ```
  .env
  __pycache__/
  ```
