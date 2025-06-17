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

    # For other queries, use the LLM to generate a response
    prompt = f"""
You are a helpful assistant. Please respond to the following user request:

User request: {user_goal}
"""
    response = llm_planner.invoke(prompt)
    state["response"] = response.content
    return state