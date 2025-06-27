# Shared agent state class
from typing import TypedDict, Optional, List, Any
from langgraph.checkpoint.memory import MemorySaver

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

class TravelAgentState(TypedDict, total=False):
    """
    State for the autonomous travel planner agent.
    """
    destination: str
    budget: float
    flights: Optional[List[dict]]
    hotels: Optional[List[dict]]
    activities: Optional[List[str]]
    plan: Optional[dict]
    total_estimated_cost: float
    platform_fee: float
    payment_status: str
    booking_status: Optional[dict]
    user_wallet: str
    error: str
    session_id: str