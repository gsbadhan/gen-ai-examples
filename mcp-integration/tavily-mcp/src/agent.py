import os
import chromadb
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
from dotenv import load_dotenv
from langsmith.run_helpers import traceable
import json

load_dotenv()

# Load keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("Set OPENAI_API_KEY")
if not TAVILY_API_KEY:
    raise RuntimeError("Set TAVILY_API_KEY")

# Initialize
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection("bank_rates")
emb = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=OPENAI_API_KEY)
client = OpenAI(api_key=OPENAI_API_KEY)

# Tavily MCP definition
tavily_tool = {
    "type": "mcp",
    "server_label": "tavily",
    "server_url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}",
    "require_approval": "never"
}


@traceable(name="RAG_call")
def query_rag(query: str, country: str, k: int = 1):
    """Query ChromaDB (internal bank data)."""
    q_emb = emb.embed_query(query)
    results = collection.query(
        query_embeddings=[q_emb],
        n_results=k,
        where_document= {"$contains": country},
        include=["documents", "metadatas"],
    )
    return [
        {"text": doc, "metadata": meta}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]


def format_rag_results(rag_docs):
    """Convert RAG docs into structured output."""
    data = {}
    for doc in rag_docs:
        meta = doc.get("metadata", {})
        country = meta.get("country")
        bank = meta.get("bank")
        fd_rate = meta.get("fd_rate")
        home_loan_rate = meta.get("home_loan")
        personal_loan_rate = meta.get("personal_loan")
        if country and bank and fd_rate:
            data.setdefault(country, []).append({
                "bank": bank, 
                "fd_rate": fd_rate,
                "home_loan_rate" : home_loan_rate,
                "personal_loan_rate" : personal_loan_rate
                })
        #print(f"rag_data {data}")
    return data

@traceable(name="Tavily_call")
def call_tavily(query: str, country: str):
    """Use Tavily MCP tool to fetch data."""
    system_prompt = """
            You are a financial data extraction assistant.
            Always return JSON only, in this exact format:
            {
            "bank": "Full Official Bank Name",
            "fd_rate": "% value or null",
            "home_loan_rate": "% value or null",
            "personal_loan_rate": "% value or null"
            }
            If rates are missing, set them to null. Do not guess.
            """
    user_prompt = f"""
                    {query}
                """
    print(f"tavily prompt {user_prompt}")
    response = client.responses.create(
        model="gpt-4.1",
        tools=[tavily_tool],
        input=[
                {"role" : "system", "content":system_prompt},
                {"role": "user", "content": user_prompt}
            ],
        max_output_tokens=300
    )

    #print(f" tavily response {response}")
    tavily_data = {}
    for output in response.output:
        # Case 1: LLM structured text (most useful)
        if output.type == "message":
            for content in getattr(output, "content", []):
                if getattr(content, "type", "") == "output_text":
                    text = getattr(content, "text", "").strip()
                    print(f" text tag {text}")
                    if text.startswith("["):  # Expect JSON array
                        try:
                            parsed = json.loads(text)
                            for entry in parsed:
                                country = entry.get("country", "").strip()
                                if not country:
                                    continue
                                tavily_data.setdefault(country, []).append({
                                    "bank": entry.get("bank", ""),
                                    "fd_rate": entry.get("fd_rate", ""),
                                    "home_loan_rate": entry.get("home_loan_rate", ""),
                                    "personal_loan_rate": entry.get("personal_loan_rate", "")
                                })
                        except Exception as e:
                            print("JSON parse error from Tavily LLM output:", e)

        # Case 2: Direct Tavily MCP search (raw results)
        elif output.type == "mcp_call" and output.server_label == "tavily":
            try:
                data = json.loads(getattr(output, "output", "{}"))
                for r in data.get("results", []):
                    print("Tavily URL:", r.get("url"))
                    print("Snippet:", r.get("content")[:200])  # optional
            except Exception as e:
                print("Error parsing raw Tavily search results:", e)
    print(f"tavily data {tavily_data}")                            
    return tavily_data


@traceable(name="LLM_call")
def call_llm(query: str, country: str):
    """Fallback: Ask LLM directly if both RAG and Tavily fail."""
    system_prompt = """
            You are a financial data extraction assistant.
            Always return JSON only, in this exact format:
            {
            "bank": "Full Official Bank Name",
            "fd_rate": "% value or null",
            "home_loan_rate": "% value or null",
            "personal_loan_rate": "% value or null"
            }
            If rates are missing, set them to null. Do not guess.
            """
    user_prompt = f"""
                    {query}
                """
    
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_output_tokens=300,
    )

    print(f"llm response {response.output_text.strip()}")
    return response.output_text.strip()


def format_final_output(rag_data, tavily_data, llm_text=None):
    """Merge results and format output."""
    final_text = "Here are the Fixed Deposit (FD) rates by country and bank:\n\n"

    combined = {**rag_data}
    for country, banks in tavily_data.items():
        combined.setdefault(country, []).extend(banks)

    if combined:
        for country, banks in combined.items():
            final_text += f"{country}:\n"
            for b in banks:
                final_text += f"  Bank {b['bank']} : FD rate {b['fd_rate']}, Personal load rate {b['personal_loan_rate']}, Home load rate {b['home_loan_rate']} \n"
            final_text += "\n"

    if not combined and llm_text:
        final_text += llm_text

    return final_text.strip()


@traceable(name="agent_call")
def run_agent(country: str):
    prompt = f"what are the FD, Home loans and Personal loans rates for country {country} ?"
    print(f"prompt: {prompt}")
    
    # Step 1: RAG
    rag_docs = query_rag(query=prompt, country=country, k=5)
    rag_data = format_rag_results(rag_docs)
    
    # Step 2: Tavily (if RAG insufficient)
    tavily_data = {}
    if not rag_data:
        print(f"No resposne from RAG, calling Tavily MCP...")
        tavily_data = call_tavily(prompt, country=country)
    else:
        print(f"Got response from RAG.")    

    # Step 3: LLM fallback (if Tavily also empty)
    llm_text = None
    if not rag_data and not tavily_data:
        print(f"No resposne from MCP, calling LLM directly...")
        llm_text = call_llm(prompt, country)

    # Final output
    final_answer = format_final_output(rag_data, tavily_data, llm_text)

    return {
        "answer": final_answer,
        "rag_docs": rag_docs,
        "tavily_data": tavily_data,
        "llm_fallback": llm_text,
    }
