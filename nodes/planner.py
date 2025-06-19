from langchain_core.messages import SystemMessage, HumanMessage
from state import AgentState
from langchain_openai import ChatOpenAI

def llm_node(state: AgentState, llm) -> AgentState:
    print("Debug - LLM Node: Processing input:", state['input'])
    response = llm.invoke([
        SystemMessage(content="You're a helpful assistant that can call tools if needed. When asked about weather, always use the get_weather tool."),
        HumanMessage(content=state['input'])
    ])

    print("Debug - LLM Node: Response:", response)
    print("Debug - LLM Node: Additional kwargs:", response.additional_kwargs)

    if response.additional_kwargs.get("tool_calls"):
        # Normalize tool call format for executor
        normalized_tool_calls = []
        for call in response.additional_kwargs["tool_calls"]:
            if "function" in call:
                normalized_tool_calls.append({
                    "name": call["function"]["name"],
                    "args": eval(call["function"]["arguments"])
                })
            else:
                normalized_tool_calls.append(call)
        state["tool_calls"] = normalized_tool_calls
    else:
        print("Debug - LLM Node: No tool call, using content:", response.content)
        state["response"] = response.content
    return state

llm_planner = ChatOpenAI(model="gpt-4o")

def plan_tasks(state: AgentState) -> AgentState:
    user_goal = state['input']

    # For weather queries, directly create a tool call
    if "weather" in user_goal.lower():
        location = user_goal.split("in ")[-1].strip()
        state["tool_calls"] = [{
            "function": {
                "name": "get_weather",
                "arguments": f'{{"location":"{location}"}}'
            }
        }]
        return state

    # For todo queries, directly create a tool call
    if "todo" in user_goal.lower():
        state["tool_calls"] = [{
            "function": {
                "name": "get_todo_list",
                "arguments": "{}"
            }
        }]
        return state

    # For flight search queries, directly create a tool call
    if "flight" in user_goal.lower() and ("search" in user_goal.lower() or "from" in user_goal.lower() and "to" in user_goal.lower()):
        # Try to extract origin, destination, and date
        import re
        # Look for airport codes (3 letters) - be more specific about context
        # Look for patterns like "from LAX to JFK" or "LAX to JFK"
        flight_pattern = re.search(r'from\s+([A-Z]{3})\s+to\s+([A-Z]{3})', user_goal.upper())
        if not flight_pattern:
            flight_pattern = re.search(r'([A-Z]{3})\s+to\s+([A-Z]{3})', user_goal.upper())
        
        # Look for date pattern (YYYY-MM-DD or similar)
        date_match = re.search(r'\b\d{4}-\d{2}-\d{2}\b', user_goal)
        
        if flight_pattern and date_match:
            origin = flight_pattern.group(1)
            destination = flight_pattern.group(2)
            date = date_match.group()
            state["tool_calls"] = [{
                "function": {
                    "name": "search_flights",
                    "arguments": f'{{"origin":"{origin}","destination":"{destination}","departure_date":"{date}"}}'
                }
            }]
            return state

    # For airport info queries, directly create a tool call
    if "airport" in user_goal.lower() or any(word in user_goal.upper() for word in ["LAX", "JFK", "LHR", "CDG", "NRT", "SFO", "ORD", "ATL"]):
        import re
        airports = re.findall(r'\b[A-Z]{3}\b', user_goal.upper())
        if airports:
            airport_code = airports[0]
            state["tool_calls"] = [{
                "function": {
                    "name": "get_airport_info",
                    "arguments": f'{{"airport_code":"{airport_code}"}}'
                }
            }]
            return state

    # For travel recommendations queries, directly create a tool call
    if any(word in user_goal.lower() for word in ["activities", "attractions", "things to do", "recommendations"]) and "in " in user_goal.lower():
        city = user_goal.lower().split("in ")[-1].strip()
        # Remove common words that might be at the end
        city = city.split()[0] if city else ""
        if city:
            state["tool_calls"] = [{
                "function": {
                    "name": "get_travel_recommendations",
                    "arguments": f'{{"city":"{city}"}}'
                }
            }]
            return state

    # For other queries, use the LLM to generate a response
    prompt = f"""
You are a helpful assistant. You have access to the following tools:
- get_weather: for weather, forecast, temperature, or climate questions
- get_todo_list: for todo list queries
- search_flights: for flight searches between airports (use IATA codes like LAX, JFK)
- get_airport_info: for airport information using IATA codes
- get_travel_recommendations: for travel activities and attractions in cities

Please respond to the following user request:

User request: {user_goal}
"""
    response = llm_planner.invoke(prompt)
    state["response"] = response.content
    return state