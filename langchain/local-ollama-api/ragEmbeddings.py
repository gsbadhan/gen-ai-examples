from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_ollama import OllamaEmbeddings
from langchain_ollama.llms import OllamaLLM


# Initialize llm using Llama 3
llm = OllamaLLM(model="llama3.1") 

# 1. Load PDF document
loader = PyPDFLoader("data/rating_202504120428_SBI.pdf")
pages = loader.load()

# 2. Split into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
docs = text_splitter.split_documents(pages)

# 3. Generate embeddings & store in FAISS
embeddings = OllamaEmbeddings(model="mxbai-embed-large",)
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
result = qa_chain.invoke(query)
print("Answer:", result["result"])

query = "What are nagative and positive factors ?"
result = qa_chain.invoke(query)
print("Answer:", result["result"])

# Optional: Print context
# print("\n--- Retrieved Context Chunks ---")
# for doc in result["source_documents"]:
#     print(doc.page_content[:300], "\n---")