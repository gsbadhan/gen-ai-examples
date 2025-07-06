import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def get_llm():
    return ChatOpenAI(temperature=0.7,
        model="gpt-4",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        )
