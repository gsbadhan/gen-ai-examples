from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

RAG_DIR = "rag_docs/"
PERSIST_DIR = "./vector_store"


def get_retriever():
        doc_loaders = [
                DirectoryLoader(path=RAG_DIR, glob="**/*.pdf", loader_cls=PyPDFLoader, show_progress=True,use_multithreading=True),
                DirectoryLoader(path=RAG_DIR, glob="**/*.txt", loader_cls=TextLoader, show_progress=True,use_multithreading=True),
        ]
        documents =[]
        for loader in doc_loaders:
                documents.extend(loader.load())

        txt_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = txt_splitter.split_documents(documents=documents)
        embedding = OpenAIEmbeddings()
        db = Chroma.from_documents(
        documents=chunks,
        embedding=embedding,
        persist_directory=PERSIST_DIR)
        print(f"RAG initialized, chroma instance={db}")
        return db.as_retriever()