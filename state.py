# Shared agent state class
from typing import TypedDict, List

class AgentState(TypedDict):
    input: str
    chat_history: List[str]
    retrieved_docs: str
    response: str