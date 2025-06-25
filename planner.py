from transaction_log import get_remaining_cap, COSTS, log_transaction
# ... existing imports ...

def plan_tasks(state: AgentState) -> AgentState:
    user_goal = state['input']
    print(f"[planner.py] Planning for user input: {user_goal}")

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
            cost = COSTS.get('payment', 0.10)
            if get_remaining_cap() < cost:
                state['response'] = f"Spend cap exceeded. Cannot process payment. Remaining cap: ${get_remaining_cap():.2f}"
                return state
            print(f"[planner.py] Parsed payment: amount={amount}, token={token_symbol}, recipient={recipient}")
            print(f"[planner.py] Routing to x402_payment_tool: {amount} {token_symbol} to {recipient}")
            log_transaction('payment', cost, {'amount': amount, 'token': token_symbol, 'recipient': recipient})
            tool_args = {
                "recipient_address": recipient,
                "amount": amount,
                "token_symbol": token_symbol
            }
            if 'referrer_wallet' in state and state['referrer_wallet']:
                tool_args["referrer_wallet"] = state["referrer_wallet"]
            state["tool_calls"] = [{
                "function": {
                    "name": "x402_payment_tool",
                    "arguments": str(tool_args)
                }
            }]
            return state

    # Wallet/balance pattern matching
    wallet_patterns = [
        "wallet balance", "check my balance", "check wallet", "my wallet", "crypto balance", "coinbase balance", "account balance"
    ]
    if any(pat in user_goal.lower() for pat in wallet_patterns) or any(word in user_goal.lower() for word in ["wallet", "balance", "crypto", "coinbase"]):
        cost = COSTS.get('weather', 0.01)
        if get_remaining_cap() < cost:
            state['response'] = f"Spend cap exceeded. Cannot check wallet balance. Remaining cap: ${get_remaining_cap():.2f}"
            return state
        print("[planner.py] Routing to check_wallet_balance tool.")
        log_transaction('weather', cost, {'query': user_goal})
        state["tool_calls"] = [{
            "function": {
                "name": "check_wallet_balance",
                "arguments": "{}"
            }
        }]
        return state

    # For weather queries, directly create a tool call
    if "weather" in user_goal.lower():
        location = user_goal.split("in ")[-1].strip()
        cost = COSTS.get('weather', 0.01)
        if get_remaining_cap() < cost:
            state['response'] = f"Spend cap exceeded. Cannot check weather. Remaining cap: ${get_remaining_cap():.2f}"
            return state
        print("[planner.py] Routing to get_weather tool.")
        log_transaction('weather', cost, {'location': location})
        state["tool_calls"] = [{
            "function": {
                "name": "get_weather",
                "arguments": f'{{"location":"{location}"}}'
            }
        }]
        return state

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
            cost = COSTS.get('travel', 0.05)
            if get_remaining_cap() < cost:
                state['response'] = f"Spend cap exceeded. Cannot search flights. Remaining cap: ${get_remaining_cap():.2f}"
                return state
            print("[planner.py] Routing to search_flights tool.")
            log_transaction('travel', cost, {'origin': origin, 'destination': destination, 'date': date})
            state["tool_calls"] = [{
                "function": {
                    "name": "search_flights",
                    "arguments": f'{{"origin":"{origin}","destination":"{destination}","departure_date":"{date}"}}'
                }
            }]
            return state

    # For referral queries, directly create a tool call
    referral_patterns = [
        "referral", "referrals", "referral records", "show me referrals", "get referral"
    ]
    if any(pat in user_goal.lower() for pat in referral_patterns) and any(word in user_goal for word in ["0x", ".eth"]):
        print("[planner.py] Routing to retrieve_referrals_by_wallet_tool.")
        # Extract wallet address from the query
        import re
        wallet_match = re.search(r'(0x[a-fA-F0-9]{40}|[a-zA-Z0-9\-]+\.eth)', user_goal)
        if wallet_match:
            wallet_address = wallet_match.group(1)
            state["tool_calls"] = [{
                "function": {
                    "name": "retrieve_referrals_by_wallet_tool",
                    "arguments": f'{{"wallet_address": "{wallet_address}"}}'
                }
            }]
            return state

    # ... rest of planner.py unchanged ... 