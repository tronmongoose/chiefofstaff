# Shared agent state class
from typing import TypedDict, Optional, List, Any

class AgentState(TypedDict, total=False):
    input: str
    chat_history: List[str]
    retrieved_docs: Optional[str]
    tool_calls: Optional[List[Any]]
    function_result: Optional[str]
    response: str
    task_queue: Optional[List[str]]
    current_task: Optional[str]
    task_result: Optional[str]