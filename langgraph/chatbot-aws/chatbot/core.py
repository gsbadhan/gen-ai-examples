from typing import List, Dict, Any, Optional
from langchain_aws import BedrockLLM
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import Graph, END
from langchain_community.chat_message_histories import ChatMessageHistory

class Llama3Chatbot:
    """Stateful chatbot powered by AWS Bedrock's Llama 3"""
    
    def __init__(self, model_id: str):
        self.llm = self._init_llm(model_id)
        self.prompt = self._build_prompt()
        self.workflow = self._build_workflow()
    
    def _init_llm(self, model_id: str) -> BedrockLLM:
        """Initialize AWS Bedrock LLM"""
        return BedrockLLM(
            model_id=model_id,
            region_name="ap-south-1",
            model_kwargs={
                "temperature": 0.3,
                "max_gen_len": 256
            }
        )
    
    def _build_prompt(self) -> ChatPromptTemplate:
        """Create conversation prompt template"""
        system_prompt = "You are a helpful assistant. Keep responses concise."
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("placeholder", "{messages}"),
            ("human", "{user_query}")
        ])
    
    def _build_workflow(self) -> Graph:
        """Fixed workflow with proper entrypoint"""
        workflow = Graph()
        
        workflow.add_node("start", self._process_input)
        workflow.add_node("generate", self._generate_response)
        
        # REQUIRED: Set entry and exit points
        workflow.set_entry_point("start")
        workflow.add_edge("start", "generate")
        workflow.add_edge("generate", END)
        
        return workflow.compile()
    
    
    def _process_input(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare input for LLM"""
        return {
            "messages": state["messages"],
            "user_query": state["user_query"]
        }
    
    def _generate_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate and format LLM response"""
        formatted = self.prompt.format_messages(
            messages=state["messages"],
            user_query=state["user_query"]
        )
        response = self.llm.invoke(formatted)
        return {
            "messages": state["messages"] + [AIMessage(content=response)],
            "response": response
        }





class ChatSession:
    """Manages conversation state and history"""
    
    def __init__(self, chatbot: Llama3Chatbot):
        self.chatbot = chatbot
        self.history = ChatMessageHistory()
    
    def send_message(self, user_query: str) -> str:
        """Process user message and return AI response"""
        # Update state
        self.history.add_user_message(user_query)
        state = {
            "messages": self.history.messages,
            "user_query": user_query
        }
        
        # Execute workflow
        result = self.chatbot.workflow.invoke(state)
        
        # Store and return response
        self.history.add_ai_message(result["response"])
        return result["response"]