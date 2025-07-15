# -*- coding: utf-8 -*-
"""
Modern FastAPI Application for ERP AI Pro
Clean, fast, and efficient - no bloat
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any
import time

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Our modern pipeline
from erp_ai_pro.core.modern_rag_pipeline import modern_rag_pipeline
from erp_ai_pro.core.models import QueryRequest, QueryResponse

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request/Response models
class ModernQueryRequest(BaseModel):
    role: str = Field(..., description="User role (admin, finance_manager, etc.)")
    question: str = Field(..., description="The question to ask")
    stream: bool = Field(False, description="Enable streaming response")

class ModernQueryResponse(BaseModel):
    answer: str = Field(..., description="The AI's answer")
    context: str = Field(default="", description="Retrieved context")
    image_analysis: Optional[str] = Field(None, description="Image analysis if provided")
    processing_time: float = Field(..., description="Processing time in seconds")
    model: str = Field(..., description="Model used")
    timestamp: str = Field(..., description="Response timestamp")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Health status")
    pipeline_ready: bool = Field(..., description="Pipeline readiness")
    metrics: Dict[str, Any] = Field(default={}, description="System metrics")

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting Modern ERP AI Pro API...")
    
    try:
        # Initialize pipeline
        await modern_rag_pipeline.setup()
        logger.info("Modern RAG pipeline initialized successfully")
        
        # Create upload directory
        os.makedirs("uploads", exist_ok=True)
        
        yield
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    
    finally:
        logger.info("Shutting down Modern ERP AI Pro API...")

# Create FastAPI app
app = FastAPI(
    title="Modern ERP AI Pro API",
    description="Clean, fast, and efficient AI assistant for ERP systems",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Modern ERP AI Pro API v2.0",
        "features": [
            "Llama-3.1 8B Integration",
            "Multimodal Support",
            "Streaming Responses",
            "Advanced Caching",
            "Business Intelligence"
        ],
        "status": "ready"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    metrics = modern_rag_pipeline.get_metrics()
    
    return HealthResponse(
        status="healthy" if metrics["model_loaded"] else "degraded",
        pipeline_ready=metrics["model_loaded"],
        metrics=metrics
    )

@app.post("/query", response_model=ModernQueryResponse)
async def query_modern(request: ModernQueryRequest):
    """Modern query endpoint"""
    try:
        result = await modern_rag_pipeline.query(
            role=request.role,
            question=request.question
        )
        
        return ModernQueryResponse(
            answer=result["answer"],
            context=result.get("context", ""),
            image_analysis=result.get("image_analysis"),
            processing_time=result["processing_time"],
            model=result["model"],
            timestamp=result["timestamp"]
        )
        
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/stream")
async def query_stream(request: ModernQueryRequest):
    """Streaming query endpoint"""
    if not request.stream:
        # Fallback to regular query
        return await query_modern(request)
    
    async def generate_stream():
        try:
            async for chunk in modern_rag_pipeline.query_stream(
                role=request.role,
                question=request.question
            ):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: {{\"type\": \"error\", \"data\": \"{str(e)}\"}}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )

@app.post("/query/multimodal")
async def query_multimodal(
    role: str,
    question: str,
    file: UploadFile = File(...),
    stream: bool = False
):
    """Multimodal query endpoint"""
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are supported")
    
    try:
        # Save uploaded file
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process query with image
        result = await modern_rag_pipeline.query(
            role=role,
            question=question,
            image_path=file_path
        )
        
        return ModernQueryResponse(
            answer=result["answer"],
            context=result.get("context", ""),
            image_analysis=result.get("image_analysis"),
            processing_time=result["processing_time"],
            model=result["model"],
            timestamp=result["timestamp"]
        )
        
    except Exception as e:
        logger.error(f"Multimodal query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/documents/add")
async def add_document(
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
    background_tasks: BackgroundTasks = None
):
    """Add document to knowledge base"""
    try:
        if background_tasks:
            background_tasks.add_task(
                modern_rag_pipeline.add_document,
                content,
                metadata
            )
            return {"message": "Document queued for processing"}
        else:
            await modern_rag_pipeline.add_document(content, metadata)
            return {"message": "Document added successfully"}
            
    except Exception as e:
        logger.error(f"Add document error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analytics/business")
async def analyze_business_data(data: Dict[str, Any]):
    """Business intelligence analysis"""
    try:
        insights = await modern_rag_pipeline.analyze_business_data(data)
        return {"insights": insights}
        
    except Exception as e:
        logger.error(f"Business analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics():
    """Get pipeline metrics"""
    return modern_rag_pipeline.get_metrics()

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
        "main_modern:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )