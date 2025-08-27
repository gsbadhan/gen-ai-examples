import os
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from pymilvus import MilvusClient, FieldSchema, CollectionSchema, DataType, Collection

# Load environment variables
load_dotenv()
MILVUS_URL = os.getenv("MILVUS_URL")  # e.g., "https://in01-xxxx.api.gcp-us-west1.zillizcloud.com"
MILVUS_TOKEN = os.getenv("MILVUS_TOKEN")  # cloud token
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# Connect to Milvus
milvus_client = MilvusClient(uri=MILVUS_URL,
                             token=MILVUS_TOKEN
                             )

COLLECTION_NAME = "product_catalog"
DIM = 1536  # OpenAI embedding dimension

# Define schema
fields = [
    FieldSchema(name="product_id", dtype=DataType.VARCHAR, is_primary=True, auto_id=False, max_length=100),
    FieldSchema(name="name", dtype=DataType.VARCHAR, max_length=500),
    FieldSchema(name="description", dtype=DataType.VARCHAR, max_length=2000),
    FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=200),
    FieldSchema(name="price", dtype=DataType.FLOAT),
    FieldSchema(name="in_stock", dtype=DataType.BOOL),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=DIM)
]
schema = CollectionSchema(fields, description="Product catalog collection")

def generate_embedding(text: str):
    """Generate embedding using OpenAI"""
    emb = client.embeddings.create(model="text-embedding-3-small", input=text)
    return emb.data[0].embedding


# Create collection
def create_schema_product():
    #List of Existing collections
    print(f"Existing collections {milvus_client.list_collections()}")

    # Create collection if not exists
    if COLLECTION_NAME not in milvus_client.list_collections():
        milvus_client.create_collection(collection_name=COLLECTION_NAME, schema=schema)
        print(f"Collection {COLLECTION_NAME} created.")
        index_params = milvus_client.prepare_index_params();
        index_params.add_index(field_name="vector",
                            index_name="vector_idx",   
                            index_type= "IVF_FLAT",
                            metric_type= "COSINE",
                            params= {"nlist": 128}
                            )
        milvus_client.create_index(collection_name=COLLECTION_NAME, index_params=index_params)
    else:
        print(f"Collection {COLLECTION_NAME} already exists.")


# Create
def insert_products_from_csv(file_path: str):
    df = pd.read_csv(file_path)
    
    records = []
    for _, row in df.iterrows():
        embedding = generate_embedding(row["description"])
        records.append({
            "product_id": str(row["product_id"]),
            "name": row["name"],
            "description": row["description"],
            "category": row["category"],
            "price": float(row["price"]),
            "in_stock": bool(row["in_stock"]),
            "vector": embedding
        })

    milvus_client.insert(collection_name=COLLECTION_NAME, data=records)
    milvus_client.flush(collection_name=COLLECTION_NAME)
    print(f"Inserted {len(df)} products from {file_path}")

# find by product id
def find_one(product_id: str) -> dict:
    product = milvus_client.get(collection_name=COLLECTION_NAME,
                                ids=[product_id])
    print(f"product {product_id} count {len(product)}")
    if len(product) > 0:
        print(f"product_id found {product[0]}")
        return product[0]
    else:
        print(f"product_id not found {product_id}")
        return {}

# search
def search_product(query: str, top_k: int = 3):
    q_emb = generate_embedding(query)
    results = milvus_client.search(
        collection_name= COLLECTION_NAME,
        data=[q_emb],
        anns_field="vector",
        search_params={"metric_type": "COSINE", "params": {"nprobe": 10}},
        limit=top_k,
        output_fields=["product_id", "name", "description", "category", "price", "in_stock"]
    )
    print("\n Search Results:")
    for res in results[0]:
        print(f"ID: {res.entity.get('product_id')} | Name: {res.entity.get('name')} | "
              f"Category: {res.entity.get('category')} | Price: {res.entity.get('price')} | "
              f"In Stock: {res.entity.get('in_stock')} | Score: {res.score:.4f}")

# update
def update_product(product_id: str, new_description: str):
    old_product = find_one(product_id=product_id)
    embedding = generate_embedding(new_description)
    print(f"sss {old_product['product_id']}")
    new_product={
            "product_id": old_product['product_id'],
            "name": old_product['name'],
            "description": new_description,
            "category": old_product['category'],
            "price": old_product['price'],
            "in_stock": old_product['in_stock'],
            "vector": embedding
        }
    milvus_client.upsert(collection_name=COLLECTION_NAME, data=new_product)
    milvus_client.flush(collection_name=COLLECTION_NAME)
    print(f"Product {product_id} updated.")

# delete
def delete_product(product_id: str):
    deleted_product = milvus_client.delete(collection_name=COLLECTION_NAME, ids=product_id)
    print(f"Product {deleted_product} deleted.")

# delete all
def delete_all_products():
    milvus_client.drop_index(collection_name=COLLECTION_NAME, index_name="vector_idx")
    print(f"Collection {COLLECTION_NAME} index name vector dropped.")
    milvus_client.drop_collection(collection_name=COLLECTION_NAME)
    print(f"Collection {COLLECTION_NAME} dropped.")
    


# ----------------- Example Run -----------------
if __name__ == "__main__":

    # delete collection
    #delete_all_products()

    # create collection
    create_schema_product()

    # Insert data from CSV
    insert_products_from_csv("data/product_catalog.csv")

    # Search example
    #search_product("blue smartphone")
    #search_product("HarperCollins")

    # Update example
    #update_product("prod_002", "A premium green Sennheiser headphone, perfect for music lovers.")

    # Delete example
    # delete_product("prod_001")

    # find example
    find_one("prod_002")
