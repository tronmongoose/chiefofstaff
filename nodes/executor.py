from tools import TOOLS
from langchain_core.messages import SystemMessage, HumanMessage, FunctionMessage
from langchain_openai import ChatOpenAI
from state import AgentState

llm_executor = ChatOpenAI(model="gpt-4o").bind_tools(TOOLS)
tool_map = {tool.name: tool for tool in TOOLS}

def execute_next_task(state: AgentState) -> AgentState:
    print("Debug - Executor: Starting execution with state:", state)

    if "tool_calls" not in state or not state["tool_calls"]:
        print("Debug - Executor: No tool calls found in state")
        # Remove the current task from queue
        if "task_queue" in state and state["task_queue"]:
            state["task_queue"].pop(0)
        state['response'] = state.get('response', "All tasks completed.")
        return state

    tool_call = state["tool_calls"][0]  # We only handle one tool call for now
    print("Debug - Executor: Processing tool call:", tool_call)

    tool_name = tool_call['function']['name']
    tool_args = eval(tool_call['function']['arguments'])  # Safely replace this later

    print(f"Debug - Executor: Tool name: {tool_name}, Args: {tool_args}")

    if tool_name not in tool_map:
        state['response'] = f"Error: Unknown tool '{tool_name}'"
        # Remove the current task from queue
        if "task_queue" in state and state["task_queue"]:
            state["task_queue"].pop(0)
        return state

    try:
        tool = tool_map[tool_name]
        result = tool.invoke(tool_args)
        print(f"Debug - Executor: Tool result: {result}")

        function_msg = FunctionMessage(name=tool_name, content=result)

        response = llm_executor.invoke([
            SystemMessage(content="You are a helpful assistant that uses tool results."),
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