from chatbot.core import Llama3Chatbot, ChatSession
from langsmith import Client
import os


os.environ["LANGCHAIN_TRACING_V2"] = "true"  # Enable tracing
os.environ["LANGCHAIN_PROJECT"] = "chatbot-aws-llama3-8b-instruct-v1"  # Project name in LangSmith UI
#os.environ["LANGSMITH_API_KEY"] ## should be in environment path
model_id = "meta.llama3-8b-instruct-v1:0"

def main():
    # Initialize
    bot = Llama3Chatbot(model_id)
    session = ChatSession(bot)
    
    # Chat loop
    print("Chat with Llama 3 (type 'quit' to exit)")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break
        
        response = session.send_message(user_input)
        print(f"AI: {response}")

if __name__ == "__main__":
    main()