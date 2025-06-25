from langchain_core.messages import SystemMessage, HumanMessage
from state import AgentState
from langchain_openai import ChatOpenAI

def llm_node(state: AgentState, llm) -> AgentState:
    print("[planner.py] LLM Node: Processing input:", state['input'])
    response = llm.invoke([
        SystemMessage(content="You're a helpful assistant that can call tools if needed. When asked about weather, always use the get_weather tool."),
        HumanMessage(content=state['input'])
    ])

    print("[planner.py] LLM Node: Response:", response)
    print("[planner.py] LLM Node: Additional kwargs:", response.additional_kwargs)

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
        print("[planner.py] LLM Node: No tool call, using content:", response.content)
        state["response"] = response.content
    return state

llm_planner = ChatOpenAI(model="gpt-4o")

def plan_tasks(state: AgentState) -> AgentState:
    user_goal = state['input']
    print(f"[planner.py] Planning for user input: {user_goal}")

    # IPFS pattern matching
    if "log to ipfs" in user_goal.lower() or "save to ipfs" in user_goal.lower():
        print("[planner.py] Routing to upload_to_ipfs_tool.")
        state["tool_calls"] = [{
            "function": {
                "name": "upload_to_ipfs_tool",
                "arguments": f'{{"content": "{user_goal}"}}'
            }
        }]
        return state

    # Payment pattern matching (support ENS and hex addresses)
    import re
    payment_patterns = [
        r'pay ([0-9.]+) (\w+) to (0x[a-fA-F0-9]{40}|[a-zA-Z0-9\-]+\.eth)',
        r'send ([0-9.]+) (\w+) to (0x[a-fA-F0-9]{40}|[a-zA-Z0-9\-]+\.eth)',
        r'transfer ([0-9.]+) (\w+) to (0x[a-fA-F0-9]{40}|[a-zA-Z0-9\-]+\.eth)',
        r'pay ([0-9.]+) (\w+) to address (0x[a-fA-F0-9]{40}|[a-zA-Z0-9\-]+\.eth)',
    ]
    for pat in payment_patterns:
        m = re.search(pat, user_goal, re.IGNORECASE)
        if m:
            amount = float(m.group(1))
            token_symbol = m.group(2).upper()
            recipient = m.group(3)
            print(f"[planner.py] Parsed payment: amount={amount}, token={token_symbol}, recipient={recipient}")
            print(f"[planner.py] Routing to x402_payment_tool: {amount} {token_symbol} to {recipient}")
            state["tool_calls"] = [{
                "function": {
                    "name": "x402_payment_tool",
                    "arguments": f'{{"recipient_address": "{recipient}", "amount": {amount}, "token_symbol": "{token_symbol}"}}'
                }
            }]
            return state

    # Wallet/balance pattern matching
    wallet_patterns = [
        "wallet balance", "check my balance", "check wallet", "my wallet", "crypto balance", "coinbase balance", "account balance"
    ]
    if any(pat in user_goal.lower() for pat in wallet_patterns) or any(word in user_goal.lower() for word in ["wallet", "balance", "crypto", "coinbase"]):
        print("[planner.py] Routing to check_wallet_balance tool.")
        state["tool_calls"] = [{
            "function": {
                "name": "check_wallet_balance",
                "arguments": "{}"
            }
        }]
        return state

    # For weather queries, directly create a tool call
    if "weather" in user_goal.lower():
        import re
        # Try different patterns to extract location
        location = None
        
        # Pattern 1: "weather in [location]"
        match = re.search(r'weather\s+in\s+([^?.,!]+)', user_goal, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
        
        # Pattern 2: "what's the weather in [location]"
        if not location:
            match = re.search(r"what'?s?\s+the\s+weather\s+in\s+([^?.,!]+)", user_goal, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
        
        # Pattern 3: "how's the weather in [location]"
        if not location:
            match = re.search(r"how'?s?\s+the\s+weather\s+in\s+([^?.,!]+)", user_goal, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
        
        # Pattern 4: "weather for [location]"
        if not location:
            match = re.search(r'weather\s+for\s+([^?.,!]+)', user_goal, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
        
        # Pattern 5: "temperature in [location]"
        if not location:
            match = re.search(r'temperature\s+in\s+([^?.,!]+)', user_goal, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
        
        # Pattern 6: "forecast for [location]"
        if not location:
            match = re.search(r'forecast\s+for\s+([^?.,!]+)', user_goal, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
        
        # If we still don't have a location, try to extract from the end of the sentence
        if not location:
            # Remove common weather-related words and extract the last meaningful word/phrase
            weather_words = ['weather', 'temperature', 'forecast', 'climate', 'what', 'how', 'is', 'the', 'in', 'for', 'of']
            words = user_goal.lower().split()
            filtered_words = [word for word in words if word not in weather_words and word not in ['?', '!', '.', ',']]
            if filtered_words:
                location = ' '.join(filtered_words[-2:])  # Take last 2 words as location
        
        if location:
            print(f"[planner.py] Routing to get_weather tool for location: {location}")
            state["tool_calls"] = [{
                "function": {
                    "name": "get_weather",
                    "arguments": f'{{"location":"{location}"}}'
                }
            }]
            return state
        else:
            print("[planner.py] Weather query detected but could not extract location")
            # Fall through to LLM

    # For todo queries, directly create a tool call
    if "todo" in user_goal.lower():
        print("[planner.py] Routing to get_todo_list tool.")
        state["tool_calls"] = [{
            "function": {
                "name": "get_todo_list",
                "arguments": "{}"
            }
        }]
        return state

    # For flight search queries, directly create a tool call
    if "flight" in user_goal.lower() and ("search" in user_goal.lower() or "from" in user_goal.lower() and "to" in user_goal.lower()):
        import re
        flight_pattern = re.search(r'from\s+([A-Z]{3})\s+to\s+([A-Z]{3})', user_goal.upper())
        if not flight_pattern:
            flight_pattern = re.search(r'([A-Z]{3})\s+to\s+([A-Z]{3})', user_goal.upper())
        date_match = re.search(r'\b\d{4}-\d{2}-\d{2}\b', user_goal)
        if flight_pattern and date_match:
            origin = flight_pattern.group(1)
            destination = flight_pattern.group(2)
            date = date_match.group()
            print("[planner.py] Routing to search_flights tool.")
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
            print("[planner.py] Routing to get_airport_info tool.")
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
        city = city.split()[0] if city else ""
        if city:
            print("[planner.py] Routing to get_travel_recommendations tool.")
            state["tool_calls"] = [{
                "function": {
                    "name": "get_travel_recommendations",
                    "arguments": f'{{"city":"{city}"}}'
                }
            }]
            return state

    # For other queries, use the LLM to generate a response
    print("[planner.py] No tool matched, using LLM fallback.")
    prompt = f"""
You are a helpful assistant. You have access to the following tools:
- check_wallet_balance: for wallet, balance, crypto, or Coinbase account queries
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