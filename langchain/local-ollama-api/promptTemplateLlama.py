from langchain_ollama.llms import OllamaLLM
from langchain.prompts import PromptTemplate

prompt="""
what is best book of data structure in computer science ? and output should not more than 3.
"""

# Initialize OllamaLLM 
llm = OllamaLLM(model="llama3.1") 

# Use the models in your LangChain chains or agents
prompt = PromptTemplate.from_template(
    "Explain {concept} like I'm 5 years old"
)

chain = prompt | llm  # Combine prompt and LLM
response = chain.invoke({"concept": "black holes"})
print(response)

