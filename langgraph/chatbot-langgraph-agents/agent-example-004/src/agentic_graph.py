from langchain_tavily import TavilySearch
from langchain_chroma import Chroma
from langchain_openai import OpenAI, OpenAIEmbeddings
from langgraph.graph import StateGraph
from typing import TypedDict
from langgraph.graph import StateGraph

class GraphState(TypedDict):
    input: str
    plan: str
    docs: list
    gaps: str
    solution: str
    code: str



# LLM setup (choose one)
llm = OpenAI(temperature=0.3)  # Or use OllamaLLM(model="llama3")

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma(persist_directory="chroma_index", embedding_function=embedding_model)
retriever = vectorstore.as_retriever()
search_tool = TavilySearch()


def plan_node(state):
    print(f"in plan_node got topic: {state['input']}")
    topic = state.get("input")
    if not topic or not isinstance(topic, str):
        raise ValueError("Invalid 'input' for plan_node: must be a non-empty string.")
    
    response = llm.invoke(f"Given the research topic '{topic}', outline research steps.")
    return {"input":topic, "plan": response}

def retrieve_node(state):
    print(f"in retrieve_node got input: {state['input']}")
    topic = state.get("input")
    if not topic or not isinstance(topic, str):
        raise ValueError("Invalid 'input' for retrieval: must be a non-empty string.")

    # Proceed with retrieval
    results = retriever.invoke(topic)
    return {"input":topic, "docs": results}


def fallback_node(state):
    print(f"in fallback_node got input: {state['input']}")
    topic = state.get("input")
    result = search_tool.invoke({"query": topic})
    #print(f"fallback_node tavily resuls: {result}")
    return {"input":topic, "docs": result}

def gap_node(state):
    print(f"in gap_node got docs: {state['docs']}")
    docs = state.get("docs", [])
    print(f"docs: {docs}")
    if isinstance(docs, dict):
        docs = list(docs.values())
    if not isinstance(docs, list):
        docs = [docs]
    content = str(docs)
    response = llm.invoke(f"Identify research gaps from these works:\n{content}")
    #print(f"in gap_node gaps: {response}")
    return {"gaps": response}

def solution_node(state):
    print(f"in solution_node got gaps: {state['gaps']}")
    gaps = state.get("gaps")
    response = llm.invoke(f"Propose a solution for gaps:\n{gaps}")
    #print(f"in solution_node solution: {response}")
    return {"solution": response}

def code_node(state):
    print(f"in code_node got solution: {state['solution']}")
    solution = state.get("solution")
    response = llm.invoke(f"Write sample JAVA code for solution:\n{solution}")
    print(f"in code_node code: {response}")
    return {"code": response}

def final_node(state):
    #print(f"in final_node got input: {state}")
    return {
        "output": {
            "Plan": state.get("plan"),
            "Gaps": state.get("gaps"),
            "Solution": state.get("solution"),
            "Code": state.get("code"),
        }
    }

# LangGraph definition
def build_agent_graph():
    workflow = StateGraph(GraphState)
    workflow.add_node("Plan", plan_node)
    workflow.add_node("Retrieve", retrieve_node)
    workflow.add_node("Fallback", fallback_node)
    workflow.add_node("GapAnalysis", gap_node)
    workflow.add_node("Solution", solution_node)
    workflow.add_node("CodeGen", code_node)
    workflow.add_node("Final", final_node)

    workflow.set_entry_point("Plan")
    workflow.add_edge("Plan", "Retrieve")
    workflow.add_conditional_edges("Retrieve", lambda state: bool(state.get("docs")), {
        True: "GapAnalysis",
        False: "Fallback"
    })
    workflow.add_edge("Fallback", "GapAnalysis")
    workflow.add_edge("GapAnalysis", "Solution")
    workflow.add_edge("Solution", "CodeGen")
    workflow.add_edge("CodeGen", "Final")
    workflow.set_finish_point("Final")

    return workflow.compile()


def show_graph(compiled_graph):
    graph = compiled_graph.get_graph()
    with open("agent_activity_graph.png", "wb") as f:
        f.write(graph.draw_mermaid_png())
    print("Graph image saved as agent_activity_graph.png")

