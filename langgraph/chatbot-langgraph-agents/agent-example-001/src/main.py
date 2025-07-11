from fastapi import FastAPI
from pydantic import BaseModel
from src.graph import get_graph, show_graph

app = FastAPI()
chat_graph = get_graph()
show_graph(chat_graph)

class ChatRequest(BaseModel):
    user_id: str
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    state = {
    "session_id": req.user_id,
    "input_message": req.message
    }
    result = chat_graph.invoke(state)
    return {"response": result["output_message"]}
