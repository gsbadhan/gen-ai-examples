import os
import getpass
from langchain_openai import OpenAIEmbeddings

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")


embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# Sample texts to embed
texts = ["The cat has kitten", "The dog has puppy"]

# Generate embeddings
vectors = embeddings.embed_documents(texts)


# Print the vector for each text
for i, vector in enumerate(vectors):
    print(f"Text: {texts[i]}")
    print(f"Vector (length {len(vector)}): {vector[:5]}...\n")  # Just showing first 5 numbers