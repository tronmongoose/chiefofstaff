import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from retrieval import create_vectorstore, query_knowledge

# Optional imports for memory, tools, and retrieval
try:
    from memory import create_memory
except ImportError:
    create_memory = None
try:
    from tools import get_weather, get_todo_list
except ImportError:
    get_weather = None
    get_todo_list = None

# Load API key from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the LLM
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-4")

# Initialize memory if available
memory = create_memory() if create_memory else None

# Initialize tools if available
TOOLS = []
if get_weather:
    TOOLS.append(get_weather)
if get_todo_list:
    TOOLS.append(get_todo_list)

# Initialize the vectorstore
vectorstore = create_vectorstore()

# Define our state type
class AgentState(TypedDict):
    messages: list[str]
    next: str

# Define our nodes
def agent_node(state: AgentState) -> AgentState:
    """Generate a response based on the last message and relevant knowledge."""
    last_message = state["messages"][-1]
    
    # Query relevant knowledge
    relevant_docs = query_knowledge(last_message, vectorstore)
    knowledge_context = "\n".join(doc.page_content for doc in relevant_docs)
    
    # Construct the prompt with context
    prompt = f"""You are an AI assistant with access to the following relevant information:

{knowledge_context}

User's message: {last_message}

Please provide a helpful response that incorporates the relevant information above when appropriate."""
    
    response = llm.invoke(prompt)
    return {
        "messages": state["messages"] + [response.content],
        "next": END
    }

# Create the graph
workflow = StateGraph(AgentState)

# Add the agent node
workflow.add_node("agent", agent_node)

# Set the entry point
workflow.set_entry_point("agent")

# Compile the graph
app = workflow.compile()

# Test the graph
if __name__ == "__main__":
    # Initialize the state
    initial_state = {
        "messages": ["I'm ready to build my AI agent!"],
        "next": "agent"
    }
    
    # Run the graph
    result = app.invoke(initial_state)
    print("\nFinal messages:")
    for msg in result["messages"]:
        print(f"- {msg}")