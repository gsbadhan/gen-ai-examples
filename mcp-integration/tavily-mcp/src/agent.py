import os
import chromadb
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
from dotenv import load_dotenv
from langsmith.run_helpers import traceable

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("Set OPENAI_API_KEY")
if not TAVILY_API_KEY:
    raise RuntimeError("Set TAVILY_API_KEY")

# Chroma
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection("bank_rates")

# Embeddings
emb = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=OPENAI_API_KEY)

# OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

tavily_tool = {
        "type": "mcp",
        "server_label": "tavily",
        "server_url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}",
        "require_approval": "never"
    }

@traceable(name="RAG call")
def retrieve_rag(query: str, k: int = 3):
    q_emb = emb.embed_query(query)
    results = collection.query(query_embeddings=[q_emb], n_results=k, include=["documents", "metadatas"])
    return [{"text": doc, "metadata": meta} for doc, meta in zip(results["documents"][0], results["metadatas"][0])]


def build_prompt(rag_docs, query: str):
    system_msg = (
        "You are a financial assistant. Use internal bank data (RAG) and external Tavily search if needed.\n"
        "Prefer RAG data when available. Always cite sources clearly."
    )
    rag_text = "\n".join([f"[RAG] {d['text']}" for d in rag_docs])
    user_msg = f"User Query: {query}\n\nInternal Data:\n{rag_text}"
    return system_msg, user_msg


@traceable(name="agent_call")
def run_agent(query: str):
    rag_docs = retrieve_rag(query)
    system_msg, user_msg = build_prompt(rag_docs, query)

    response = client.responses.create(
    model="gpt-4.1",
    tools=[tavily_tool],
    input=[
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ],
    max_output_tokens=500
    )

    # for debugging purpose
    tools_used = get_sources(response=response)

    return {
        "answer": getattr(response, "output_text", str(response)),
        "rag_docs": rag_docs,
        "tools_used": tools_used,
        "raw": response
    }


def get_sources(response):
    sources = set()

    for output in response.output:
        # Detect Tavily usage
        if output.type == "mcp_call" and output.server_label == "tavily":
            sources.add("TAVILY")

        # Detect RAG usage from assistant message
        if output.type == "message":
            text = output.content[0].text
            if "Internal Bank Data" in text or "internal bank data" in text:
                sources.add("RAG")

    return sources

