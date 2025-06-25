from tools.payment import WALLET_TOOLS
from agent_tools import TOOLS as BASE_TOOLS
from langchain_core.messages import SystemMessage, HumanMessage, FunctionMessage
from langchain_openai import ChatOpenAI
from state import AgentState
from tools.ipfs import upload_to_ipfs
import time

TOOLS = BASE_TOOLS + WALLET_TOOLS
llm_executor = ChatOpenAI(model="gpt-4o").bind_tools(TOOLS)
tool_map = {tool.name: tool for tool in TOOLS}

def execute_next_task(state: AgentState) -> AgentState:
    print("[executor.py] Starting execution with state:", state)

    if "tool_calls" not in state or not state["tool_calls"]:
        print("[executor.py] No tool calls found in state")
        # Remove the current task from queue
        if "task_queue" in state and state["task_queue"]:
            state["task_queue"].pop(0)
        state['response'] = state.get('response', "All tasks completed.")
        return state

    tool_call = state["tool_calls"][0]  # We only handle one tool call for now
    print("[executor.py] Processing tool call:", tool_call)

    tool_name = tool_call['function']['name']
    tool_args = eval(tool_call['function']['arguments'])  # Safely replace this later

    print(f"[executor.py] Tool name: {tool_name}, Args: {tool_args}")

    if tool_name not in tool_map:
        state['response'] = f"Error: Unknown tool '{tool_name}'"
        # Remove the current task from queue
        if "task_queue" in state and state["task_queue"]:
            state["task_queue"].pop(0)
        return state

    try:
        # Special routing for upload_to_ipfs_tool
        if tool_name == "upload_to_ipfs_tool":
            print("[executor.py] Routing to upload_to_ipfs directly...")
            result = upload_to_ipfs(tool_args)
        # Automatically upload travel recommendations to IPFS
        elif tool_name == "get_travel_recommendations":
            tool = tool_map[tool_name]
            print(f"[executor.py] Invoking tool: {tool_name}")
            result = tool.invoke(tool_args)
            # Prepare payload for IPFS
            ipfs_payload = {
                "city": tool_args.get("city"),
                "user_input": state.get("input"),
                "recommendations": result,
                "timestamp": int(time.time())
            }
            try:
                ipfs_hash = upload_to_ipfs(ipfs_payload)
                print(f"[executor.py] Posted travel recommendations to IPFS: {ipfs_hash}")
                state["travel_ipfs_hash"] = ipfs_hash
            except Exception as e:
                print(f"[executor.py] Error posting travel recommendations to IPFS: {e}")
                ipfs_hash = None
            # Append IPFS info in Markdown format
            if ipfs_hash:
                result += f"\n\n---\n**🌐 This travel plan has been posted to IPFS:** [View on IPFS](https://gateway.pinata.cloud/ipfs/{ipfs_hash})\n\n`{ipfs_hash}`\n---"
        else:
            tool = tool_map[tool_name]
            print(f"[executor.py] Invoking tool: {tool_name}")
            result = tool.invoke(tool_args)
        print(f"[executor.py] Tool result: {result}")

        # Referral record logic
        if tool_name == "x402_payment_tool" and tool_args.get("referrer_wallet"):
            print(f"[executor.py] Processing referral payment with referrer: {tool_args['referrer_wallet']}")
            print(f"[executor.py] Payment result type: {type(result)}")
            print(f"[executor.py] Payment result: {result}")
            
            try:
                import json
                # Handle both string and dict results
                if isinstance(result, str):
                    try:
                        res_obj = json.loads(result.replace("'", '"'))
                    except:
                        res_obj = {"raw_result": result}
                else:
                    res_obj = result
                
                tx_id = None
                if isinstance(res_obj, dict):
                    # Try to extract tx_hash from various possible locations
                    if 'agent' in res_obj and isinstance(res_obj['agent'], dict):
                        tx_id = res_obj['agent'].get('tx_hash')
                    elif 'referrer' in res_obj and isinstance(res_obj['referrer'], dict):
                        tx_id = res_obj['referrer'].get('tx_hash')
                    else:
                        tx_id = res_obj.get('tx_hash')
                
                referral_record = {
                    "referrer_wallet": tool_args["referrer_wallet"],
                    "referee_wallet": tool_args.get("recipient_address"),
                    "trip_request_details": state.get("input"),
                    "payment_transaction_id": tx_id,
                    "timestamp": int(time.time())
                }
                print(f"[executor.py] Creating referral record: {referral_record}")
                ipfs_hash = upload_to_ipfs(referral_record)
                print(f"[executor.py] Posted referral record to IPFS: {ipfs_hash}")
                state["referral_ipfs_hash"] = ipfs_hash
            except Exception as e:
                print(f"[executor.py] Error posting referral record to IPFS: {e}")
                import traceback
                traceback.print_exc()

        function_msg = FunctionMessage(name=tool_name, content=result)

        # Build system prompt
        system_prompt = "You are a helpful assistant that uses tool results."
        if state.get("referral_ipfs_hash"):
            system_prompt += " The payment has been successfully split between the agent and the referring wallet as part of our decentralized referral system. A referral record has been posted to IPFS."
        response = llm_executor.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=state['input']),
            function_msg
        ])
        state['response'] = response.content
        # Remove the current task from queue
        if "task_queue" in state and state["task_queue"]:
            state["task_queue"].pop(0)
    except Exception as e:
        state['response'] = f"Error calling tool '{tool_name}': {str(e)}"
        # Remove the current task from queue even if there's an error
        if "task_queue" in state and state["task_queue"]:
            state["task_queue"].pop(0)

    return state