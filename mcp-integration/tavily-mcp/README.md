# Description
Banking rates agent which is integrated with Tavily MCP server, Vector DB, LLM and langsmith. Tavily MCP doc https://docs.tavily.com/documentation/mcp.


# project setup
1. uv init tavily-mcp (optional)
2. uv venv
3. source .venv/bin/activate
4. uv sync


# Environment configurations, you can put in bash_profile or .env
1. OPENAI_API_KEY= openai api key
2. TAVILY_API_KEY= tavily MCP api key


# Setup and build vector db with data
python src/vector_setup.py

# Run bank AI agent
streamlit run src/streamlit_app.py


# Tests execution