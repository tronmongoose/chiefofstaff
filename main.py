import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from state import AgentState
from memory import create_memory
from tools import tools
from retrieval import create_vectorstore
from langchain_core.runnables import RunnableLambda

# Load keys
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize components
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-4")
memory = create_memory()
vectorstore = create_vectorstore()

# ---- LangGraph Nodes ----

# 1️⃣ Memory Node
def memory_node(state: AgentState) -> AgentState:
    chat_history = memory.load_memory_variables({}).get("chat_history", [])
    state["chat_history"] = chat_history
    return state

# 2️⃣ Retrieval Node
def retrieval_node(state: AgentState) -> AgentState:
    retriever = vectorstore.as_retriever()
    docs = retriever.get_relevant_documents(state['input'])
    retrieved_text = "\n".join([doc.page_content for doc in docs])
    state['retrieved_docs'] = retrieved_text
    return state

# 3️⃣ Reasoning Node (LLM core)
def reasoning_node(state: AgentState) -> AgentState:
    # Format tools for the prompt
    tools_str = "\n".join([f"- {tool.name}: {tool.description}" for tool in tools])
    
    input_prompt = (
        f"""You are a helpful AI assistant with access to the following tools:

{tools_str}

User's message: {state['input']}

Chat history:
{state.get('chat_history', '')}

Relevant knowledge from the knowledge base:
{state.get('retrieved_docs', '')}

Please provide a helpful response. If the user's question can be answered using the tools above, use them appropriately."""
    )
    response = llm.invoke(input_prompt)
    state['response'] = response.content
    memory.save_context({"input": state['input']}, {"output": response.content})
    return state

# ---- Build LangGraph ----

graph = StateGraph(AgentState)

graph.add_node("memory", memory_node)
graph.add_node("retrieval", retrieval_node)
graph.add_node("reasoning", reasoning_node)

graph.set_entry_point("memory")
graph.add_edge("memory", "retrieval")
graph.add_edge("retrieval", "reasoning")

app = graph.compile()

# ---- Infinite Chat Loop ----

if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        output = app.invoke({"input": user_input})
        print("AI:", output['response'])