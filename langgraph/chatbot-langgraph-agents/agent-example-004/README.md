# Description
It gives you basic agentic research chatbot behaviour. Its integrated with RAG(Chroma DB), Tavily.



# chat agent flow graph
![agent flow graph](src/agent_activity_graph.png)


# project setup
1. uv init agent-example-004
2. uv venv
3. source .venv/bin/activate
4. uv sync

# environment configurations, you can put in bash_profile or .env
1. export OPENAI_API_KEY=xxxxxx
2. export TAVILY_API_KEY=xx
3. export LANGSMITH_TRACING=true
4. export LANGSMITH_API_KEY=xxxxxx
5. export LANGSMITH_PROJECT="chatbot-agent-test"


# run agent server locally
1. start agent server: python src/app.py
2. send user questions:
  curl -X POST http://localhost:5000/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "Graph Neural Networks for Traffic Prediction"}'
  
3. shutdown agent server: press CTRL+C or find and kill the port like lsof -i tcp:5000 and kill -9 PID


# test case execution
1. for integration tests: pytest tests/integration
2. for unit tests: pytest tests/unit
3. for code coverage: pytest --cov=src
4. for code coverage report: pytest --cov=src --cov-report=html
