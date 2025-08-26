# Description
CRUD operations of Qdrant DB https://cloud.qdrant.io/.

# project setup
1. uv init example-001 (optional)
2. uv venv
3. source .venv/bin/activate
4. uv sync

# Environment configurations, you can put in bash_profile or .env
1. QDRANT_API_KEY= qdrant api key
2. OPENAI_API_KEY= openai api key
3. QDRANT_URL= qdrant cloud url

# Build custom product catalog data
python src/create_product_catalog.py

# Run CRUD operations
python src/crud_operations.py


# Tests execution
