# Tools/functions for agent to call
from langchain_core.tools import tool

@tool
def get_weather(location: str) -> str:
    """Returns a pretend weather report for a location"""
    return f"The weather in {location} is 72°F and sunny."

@tool
def get_todo_list(user: str) -> str:
    """Returns a pretend todo list for a user"""
    return f"{user}'s todo list: 1) Build AI agent. 2) Test LangGraph. 3) Celebrate progress."