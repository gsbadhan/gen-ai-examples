import os
import pandas as pd
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

# 1. Setup Pinecone & OpenAI
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "products-catalog-indx"
PINECONE_CLOUD_NAME = os.getenv("PINECONE_CLOUD_NAME")
PINECONE_CLOUD_REGION = os.getenv("PINECONE_CLOUD_REGION")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize Pinecone client.
# Note: on HTTP-401 error or unauthorised error, copy/paste api key directly here.
pc = Pinecone(api_key=PINECONE_API_KEY)

# Create index (only if not exists)
print("Available indexes:", pc.list_indexes().names())

if PINECONE_INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=1536,   # depends on embedding model
        metric="cosine",
        spec=ServerlessSpec(
            cloud=PINECONE_CLOUD_NAME,
            region=PINECONE_CLOUD_REGION
        )
    )

index = pc.Index(PINECONE_INDEX_NAME)

# 2. Load Dataset
df = pd.read_csv("data/product_catalog.csv")

# 3. Generate Embeddings
def get_embedding(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

# 4. CRUD Operations

# Create / Insert
def create_products(df):
    vectors = []
    for _, row in df.iterrows():
        text = f"{row['name']} {row['description']}"
        embedding = get_embedding(text)
        vectors.append({
            "id": row["product_id"],
            "values": embedding,
            "metadata": {
                "name": row["name"],
                "description": row["description"],
                "category": row["category"],
                "price": row["price"],
                "in_stock": row["in_stock"]
            }
        })
    index.upsert(vectors=vectors)
    print("Products inserted into Pinecone")

# Read / Query (Semantic Search)
def search_products(query, top_k=2):
    query_emb = get_embedding(query)
    results = index.query(vector=query_emb, top_k=top_k, include_metadata=True)
    return results

# Update (re-insert with same id)
def update_product(product_id, new_description):
    results = index.fetch(ids=[product_id])
    if not results.vectors:
        print("Product not found")
        return
    metadata = results.vectors[product_id].metadata
    metadata["description"] = new_description
    embedding = get_embedding(metadata["name"] + " " + new_description)
    index.upsert(vectors=[{
        "id": product_id,
        "values": embedding,
        "metadata": metadata
    }])
    print(f"Product {product_id} updated")

# Delete
def delete_product(product_id):
    index.delete(ids=[product_id])
    print(f"Product {product_id} deleted")


# Clean all data from index
def clean_all():
    index.delete(delete_all=True)
    print(f"all deleted")


# 5. Example Usage
if __name__ == "__main__":
    # Insert products
    create_products(df)

    # Search
    print("\n Searching for 'red book':")
    res = search_products("red book")
    for match in res["matches"]:
        print(match["metadata"], "Score:", match["score"])

    # Update
    update_product("prod_002", "An elegant Fossil watch suitable for parties and meetings.")

    # Delete
    delete_product("prod_001")

    # Delete all data
    clean_all()
