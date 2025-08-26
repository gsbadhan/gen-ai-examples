import os
import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.http import models
from openai import OpenAI
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 

QDRANT_URL = os.getenv("QDRANT_URL")

QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

COLLECTION_NAME = "products_catalog"

# Initialize clients
client = OpenAI(api_key=OPENAI_API_KEY)
qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=10.0)

# Generate embedding
def generate_embedding(text: str):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

# Ensure collection exists
def init_collection():
    if not qdrant.collection_exists(COLLECTION_NAME):
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=1536,   # depends on embedding model (text-embedding-3-small = 1536)
                distance=models.Distance.COSINE,
            ),
        )

# Load CSV
def load_products(csv_file: str):
    return pd.read_csv(csv_file)

# Insert products
def insert_products(df):
    points = []
    for _, row in df.iterrows():
        vector = generate_embedding(row["description"])
        metadata = {
            "product_id": row["product_id"],
            "name": row["name"],
            "description": row["description"],
            "category": row["category"],
            "price": float(row["price"]),
            "in_stock": bool(row["in_stock"]),
        }
        points.append(
            models.PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_DNS,row["product_id"])),  # use uuid of product_id as point id
                vector=vector,
                payload=metadata,
            )
        )
    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    print("Products inserted into Qdrant")

# Search
def search_products(query: str, top_k=3):
    query_vector = generate_embedding(query)
    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k,
    )
    for r in results:
        print(r.payload, "Score:", r.score)

# Update
def update_product(product_id: str, new_description: str):
    vector = generate_embedding(new_description)
    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            models.PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_DNS,product_id)),
                vector=vector,
                payload={"description": new_description}
            )
        ]
    )
    print(f"Product {product_id} updated")

# Delete
def delete_product(product_id: str):
    qdrant.delete(
        collection_name=COLLECTION_NAME,
        points_selector=models.PointIdsList(points=[str(uuid.uuid5(uuid.NAMESPACE_DNS,product_id))])
    )
    print(f"Product {product_id} deleted")


# Delete all records from collection
def delete_all_products():
    qdrant.delete_collection(collection_name=COLLECTION_NAME)
    print(f"collection_name {COLLECTION_NAME} deleted")
    print(f"collection list {qdrant.get_collections()}")


if __name__ == "__main__":

    # 1. Create collection
    init_collection()

    # 2. Load and insert data
    df = load_products("data/product_catalog.csv")
    #insert_products(df)

    # 3. Search
    print("\n Searching for 'red book':")
    search_products("red book")

    # 4. Update
    update_product("prod_002", "An elegant Fossil watch suitable for parties and meetings.")

    # 5. Search again
    print("\n Searching for 'Fossil watch':")
    search_products("Fossil watch")

    # 6. Delete
    delete_product("prod_001")

    # 7. Verify deletion
    print("\n Searching after deletion:")
    search_products("red book")

    # 8. Delete all
    delete_all_products()
