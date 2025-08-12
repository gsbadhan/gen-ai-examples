# Description
Multi agent flow using Autogen framework https://microsoft.github.io/autogen/stable//index.html. It has back & forth review calls.


# project setup
1. uv init agent-example-001
2. uv venv
3. source .venv/bin/activate
4. uv sync

# environment configurations, you can put in bash_profile or .env
1. export OPENAI_API_KEY=xxxxxx
2. export TAVILY_API_KEY=xx


# run agent server locally
1. start agent server: python src/app.py
2. send user questions:
  curl -X POST http://127.0.0.1:5000/research \
     -H "Content-Type: application/json" \
     -d '{"topic":"quantum computing applications"}'
  
3. shutdown agent server: press CTRL+C or find and kill the port like lsof -i tcp:5000 and kill -9 PID


# test case execution
1. for integration tests: pytest tests/integration
2. for unit tests: pytest tests/unit
3. for code coverage: pytest --cov=src
4. for code coverage report: pytest --cov=src --cov-report=html