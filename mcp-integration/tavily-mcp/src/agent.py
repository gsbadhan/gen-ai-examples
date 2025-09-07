import os
import chromadb
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
from dotenv import load_dotenv
from langsmith.run_helpers import traceable

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


@traceable(name="RAG call")
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
        if country and bank and fd_rate:
            data.setdefault(country, []).append({"bank": bank, "fd_rate": fd_rate})
    return data


def call_tavily(query: str):
    """Use Tavily MCP tool to fetch data."""
    response = client.responses.create(
        model="gpt-4.1",
        tools=[tavily_tool],
        input=[{"role": "user", "content": query}],
        max_output_tokens=800,
    )

    tavily_data = {}
    for output in response.output:
        if output.type == "mcp_call" and output.server_label == "tavily":
            text = getattr(output, "output_text", "")
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                # Example: "China ICBC: 1.8%"
                if ":" in line:
                    parts = line.split(":")
                    left, right = parts[0].strip(), parts[1].strip()
                    tokens = left.split()
                    if len(tokens) >= 2:
                        country, bank = tokens[0], " ".join(tokens[1:])
                        tavily_data.setdefault(country, []).append(
                            {"bank": bank, "fd_rate": right}
                        )
    return tavily_data


def call_llm(query: str):
    """Fallback: Ask LLM directly if both RAG and Tavily fail."""
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": "Answer clearly with country-wise, bank-wise FD rates if available."},
            {"role": "user", "content": query},
        ],
        max_output_tokens=600,
    )
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
                final_text += f"  {b['bank']}: {b['fd_rate']}\n"
            final_text += "\n"

    if not combined and llm_text:
        final_text += llm_text

    return final_text.strip()


@traceable(name="agent_call")
def run_agent(country: str):
    prompt = f"what are the FD, Home loans and Personal loans rates for country {country} ?"
    print(f"prompt: {prompt}")
    
    # Step 1: RAG
    rag_docs = query_rag(query=prompt, country=country, k=1)
    rag_data = format_rag_results(rag_docs)
    
    # Step 2: Tavily (if RAG insufficient)
    tavily_data = {}
    if not rag_data:
        print(f"No resposne from RAG, calling Tavily MCP...")
        tavily_data = call_tavily(prompt)

    # Step 3: LLM fallback (if Tavily also empty)
    llm_text = None
    if not rag_data and not tavily_data:
        print(f"No resposne from MCP, calling LLM directly...")
        llm_text = call_llm(prompt)

    # Final output
    final_answer = format_final_output(rag_data, tavily_data, llm_text)

    return {
        "answer": final_answer,
        "rag_docs": rag_docs,
        "tavily_data": tavily_data,
        "llm_fallback": llm_text,
    }
