# -*- coding: utf-8 -*-
"""
This script processes the source knowledge base, creates text embeddings,
and stores them in a ChromaDB vector store.
"""
import json
import os
import sys
from pathlib import Path

# Add the project root to the Python path
# This is a professional way to ensure that imports from other project directories work correctly
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.docstore.document import Document
from tqdm import tqdm

from erp_ai_pro.core.rag_config import RAGConfig

def create_vector_store():
    """Main function to build and persist the vector store."""
    config = RAGConfig()

    print("--- Starting Vector Store Creation ---")

    # 1. Load the source knowledge data
    print(f"Loading knowledge from: {config.knowledge_base_path}")
    with open(config.knowledge_base_path, 'r', encoding='utf-8') as f:
        knowledge_data = json.load(f)
    print(f"Loaded {len(knowledge_data)} knowledge items.")

    # 2. Convert data into LangChain Document objects
    # We create a single document for each Q&A pair, combining them into a coherent text.
    # This helps the retrieval model find relevant context based on either question or answer content.
    documents = []
    for item in tqdm(knowledge_data, desc="Processing documents"):
        content = f"Role: {item['role']}\nQuestion: {item['instruction']}\nAnswer: {item['response']}"
        metadata = {"role": item["role"]}
        doc = Document(page_content=content, metadata=metadata)
        documents.append(doc)
    
    print(f"Created {len(documents)} LangChain documents.")

    # 3. Initialize the embedding model
    print(f"Initializing embedding model: {config.embedding_model_name}")
    # This model runs locally and is great for general-purpose text embeddings.
    embedding_function = SentenceTransformerEmbeddings(model_name=config.embedding_model_name)

    # 4. Create and persist the ChromaDB vector store
    print(f"Creating and persisting vector store at: {config.vector_store_path}")
    if os.path.exists(config.vector_store_path):
        print("Vector store already exists. Deleting old version.")
        # A more robust implementation might update the store instead of deleting.
        import shutil
        shutil.rmtree(config.vector_store_path)

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embedding_function,
        persist_directory=config.vector_store_path,
        collection_name=config.collection_name
    )

    print(f"Vector store created successfully with {vector_store._collection.count()} documents.")
    print("--- Vector Store Creation Complete ---")

if __name__ == "__main__":
    create_vector_store()
