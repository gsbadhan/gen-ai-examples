from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma


PERSIST_DIR = "./vector_store"

def get_retriever():
    loader = TextLoader("rag_docs/country_information.txt")  # Replace with your document
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    db = Chroma.from_documents(
        documents=chunks,
        embedding=OpenAIEmbeddings(),
        persist_directory=PERSIST_DIR
    )
    print("RAG initialized.. !")

    return db.as_retriever()