# -*- coding: utf-8 -*-
"""
Enhanced RAG Pipeline with Modern AI Models and Multimodal Support
Includes: Llama-3.1, GraphRAG, Streaming, Multimodal Processing, Advanced Caching
"""

import sys
import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime
import torch
from tenacity import retry, stop_after_attempt, wait_exponential

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Modern AI Libraries
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, 
    pipeline, BlipProcessor, BlipForConditionalGeneration,
    CLIPProcessor, CLIPModel
)
from vllm import LLM, SamplingParams
import ollama

# Enhanced LangChain
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_experimental.graph_transformers.diffbot import DiffbotGraphTransformer
from langgraph.graph import Graph, StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import Runnable, RunnableLambda
from langchain_core.tools import tool

# Vector Databases
import chromadb
from pinecone import Pinecone
import weaviate
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Multimodal Processing
from PIL import Image
import cv2
import pytesseract
import easyocr
from pdf2image import convert_from_path
import clip

# Enhanced Utilities
import redis
import diskcache
import networkx as nx
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss

# Monitoring
from prometheus_client import Counter, Histogram, Gauge
import structlog

# Configure structured logging
logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger()

# Metrics
query_counter = Counter('rag_queries_total', 'Total number of RAG queries')
response_time = Histogram('rag_response_time_seconds', 'Response time for RAG queries')
active_queries = Gauge('rag_active_queries', 'Number of active RAG queries')

@dataclass
class EnhancedRAGConfig:
    """Enhanced configuration for the RAG pipeline."""
    
    # Model Configuration
    base_model_name: str = "meta-llama/Llama-3.1-8B-Instruct"
    vision_model_name: str = "Salesforce/blip-image-captioning-base"
    clip_model_name: str = "openai/clip-vit-base-patch32"
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Vector Database
    vector_db_type: str = "qdrant"  # qdrant, pinecone, weaviate, chromadb
    vector_db_url: str = "http://localhost:6333"
    collection_name: str = "erp_knowledge_enhanced"
    
    # Graph Database
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "password"
    
    # Caching
    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 3600  # 1 hour
    
    # Performance
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 0.9
    retrieval_k: int = 10
    rerank_k: int = 5
    
    # Streaming
    stream_chunk_size: int = 1024
    stream_timeout: int = 30

class MultimodalProcessor:
    """Handles multimodal content processing."""
    
    def __init__(self, config: EnhancedRAGConfig):
        self.config = config
        self.setup_models()
        
    def setup_models(self):
        """Initialize multimodal models."""
        # BLIP for image captioning
        self.blip_processor = BlipProcessor.from_pretrained(self.config.vision_model_name)
        self.blip_model = BlipForConditionalGeneration.from_pretrained(self.config.vision_model_name)
        
        # CLIP for image understanding
        self.clip_processor = CLIPProcessor.from_pretrained(self.config.clip_model_name)
        self.clip_model = CLIPModel.from_pretrained(self.config.clip_model_name)
        
        # OCR engines
        self.easyocr_reader = easyocr.Reader(['en', 'vi'])
        
        logger.info("Multimodal models initialized successfully")
    
    async def process_image(self, image_path: str) -> Dict[str, Any]:
        """Process image and extract information."""
        try:
            # Load image
            image = Image.open(image_path).convert('RGB')
            
            # Generate caption
            inputs = self.blip_processor(image, return_tensors="pt")
            out = self.blip_model.generate(**inputs, max_length=100)
            caption = self.blip_processor.decode(out[0], skip_special_tokens=True)
            
            # Extract text using OCR
            ocr_text = self.easyocr_reader.readtext(np.array(image), detail=0)
            
            # Get image embeddings
            clip_inputs = self.clip_processor(images=image, return_tensors="pt")
            image_features = self.clip_model.get_image_features(**clip_inputs)
            
            return {
                "caption": caption,
                "ocr_text": " ".join(ocr_text) if ocr_text else "",
                "image_embeddings": image_features.detach().numpy().tolist(),
                "image_type": "chart" if self._is_chart(image) else "document"
            }
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return {"error": str(e)}
    
    def _is_chart(self, image: Image.Image) -> bool:
        """Detect if image is a chart/graph."""
        # Simple heuristic - can be improved with specialized models
        np_image = np.array(image)
        return len(np.unique(np_image)) > 100  # Charts typically have many colors

class GraphRAGProcessor:
    """Implements GraphRAG for enhanced reasoning."""
    
    def __init__(self, config: EnhancedRAGConfig):
        self.config = config
        self.graph = nx.DiGraph()
        self.communities = {}
        
    async def build_knowledge_graph(self, documents: List[Dict[str, Any]]):
        """Build knowledge graph from documents."""
        logger.info("Building knowledge graph...")
        
        for doc in documents:
            # Extract entities and relationships
            entities = await self._extract_entities(doc['content'])
            relationships = await self._extract_relationships(doc['content'])
            
            # Add to graph
            for entity in entities:
                self.graph.add_node(entity['name'], **entity)
            
            for rel in relationships:
                self.graph.add_edge(rel['source'], rel['target'], **rel)
        
        # Detect communities
        self.communities = self._detect_communities()
        logger.info(f"Knowledge graph built with {len(self.graph.nodes)} nodes")
    
    async def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities from text."""
        # Simplified entity extraction - can be enhanced with NER models
        entities = []
        # Add your entity extraction logic here
        return entities
    
    async def _extract_relationships(self, text: str) -> List[Dict[str, Any]]:
        """Extract relationships from text."""
        # Simplified relationship extraction
        relationships = []
        # Add your relationship extraction logic here
        return relationships
    
    def _detect_communities(self) -> Dict[str, List[str]]:
        """Detect communities in the knowledge graph."""
        import networkx.algorithms.community as nx_comm
        communities = nx_comm.greedy_modularity_communities(self.graph)
        return {f"community_{i}": list(community) for i, community in enumerate(communities)}

class VectorDatabase:
    """Unified vector database interface."""
    
    def __init__(self, config: EnhancedRAGConfig):
        self.config = config
        self.client = None
        self.setup_client()
    
    def setup_client(self):
        """Setup vector database client."""
        if self.config.vector_db_type == "qdrant":
            self.client = QdrantClient(url=self.config.vector_db_url)
            self._setup_qdrant_collection()
        elif self.config.vector_db_type == "pinecone":
            self.client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        elif self.config.vector_db_type == "weaviate":
            self.client = weaviate.Client(self.config.vector_db_url)
        else:
            # Fallback to ChromaDB
            self.client = chromadb.Client()
    
    def _setup_qdrant_collection(self):
        """Setup Qdrant collection."""
        try:
            self.client.create_collection(
                collection_name=self.config.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
        except Exception as e:
            logger.info(f"Collection already exists or error: {e}")
    
    async def search(self, query_vector: List[float], k: int = 10) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        if self.config.vector_db_type == "qdrant":
            results = self.client.search(
                collection_name=self.config.collection_name,
                query_vector=query_vector,
                limit=k
            )
            return [{"id": r.id, "score": r.score, "payload": r.payload} for r in results]
        
        # Add implementations for other vector databases
        return []

class CacheManager:
    """Advanced caching with Redis and disk cache."""
    
    def __init__(self, config: EnhancedRAGConfig):
        self.config = config
        self.redis_client = None
        self.disk_cache = diskcache.Cache('/tmp/rag_cache')
        self.setup_redis()
    
    def setup_redis(self):
        """Setup Redis client."""
        try:
            self.redis_client = redis.from_url(self.config.redis_url)
            self.redis_client.ping()
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.warning(f"Redis not available: {e}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value."""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            
            # Fallback to disk cache
            return self.disk_cache.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None):
        """Set cached value."""
        try:
            ttl = ttl or self.config.cache_ttl
            
            if self.redis_client:
                self.redis_client.setex(key, ttl, json.dumps(value))
            
            # Also store in disk cache
            self.disk_cache.set(key, value, expire=ttl)
        except Exception as e:
            logger.error(f"Cache set error: {e}")

class EnhancedRAGPipeline:
    """Enhanced RAG Pipeline with modern AI capabilities."""
    
    def __init__(self, config: EnhancedRAGConfig = None):
        self.config = config or EnhancedRAGConfig()
        self.multimodal_processor = MultimodalProcessor(self.config)
        self.graph_processor = GraphRAGProcessor(self.config)
        self.vector_db = VectorDatabase(self.config)
        self.cache_manager = CacheManager(self.config)
        self.llm = None
        self.embedding_model = None
        
    async def setup(self):
        """Setup the pipeline."""
        logger.info("Setting up Enhanced RAG Pipeline...")
        
        # Setup LLM
        await self._setup_llm()
        
        # Setup embedding model
        self.embedding_model = SentenceTransformer(self.config.embedding_model_name)
        
        # Setup vector database
        await self._setup_vector_db()
        
        logger.info("Enhanced RAG Pipeline setup complete")
    
    async def _setup_llm(self):
        """Setup the language model."""
        try:
            # Try VLLM first for better performance
            self.llm = LLM(
                model=self.config.base_model_name,
                tensor_parallel_size=torch.cuda.device_count() if torch.cuda.is_available() else 1,
                gpu_memory_utilization=0.8
            )
            logger.info("VLLM model loaded successfully")
        except Exception as e:
            logger.warning(f"VLLM failed, falling back to transformers: {e}")
            # Fallback to transformers
            self.tokenizer = AutoTokenizer.from_pretrained(self.config.base_model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.config.base_model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
    
    async def _setup_vector_db(self):
        """Setup vector database with sample data."""
        # This would typically load your ERP knowledge base
        pass
    
    async def query_stream(self, role: str, question: str, **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream query results."""
        query_counter.inc()
        
        with response_time.time():
            active_queries.inc()
            try:
                # Check cache first
                cache_key = f"query:{role}:{hash(question)}"
                cached_result = await self.cache_manager.get(cache_key)
                
                if cached_result:
                    yield {"type": "cached", "data": cached_result}
                    return
                
                # Process multimodal inputs if present
                if 'image_path' in kwargs:
                    image_data = await self.multimodal_processor.process_image(kwargs['image_path'])
                    yield {"type": "multimodal", "data": image_data}
                
                # Enhanced retrieval
                retrieval_results = await self._enhanced_retrieval(question)
                yield {"type": "retrieval", "data": retrieval_results}
                
                # Generate streaming response
                async for chunk in self._generate_streaming_response(question, retrieval_results):
                    yield chunk
                
            finally:
                active_queries.dec()
    
    async def _enhanced_retrieval(self, query: str) -> List[Dict[str, Any]]:
        """Enhanced retrieval with graph and vector search."""
        # Vector search
        query_embedding = self.embedding_model.encode(query).tolist()
        vector_results = await self.vector_db.search(query_embedding, k=self.config.retrieval_k)
        
        # Graph search (simplified)
        graph_results = await self._graph_search(query)
        
        # Combine and rerank
        combined_results = vector_results + graph_results
        reranked_results = await self._rerank_results(query, combined_results)
        
        return reranked_results[:self.config.rerank_k]
    
    async def _graph_search(self, query: str) -> List[Dict[str, Any]]:
        """Search the knowledge graph."""
        # Simplified graph search - can be enhanced
        return []
    
    async def _rerank_results(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rerank results using cross-encoder."""
        # Simplified reranking - can be enhanced with cross-encoder models
        return sorted(results, key=lambda x: x.get('score', 0), reverse=True)
    
    async def _generate_streaming_response(self, query: str, context: List[Dict[str, Any]]) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate streaming response."""
        # Prepare context
        context_text = "\n".join([item.get('content', '') for item in context])
        
        # Create prompt
        prompt = f"""Based on the following context, answer the question in Vietnamese:

Context:
{context_text}

Question: {query}

Answer:"""
        
        # Generate response
        if hasattr(self.llm, 'generate'):
            # VLLM path
            sampling_params = SamplingParams(
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                max_tokens=self.config.max_tokens,
                stream=True
            )
            
            outputs = self.llm.generate([prompt], sampling_params)
            for output in outputs:
                for token in output.outputs[0].text:
                    yield {"type": "token", "data": token}
        else:
            # Transformers path
            inputs = self.tokenizer(prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    top_p=self.config.top_p,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = response.replace(prompt, "").strip()
            
            # Simulate streaming by chunking
            for i in range(0, len(response), self.config.stream_chunk_size):
                chunk = response[i:i + self.config.stream_chunk_size]
                yield {"type": "chunk", "data": chunk}
    
    async def query(self, role: str, question: str, **kwargs) -> Dict[str, Any]:
        """Standard query method."""
        result = {
            "answer": "",
            "source_documents": [],
            "metadata": {
                "model": self.config.base_model_name,
                "timestamp": datetime.now().isoformat(),
                "processing_time": 0
            }
        }
        
        start_time = datetime.now()
        
        # Collect streaming results
        async for chunk in self.query_stream(role, question, **kwargs):
            if chunk["type"] == "chunk":
                result["answer"] += chunk["data"]
            elif chunk["type"] == "retrieval":
                result["source_documents"] = chunk["data"]
            elif chunk["type"] == "token":
                result["answer"] += chunk["data"]
        
        result["metadata"]["processing_time"] = (datetime.now() - start_time).total_seconds()
        
        # Cache result
        cache_key = f"query:{role}:{hash(question)}"
        await self.cache_manager.set(cache_key, result)
        
        return result

# Factory function
def create_enhanced_rag_pipeline(config: EnhancedRAGConfig = None) -> EnhancedRAGPipeline:
    """Create and return an enhanced RAG pipeline."""
    return EnhancedRAGPipeline(config)