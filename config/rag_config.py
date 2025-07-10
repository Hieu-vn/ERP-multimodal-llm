# -*- coding: utf-8 -*-
"""
Configuration for the RAG pipeline.
"""
from dataclasses import dataclass

@dataclass
class RAGConfig:
    # Path to the source knowledge base file
    knowledge_base_path: str = "data_preparation/sample_erp_knowledge.json"

    # Path to the persistent ChromaDB vector store
    vector_store_path: str = "data_preparation/vector_store"

    # Name of the ChromaDB collection
    collection_name: str = "erp_knowledge"

    # Sentence Transformer model for creating embeddings
    embedding_model_name: str = "all-MiniLM-L6-v2"

    # Number of search results to retrieve from the vector store
    retrieval_k: int = 3
