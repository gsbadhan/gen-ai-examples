from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_aws import BedrockLLM
from langchain_aws import BedrockEmbeddings



# Initialize llm using Llama 3
llm = BedrockLLM(
    model_id="meta.llama3-8b-instruct-v1:0",
    region_name="ap-south-1",
    model_kwargs={"temperature": 0.5, "max_gen_len": 256}
)


# 1. Load PDF document
loader = PyPDFLoader("data/rating_202504120428_SBI.pdf")
pages = loader.load()

# 2. Split into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
docs = text_splitter.split_documents(pages)

# 3. Generate embeddings & store in FAISS
embeddings = BedrockEmbeddings(
    model_id="amazon.titan-embed-text-v2:0",
    region_name="ap-south-1"
)
vectorstore = FAISS.from_documents(docs, embeddings)

# 5. Set up retriever from vector store
retriever = vectorstore.as_retriever(search_type="similarity", k=3)

# 6. Build a RetrievalQA chain (injects context into prompt!)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True  # Optional: to trace where info came from
)

# 7. Ask a question (embedding is generated, context injected into prompt)
query = "What is summary ?"
result = qa_chain(query)
print("Answer:", result["result"])

query = "What are nagative and positive factors ?"
result = qa_chain(query)
print("Answer:", result["result"])

# Optional: Print context
# print("\n--- Retrieved Context Chunks ---")
# for doc in result["source_documents"]:
#     print(doc.page_content[:300], "\n---")