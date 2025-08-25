# Description
CRUD operations of Pinecone DB https://app.pinecone.io/.

# project setup
1. uv init example-001 (optional)
2. uv venv
3. source .venv/bin/activate
4. uv sync

# Environment configurations, you can put in bash_profile or .env
1. PINECONE_API_KEY=your_pinecone_api_key_here
2. OPENAI_API_KEY=your_openai_api_key_here
3. PINECONE_CLOUD_NAME=cloud name e.g. aws
4. PINECONE_CLOUD_REGION=cloud region name e.g. us-east-1

# Build custom product catalog data
python src/create_product_catalog.py

# Run CRUD operations
python src/crud_operations.py


# Tests execution

# Pinecone API URL
curl -i https://api.pinecone.io/indexes -H "Api-Key: $PINECONE_API_KEY"
