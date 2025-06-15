# Memory management
from langchain_community.memory import ConversationBufferMemory

def create_memory():
    """Create a conversation memory buffer."""
    return ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="output"
    )