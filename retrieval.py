# RAG / Vectorstore logic
import os
from typing import List
import chromadb
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def create_vectorstore():
    """Create or load the vectorstore using chromadb.PersistentClient."""
    client = chromadb.PersistentClient(path="./chroma_db")
    embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    collection = Chroma(
        client=client,
        collection_name="agent_knowledge",
        embedding_function=embedding
    )
    return collection

def add_documents(vectorstore):
    """Add documents from knowledge.txt to the vectorstore."""
    # Load the knowledge file
    loader = TextLoader("knowledge.txt")
    documents = loader.load()
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    
    # Add chunks to vectorstore
    vectorstore.add_documents(chunks)

def query_knowledge(query: str, vectorstore: Chroma, k: int = 3) -> List[Document]:
    """Query the vectorstore for relevant documents."""
    return vectorstore.similarity_search(query, k=k)