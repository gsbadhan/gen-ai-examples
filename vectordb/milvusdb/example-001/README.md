# Description
CRUD operations of Milvus (or zilliz) DB https://milvus.io/.

# project setup
1. uv init example-001 (optional)
2. uv venv
3. source .venv/bin/activate
4. uv sync

# Environment configurations, you can put in bash_profile or .env
1. OPENAI_API_KEY= openai api key
2. MILVUS_URL= milvus db url
3. MILVUS_TOKEN= milvus db token

# Build custom product catalog data
python src/create_product_catalog.py

# Run CRUD operations
python src/crud_operations.py


# Tests execution
