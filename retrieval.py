# RAG / Vectorstore logic
import os
from typing import List
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.schema import Document
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize embeddings
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

def create_vectorstore() -> Chroma:
    """Create or load the vectorstore."""
    # Create a persistent directory for the vectorstore
    persist_directory = "chroma_db"
    if not os.path.exists(persist_directory):
        os.makedirs(persist_directory)
    
    # Initialize the vectorstore
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
    
    # Check if we need to add documents
    if vectorstore._collection.count() == 0:
        add_documents(vectorstore)
    
    return vectorstore

def add_documents(vectorstore: Chroma) -> None:
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