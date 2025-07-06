from langchain_community.chat_message_histories import ChatMessageHistory

# Replace with Redis or DB for prod
user_memory_store = {}

def get_user_memory(session_id: str) -> ChatMessageHistory:
    if session_id not in user_memory_store:
        user_memory_store[session_id] = ChatMessageHistory()
    return user_memory_store[session_id]
