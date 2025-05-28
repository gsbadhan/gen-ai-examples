from langchain_aws import BedrockLLM
from langchain.prompts import PromptTemplate
import os
from langsmith import Client


os.environ["LANGCHAIN_TRACING"] = "true"  # Enable tracing
os.environ["LANGCHAIN_PROJECT"] = "llm-llama3-8b-instruct-v1-traces"  # Project name in LangSmith UI
#os.environ["LANGSMITH_API_KEY"] ## should be in environment path

llm = BedrockLLM(
    model_id="meta.llama3-8b-instruct-v1:0",  
    region_name="ap-south-1",                  
    model_kwargs={
        "temperature": 0.5,    
        "max_gen_len": 256   
    })


prompt = PromptTemplate.from_template(
    "Explain {concept} like I'm 5 years old"
)

chain = prompt | llm  # Combine prompt and LLM
response = chain.invoke({"concept": "black holes"})
print(response)

### check llm traces on https://smith.langchain.com/ 

