
# Ollama infrastructure
1. Download ollama LLMs studio from https://ollama.com and install it on local machine 
2. Pull llm model `ollama pull llama3.1`
3. Pull embeddings model `ollama pull mxbai-embed-large`

# How to run
1. Go to folder local-ollama-api
2. Create folder venv : python -m venv venv
3. Activate the virtual environment on mac : source venv/bin/activate
4. Install dependencies : pip install -r requirements.txt
5. Run program : python llama3.py

