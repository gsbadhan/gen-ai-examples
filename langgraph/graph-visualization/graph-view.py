from typing import TypedDict
from langgraph.graph import StateGraph, END


# Step 1: Define state schema
class State(TypedDict):
    question: str
    response: str

# Step 2: Define node logic
def router(state: State) -> str:
    return "research" if "who is" in state["question"].lower() else "answer"

def answer_agent(state: State) -> State:
    return {"question": state["question"], "response": f"Answering: {state['question']}"}

def research_agent(state: State) -> State:
    return {"question": state["question"], "response": f"Researching: {state['question']}"}

# Step 3: Build the graph
graph_builder = StateGraph(state_schema=State)
graph_builder.set_entry_point("router")
graph_builder.add_node("router", router)
graph_builder.add_node("answer", answer_agent)
graph_builder.add_node("research", research_agent)
graph_builder.add_edge("router", "answer")
graph_builder.add_edge("router", "research")
graph_builder.add_edge("answer", END)
graph_builder.add_edge("research", END)

# Step 4: Compile first!
compiled_graph = graph_builder.compile()

graph = compiled_graph.get_graph()

# get the Mermaid description
graph = compiled_graph.get_graph()
with open("chatbot_graph.png", "wb") as f:
    f.write(graph.draw_mermaid_png())

print("Graph image saved as chatbot_graph.png")