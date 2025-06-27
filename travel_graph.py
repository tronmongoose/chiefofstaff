from langgraph.graph import StateGraph, END
from state import TravelAgentState
from nodes.travel_planner import (
    search_flights_node,
    search_hotels_node,
    get_activities_node,
    assemble_plan_node,
    budget_branch_node,
    wait_for_confirmation_node,
    process_payment_node,
    confirm_bookings_node,
    store_platform_fee_node,
    error_handler_node,
)

# Build the LangGraph for the autonomous travel planner
travel_graph = StateGraph(TravelAgentState)

# Add nodes
travel_graph.add_node("search_flights", search_flights_node)
travel_graph.add_node("search_hotels", search_hotels_node)
travel_graph.add_node("get_activities", get_activities_node)
travel_graph.add_node("assemble_plan", assemble_plan_node)
travel_graph.add_node("budget_branch", budget_branch_node)
travel_graph.add_node("wait_for_confirmation", wait_for_confirmation_node)
travel_graph.add_node("process_payment", process_payment_node)
travel_graph.add_node("confirm_bookings", confirm_bookings_node)
travel_graph.add_node("store_platform_fee", store_platform_fee_node)
travel_graph.add_node("error_handler", error_handler_node)

# Entry point
travel_graph.set_entry_point("search_flights")

# Define parallel execution after flights
def should_continue_to_parallel(state):
    """Determine if we should continue to parallel execution"""
    return "search_hotels" if state.get("flights") else "error_handler"

def should_continue_to_assemble(state):
    """Determine if we should continue to assemble plan"""
    return "assemble_plan" if (state.get("hotels") and state.get("activities")) else "error_handler"

# Add edges for parallel execution
travel_graph.add_conditional_edges(
    "search_flights",
    should_continue_to_parallel,
    {
        "search_hotels": "search_hotels",
        "error_handler": "error_handler"
    }
)

travel_graph.add_edge("search_hotels", "get_activities")
travel_graph.add_conditional_edges(
    "get_activities",
    should_continue_to_assemble,
    {
        "assemble_plan": "assemble_plan",
        "error_handler": "error_handler"
    }
)

# Budget check/branch
travel_graph.add_edge("assemble_plan", "budget_branch")
travel_graph.add_edge("budget_branch", "wait_for_confirmation")

# User confirmation
travel_graph.add_edge("wait_for_confirmation", "process_payment")
travel_graph.add_edge("process_payment", "confirm_bookings")
travel_graph.add_edge("confirm_bookings", "store_platform_fee")

# End states
travel_graph.add_edge("store_platform_fee", END)
travel_graph.add_edge("error_handler", END)

# Compile the graph
travel_app = travel_graph.compile() 