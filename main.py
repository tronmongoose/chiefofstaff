import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from state import AgentState
from memory import create_memory
from nodes.planner import plan_tasks
from nodes.executor import execute_next_task

# Load env vars
load_dotenv()

# Initialize components
memory = create_memory()

# -------- LangGraph Nodes --------

def memory_node(state: AgentState) -> AgentState:
    chat_history = memory.load_memory_variables({}).get("chat_history", [])
    state["chat_history"] = chat_history
    return state

# -------- Build LangGraph --------

graph = StateGraph(AgentState)
graph.add_node("planner", plan_tasks)
graph.add_node("executor", execute_next_task)

graph.set_entry_point("planner")
graph.add_edge("planner", "executor")

app = graph.compile()

# -------- Chat Loop --------

if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        output_state = app.invoke(input={"input": user_input})
        print("AI:", output_state.get('response', "Done."))