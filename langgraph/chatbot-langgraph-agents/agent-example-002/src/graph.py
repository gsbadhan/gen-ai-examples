from langgraph.graph import StateGraph
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from src.memory import get_user_memory
from src.config import get_llm
from src.rag import get_retriever


# 1. Prepare the LLM and Prompt Template with RAG context
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use the context and chat history to answer."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}\n\nContext:\n{context}")
])

# 2. Create retriever
retriever = get_retriever()

# 2. Define the base LLM chain
llm_chain: Runnable = prompt | get_llm()

# 3. Wrap it with per-user memory
chat_runnable = RunnableWithMessageHistory(
    llm_chain,
    get_user_memory,  # This should return a MessageHistory object (e.g., from Redis or ConversationBufferMemory)
    input_messages_key="input",
    history_messages_key="history"
)

# 5. LangGraph Node Function with RAG
def respond_node(state: dict) -> dict:
    user_id = state["session_id"]
    input_message = state["input_message"]

    #  Perform document retrieval
    docs = retriever.invoke(input_message)
    context = "\n\n".join(doc.page_content for doc in docs) if docs else "No relevant context found."

    #  Invoke with memory and context
    response = chat_runnable.invoke(
        {
            "input": input_message,
            "context": context
        },
        config={"configurable": {"session_id": user_id}}
    )

    return {
        "user_id": user_id,
        "input_message": input_message,
        "output_message": response.content if hasattr(response, "content") else str(response)
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