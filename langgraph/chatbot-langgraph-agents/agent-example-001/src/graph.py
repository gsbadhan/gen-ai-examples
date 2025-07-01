from langgraph.graph import StateGraph
from langchain.chains import ConversationChain
from memory import get_user_memory
from config import get_llm


class ChatState:

    def __init__(self, user_id, input_message):
        self.user_id = user_id
        self.input_message = input_message
        self.output_message = None


def respond_node(state: dict) -> dict:
    user_id = state["user_id"]
    input_message = state["input_message"]

    memory = get_user_memory(user_id)
    llm = get_llm()
    chain = ConversationChain(llm=llm, memory=memory)
    output_message = chain.run(input_message)

    return {
        "user_id": user_id,
        "input_message": input_message,
        "output_message": output_message
    }


# Define graph
def get_graph():
    builder = StateGraph(dict)
    builder.add_node("respond", respond_node)
    builder.set_entry_point("respond")
    return builder.compile()

# get the Mermaid description
def show_graph(compile_graph):
    graph = compile_graph.get_graph()
    with open("agent_activity_graph.png", "wb") as f:
        f.write(graph.draw_mermaid_png())
    print("Graph image saved as agent_activity_graph.png")