# -*- coding: utf-8 -*-
"""
Enhanced FastAPI Application for ERP AI Pro
Features: Streaming responses, multimodal support, WebSocket, advanced monitoring
"""

import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional, AsyncGenerator
import time
import aiofiles
from pathlib import Path

# FastAPI Enhanced
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, File, UploadFile, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.websockets import WebSocketState

# Monitoring
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from prometheus_client.exposition import CONTENT_TYPE_LATEST
import structlog

# Import our enhanced pipeline
import sys
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from erp_ai_pro.core.enhanced_rag_pipeline import EnhancedRAGPipeline, EnhancedRAGConfig
from erp_ai_pro.core.models import QueryRequest, QueryResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger()

# Metrics
request_count = Counter('erp_ai_requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('erp_ai_request_duration_seconds', 'Request duration')
active_connections = Gauge('erp_ai_active_connections', 'Active WebSocket connections')
pipeline_health = Gauge('erp_ai_pipeline_health', 'Pipeline health status')

# Pydantic Models
class EnhancedQueryRequest(BaseModel):
    role: str = Field(..., description="User role (admin, finance_manager, etc.)")
    question: str = Field(..., description="The question to ask")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    stream: bool = Field(False, description="Enable streaming response")
    include_sources: bool = Field(True, description="Include source documents")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens in response")
    temperature: Optional[float] = Field(None, description="Temperature for generation")

class MultimodalQueryRequest(BaseModel):
    role: str = Field(..., description="User role")
    question: str = Field(..., description="The question to ask")
    image_description: Optional[str] = Field(None, description="Description of uploaded image")
    stream: bool = Field(False, description="Enable streaming response")

class EnhancedQueryResponse(BaseModel):
    answer: str = Field(..., description="The AI's answer")
    source_documents: List[Dict[str, Any]] = Field(default=[], description="Source documents")
    metadata: Dict[str, Any] = Field(default={}, description="Response metadata")
    processing_time: float = Field(..., description="Processing time in seconds")
    model_info: Dict[str, Any] = Field(default={}, description="Model information")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Health status")
    pipeline_ready: bool = Field(..., description="Pipeline readiness")
    services: Dict[str, str] = Field(default={}, description="Service statuses")
    metrics: Dict[str, Any] = Field(default={}, description="System metrics")

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        active_connections.inc()
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            active_connections.dec()
            logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            if connection.client_state == WebSocketState.CONNECTED:
                await connection.send_text(message)

# Global variables
rag_pipeline: Optional[EnhancedRAGPipeline] = None
connection_manager = ConnectionManager()

# Lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    global rag_pipeline
    
    # Startup
    logger.info("Starting Enhanced ERP AI Pro API...")
    
    try:
        # Initialize pipeline
        config = EnhancedRAGConfig()
        rag_pipeline = EnhancedRAGPipeline(config)
        await rag_pipeline.setup()
        
        pipeline_health.set(1)
        logger.info("Pipeline initialized successfully")
        
        # Create upload directory
        os.makedirs("uploads", exist_ok=True)
        
        yield
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        pipeline_health.set(0)
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down Enhanced ERP AI Pro API...")
        pipeline_health.set(0)

# Create FastAPI app
app = FastAPI(
    title="Enhanced ERP AI Pro API",
    description="Next-generation AI assistant with multimodal support and streaming",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Create static file directory
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Utility functions
def get_client_ip(request):
    """Get client IP address."""
    x_forwarded_for = request.headers.get('x-forwarded-for')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.client.host

async def save_upload_file(upload_file: UploadFile, destination: Path):
    """Save uploaded file asynchronously."""
    async with aiofiles.open(destination, 'wb') as f:
        content = await upload_file.read()
        await f.write(content)

# Routes

@app.get("/", response_class=JSONResponse)
async def root():
    """Root endpoint."""
    request_count.labels(method='GET', endpoint='/').inc()
    return {
        "message": "Enhanced ERP AI Pro API v2.0",
        "features": [
            "Llama-3.1 Integration",
            "Multimodal Support",
            "Streaming Responses",
            "GraphRAG",
            "Advanced Caching",
            "WebSocket Support"
        ],
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Enhanced health check endpoint."""
    request_count.labels(method='GET', endpoint='/health').inc()
    
    # Check pipeline health
    pipeline_ready = rag_pipeline is not None and hasattr(rag_pipeline, 'llm')
    
    # Check services
    services = {
        "pipeline": "healthy" if pipeline_ready else "unhealthy",
        "vector_db": "healthy",  # Add actual checks
        "cache": "healthy",      # Add actual checks
        "graph_db": "healthy"    # Add actual checks
    }
    
    # System metrics
    metrics = {
        "active_connections": len(connection_manager.active_connections),
        "pipeline_health": pipeline_health._value.get(),
        "request_count": request_count._value.sum(),
    }
    
    return HealthResponse(
        status="healthy" if pipeline_ready else "degraded",
        pipeline_ready=pipeline_ready,
        services=services,
        metrics=metrics
    )

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest()

@app.post("/query", response_model=EnhancedQueryResponse)
async def query_enhanced(request: EnhancedQueryRequest):
    """Enhanced query endpoint with improved features."""
    request_count.labels(method='POST', endpoint='/query').inc()
    
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    start_time = time.time()
    
    try:
        with request_duration.time():
            # Prepare query parameters
            query_params = {}
            if request.max_tokens:
                query_params['max_tokens'] = request.max_tokens
            if request.temperature:
                query_params['temperature'] = request.temperature
            
            # Execute query
            response = await rag_pipeline.query(
                role=request.role,
                question=request.question,
                **query_params
            )
            
            processing_time = time.time() - start_time
            
            return EnhancedQueryResponse(
                answer=response["answer"],
                source_documents=response.get("source_documents", []) if request.include_sources else [],
                metadata=response.get("metadata", {}),
                processing_time=processing_time,
                model_info={
                    "model": rag_pipeline.config.base_model_name,
                    "version": "2.0.0",
                    "features": ["multimodal", "streaming", "graphrag"]
                }
            )
            
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/stream")
async def query_stream(request: EnhancedQueryRequest):
    """Streaming query endpoint."""
    request_count.labels(method='POST', endpoint='/query/stream').inc()
    
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    async def generate_stream():
        try:
            async for chunk in rag_pipeline.query_stream(
                role=request.role,
                question=request.question
            ):
                yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:
            error_chunk = {"type": "error", "data": str(e)}
            yield f"data: {json.dumps(error_chunk)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/query/multimodal", response_model=EnhancedQueryResponse)
async def query_multimodal(
    role: str,
    question: str,
    file: UploadFile = File(...),
    stream: bool = False
):
    """Multimodal query endpoint for image + text."""
    request_count.labels(method='POST', endpoint='/query/multimodal').inc()
    
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are supported")
    
    start_time = time.time()
    
    try:
        # Save uploaded file
        file_path = f"uploads/{file.filename}"
        await save_upload_file(file, Path(file_path))
        
        # Process query with image
        response = await rag_pipeline.query(
            role=role,
            question=question,
            image_path=file_path
        )
        
        processing_time = time.time() - start_time
        
        return EnhancedQueryResponse(
            answer=response["answer"],
            source_documents=response.get("source_documents", []),
            metadata=response.get("metadata", {}),
            processing_time=processing_time,
            model_info={
                "model": rag_pipeline.config.base_model_name,
                "multimodal": True,
                "image_processed": True
            }
        )
        
    except Exception as e:
        logger.error(f"Multimodal query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    await connection_manager.connect(websocket)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "query":
                # Handle query via WebSocket
                try:
                    if not rag_pipeline:
                        await connection_manager.send_personal_message(
                            json.dumps({"type": "error", "message": "Pipeline not ready"}),
                            websocket
                        )
                        continue
                    
                    # Send streaming response
                    async for chunk in rag_pipeline.query_stream(
                        role=message.get("role", "user"),
                        question=message.get("question", "")
                    ):
                        if websocket.client_state == WebSocketState.CONNECTED:
                            await connection_manager.send_personal_message(
                                json.dumps(chunk),
                                websocket
                            )
                        else:
                            break
                            
                except Exception as e:
                    await connection_manager.send_personal_message(
                        json.dumps({"type": "error", "message": str(e)}),
                        websocket
                    )
            
            elif message.get("type") == "ping":
                await connection_manager.send_personal_message(
                    json.dumps({"type": "pong"}),
                    websocket
                )
                
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        connection_manager.disconnect(websocket)

@app.post("/admin/reload")
async def reload_pipeline():
    """Admin endpoint to reload the pipeline."""
    global rag_pipeline
    
    try:
        config = EnhancedRAGConfig()
        rag_pipeline = EnhancedRAGPipeline(config)
        await rag_pipeline.setup()
        
        pipeline_health.set(1)
        return {"message": "Pipeline reloaded successfully"}
        
    except Exception as e:
        logger.error(f"Pipeline reload error: {e}")
        pipeline_health.set(0)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/stats")
async def get_stats():
    """Admin endpoint for system statistics."""
    return {
        "active_connections": len(connection_manager.active_connections),
        "pipeline_health": pipeline_health._value.get(),
        "total_requests": request_count._value.sum(),
        "model_info": {
            "model": rag_pipeline.config.base_model_name if rag_pipeline else "Not loaded",
            "features": ["multimodal", "streaming", "graphrag", "caching"]
        }
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "enhanced_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        access_log=True
    )