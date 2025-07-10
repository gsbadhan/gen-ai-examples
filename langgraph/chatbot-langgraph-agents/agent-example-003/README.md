# Description
It gives you basic research agent behaviour with RAG. It has in-memory history for chat context user wise and chromadb as vector database. It can read .txt and .pdf documents for RAG. It has Tavily external web-call integration.



# chat agent flow graph
![agent flow graph](src/agent_activity_graph.png)


# project setup
1. uv init agent-example-003
2. uv venv
3. source .venv/bin/activate
4. uv sync

# environment configurations, you can put in bash_profile or .env
1. export OPENAI_API_KEY=xxxxxx
2. export TAVILY_API_KEY=xx
3. export LANGSMITH_TRACING=true
4. export LANGSMITH_API_KEY=xxxxxx
5. export LANGSMITH_PROJECT="chatbot-agent-test"

# RAG information
1. you can put .txt or .pdf files in /rag_docs folder

# run agent server locally
1. start agent server: uvicorn src.main:app --host 0.0.0.0 --port 8000
2. send user questions: 
  curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "abc123", "message": "can you summarise the research paper AUTOMATIC FLOOD DETECTION FROM SENTINEL-1 DATA USING DEEP LEARNING ARCHITECTURES ?"}'

  
3. shutdown agent server: press CTRL+C or find and kill the port like lsof -i tcp:8000 and kill -9 PID


# test case execution
1. for integration tests: pytest tests/integration
2. for unit tests: pytest tests/unit
3. for code coverage: pytest --cov=src
4. for code coverage report: pytest --cov=src --cov-report=html
