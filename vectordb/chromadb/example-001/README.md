# Description
CRUD operations of chromadb.

# project setup
1. uv init example-001 (optional)
2. uv venv
3. source .venv/bin/activate
4. uv sync

# Build custom product catalog data
python src/create_product_catalog.py

# Run CRUD operations
python crud_operations.py


# Tests execution
1. run all integration tests: python -m unittest discover -s tests -v
2. run one integration test: python -m unittest tests.test_crud_operations_integration.TestChromaDBCatalogIntegration.test_1_create_catalog_from_csv -v
