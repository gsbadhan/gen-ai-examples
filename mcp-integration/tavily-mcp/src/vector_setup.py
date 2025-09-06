import os
import pandas as pd
import chromadb
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Set OPENAI_API_KEY before running this script")

# Chroma client
client = chromadb.PersistentClient(path="./chroma_db")

# Embeddings
emb = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=OPENAI_API_KEY)

# Collection (no embedding_function here)
collection = client.get_or_create_collection(name="bank_rates")

# Read CSV
df = pd.read_csv("data/bank_rates.csv")

# Build docs + embeddings
docs, metadatas, ids, vectors = [], [], [], []
for i, row in df.iterrows():
    doc = (f"{row['bank']} in {row['country']} offers FD rate {row['fd_rate']}, "
           f"Home Loan rate {row['home_loan']}, and Personal Loan rate {row['personal_loan']}.")
    docs.append(doc)
    metadatas.append(row.to_dict())
    ids.append(f"rec-{i+1}")
    vectors.append(emb.embed_query(doc))  # embed each doc explicitly

# Insert into Chroma
collection.add(documents=docs, metadatas=metadatas, embeddings=vectors, ids=ids)
print(f"Inserted {len(docs)} records into Chroma collection 'bank_rates'")
