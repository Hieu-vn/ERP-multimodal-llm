# -*- coding: utf-8 -*-
"""
Script to create and persist the ChromaDB vector store from the ERP knowledge base.
"""
import json
from pathlib import Path
import sys

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores.utils import filter_complex_metadata

# Add the project root to the Python path for robust imports
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from erp_ai_pro.core.rag_config import RAGConfig

def create_vector_store():
    config = RAGConfig()

    # Construct the absolute path to the knowledge base file
    knowledge_base_file = project_root / config.knowledge_base_path
    print(f"--- Creating Vector Store from: {knowledge_base_file} ---")

    # Load knowledge base
    try:
        with open(knowledge_base_file, 'r', encoding='utf-8') as f:
            knowledge_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Knowledge base file not found at {knowledge_base_file}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in knowledge base file at {knowledge_base_file}")
        sys.exit(1)

    # Convert data to LangChain Document format
    documents = []
    for item in knowledge_data:
        doc = Document(
            page_content=item["content"],
            metadata=item.get("metadata", {})
        )
        documents.append(doc)

    if not documents:
        print("No documents found in the knowledge base. Vector store will be empty.")
        return

    # Filter complex metadata
    documents = filter_complex_metadata(documents)

    # Initialize embedding function
    print(f"Initializing embedding model: {config.embedding_model_name}")
    embedding_function = SentenceTransformerEmbeddings(model_name=config.embedding_model_name)

    # Create and persist the vector store
    print(f"Creating and persisting ChromaDB vector store to: {config.vector_store_path}")
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embedding_function,
        persist_directory=str(project_root / config.vector_store_path),
        collection_name=config.collection_name
    )
    vector_store.persist()
    print("Vector store created and persisted successfully.")

if __name__ == "__main__":
    create_vector_store()