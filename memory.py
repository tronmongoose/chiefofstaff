# Memory management
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

def create_memory():
    return ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=False
    )

def save_context(memory, input_str: str, output_str: str):
    memory.add_message(HumanMessage(content=input_str))
    memory.add_message(AIMessage(content=output_str))

def load_memory_variables(memory):
    messages = memory.messages
    return {"chat_history": messages}