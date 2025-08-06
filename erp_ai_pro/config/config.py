# -*- coding: utf-8 -*-
"""
Centralized Configuration for ERP AI Pro
This file breaks the circular import dependency.
"""

from dataclasses import dataclass

@dataclass
class SystemConfig:
    """Centralized configuration for the entire system and all agents."""
    # Model Configuration
    base_model_name: str = "meta-llama/Llama-3.1-8B-Instruct"
    vision_model_name: str = "Salesforce/blip-image-captioning-base"
    clip_model_name: str = "openai/clip-vit-base-patch32"
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Vector Database
    vector_db_type: str = "qdrant"
    vector_db_url: str = "http://localhost:6333"
    collection_name: str = "erp_knowledge_enhanced"

    # Caching
    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 3600

    # Performance
    retrieval_k: int = 10
    rerank_k: int = 5
