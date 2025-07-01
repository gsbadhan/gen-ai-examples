from langchain.memory import ConversationBufferMemory

# Replace with Redis or DB for prod
user_memory = {}


def get_user_memory(user_id:str):
    if user_id not in user_memory:
        user_memory[user_id] = ConversationBufferMemory(
            return_messages=True, memory_key="history"
        )
    return user_memory[user_id]
