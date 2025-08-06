# -*- coding: utf-8 -*-
"""
Configuration for the RAG pipeline.
"""
import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class RAGConfig:
    # Path to the source knowledge base file
    knowledge_base_path: str = os.getenv("ERP_KNOWLEDGE_BASE_PATH", "erp_ai_pro/data_preparation/sample_erp_knowledge.json")

    # Path to the persistent ChromaDB vector store
    vector_store_path: str = os.getenv("VECTOR_STORE_PATH", "data_preparation/vector_store")

    # Name of the ChromaDB collection
    collection_name: str = os.getenv("CHROMA_COLLECTION_NAME", "erp_knowledge")

    # Sentence Transformer model for creating embeddings
    embedding_model_name: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

    # Number of search results to retrieve from the vector store
    retrieval_k: int = int(os.getenv("RETRIEVAL_K", 3))

    # --- LLM Configuration ---
    # This section is designed to be compatible with a future Model Registry.
    # The base model identifier from Hugging Face Hub.
    base_model_name: str = os.getenv("BASE_MODEL_NAME", "google/flan-t5-base")

    # The fine-tuned adapter path. This can be a local path or a Hub identifier.
    # In a production MLOps setup, this would be populated by the CI/CD pipeline
    # after a new model is trained and registered.
    # Set to an empty string or None to use the base model only.
    finetuned_model_path: str = os.getenv("FINETUNED_MODEL_PATH", "path/to/your/finetuned_erp_model") # Placeholder path

    # --- Re-ranker Configuration ---
    reranker_model_name: str = os.getenv("RERANKER_MODEL_NAME", "cross-encoder/ms-marco-MiniLM-L-6-v2") # Example re-ranker model

    # --- Neo4j Configuration ---
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_username: str = os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "password")

    
