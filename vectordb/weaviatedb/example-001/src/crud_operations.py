import os
from dotenv import load_dotenv
import weaviate
import weaviate.classes.config as wvc
from weaviate.classes.init import Auth
import pandas as pd
import uuid

# Load environment variables
load_dotenv()
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COLLECTION_NAME:str = "product_catalog"

# Connect to Weaviate Cloud
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_URL,
    auth_credentials=Auth.api_key(WEAVIATE_API_KEY),
    skip_init_checks=True,
    headers={
        "X-OpenAI-Api-Key": OPENAI_API_KEY
    }
)
print(f"weaviate db connected {client.is_ready()}")
print(f"db collecions {client.collections.list_all().keys()}")

# create collection
def create_collection():
    if COLLECTION_NAME.lower() not in [key.lower() for key in client.collections.list_all().keys()]:
        props = [
            wvc.Property(name="product_id", data_type=wvc.DataType.TEXT, vectorize_property_name=False),
            wvc.Property(name="name", data_type=wvc.DataType.TEXT, vectorize_property_name=True),
            wvc.Property(name="description", data_type=wvc.DataType.TEXT, vectorize_property_name=True),
            wvc.Property(name="category", data_type=wvc.DataType.TEXT, vectorize_property_name=True),
            wvc.Property(name="price", data_type=wvc.DataType.NUMBER, vectorize_property_name=False),
            wvc.Property(name="in_stock", data_type=wvc.DataType.BOOL, vectorize_property_name=False),
        ]
        
        client.collections.create(
            name=COLLECTION_NAME,
            vector_config=wvc.Configure.Vectors.text2vec_openai(),
            generative_config=wvc.Configure.Generative.openai(),
            properties=props,
            )
        print(f"collection {COLLECTION_NAME} created.")
    else:
        print(f"collection {COLLECTION_NAME} already exist.")


# delete collection
def delete_collection():
    if COLLECTION_NAME not in client.collections.list_all().keys():
        client.collections.delete(name=COLLECTION_NAME)
        print(f"collection {COLLECTION_NAME} deleted.")


# insert csv data
def insert_products(csv_path):
    # Load CSV into pandas DataFrame
    df = pd.read_csv(csv_path)

    collection = client.collections.use(name=COLLECTION_NAME)

    # Convert DataFrame rows into list of dicts
    products = df.to_dict(orient="records")

    responses = []
    for product in products:
        try:
            response = collection.data.insert(
                uuid= str(uuid.uuid5(uuid.NAMESPACE_DNS,str(product["product_id"]))),
                properties={
                    "product_id": str(product["product_id"]),
                    "name": str(product["name"]),
                    "description": str(product["description"]),
                    "category": str(product["category"]),
                    "price": float(product["price"]),
                    "in_stock": bool(product["in_stock"]),
                }
            )
            responses.append(response)
            print(f"Inserted: {product['name']} (UUID: {response})")
        except Exception as e:
            print(f"Failed to insert {product['name']}: {e}")

    print(f"\n Inserted {len(responses)} products successfully out of {len(products)}.")
    return responses

# search product
def search(query: str, top_k=3):
    print(f"searching query {query}")
    collection = client.collections.use(name=COLLECTION_NAME)
    products = collection.query.near_text(query=query, limit=top_k)
    if(products is not None):
        for product in products.objects:
            print(f"\n search result {product.properties}")
        return products.objects
    else:
        print(f"\n No result found {query}")

# find product by id
def find_one(product_id: str):
    print(f"finding product_id {product_id}")
    collection = client.collections.use(name=COLLECTION_NAME)
    product =collection.query.fetch_object_by_id(uuid=str(uuid.uuid5(uuid.NAMESPACE_DNS, product_id)))
    if product is not None:
        print(f"product {product.properties}")
        return product
    else:
        print(f"product_id not found")


def update(product_id: str, new_description: str):
    print(f"updating product_id {product_id}")
    collection = client.collections.use(name=COLLECTION_NAME)
    old_product = find_one(product_id = product_id)
    old_product_props = old_product.properties;
    collection.data.update(
                           uuid=str(uuid.uuid5(uuid.NAMESPACE_DNS, product_id)), 
                           properties={
                                "product_id": str(old_product_props["product_id"]),
                                "name": str(old_product_props["name"]),
                                "description": new_description,
                                "category": str(old_product_props["category"]),
                                "price": float(old_product_props["price"]),
                                "in_stock": bool(old_product_props["in_stock"]),
                           }
                           )
    print(f"product_id {product_id} updated")


# ----------------- Example Run -----------------
if __name__ == "__main__":
    try:
        create_collection()
        insert_products(csv_path="data/product_catalog.csv")
        search(query="red book", top_k=3)
        find_one(product_id="prod_019")
        update(product_id="prod_019", new_description="A high-quality green book by Random House. Perfect for everyday use v3.")
        delete_collection()
    except Exception as e:
        client.close()
        raise e
    finally:
        client.close()

