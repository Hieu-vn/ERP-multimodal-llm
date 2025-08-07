# -*- coding: utf-8 -*-
"""
Enhanced FastAPI Application for ERP AI Pro - ATOMIC Agent Architecture
Features: Streaming responses, multimodal support, WebSocket, advanced monitoring
"""

import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
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
import structlog

# Import our new main system


from erp_ai_pro.cognitive.main_system import MainSystem
from erp_ai_pro.config.config import SystemConfig
from erp_ai_pro.presentation.models import QueryRequest, QueryResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger()

# Metrics
request_count = Counter('erp_ai_requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('erp_ai_request_duration_seconds', 'Request duration')
active_connections = Gauge('erp_ai_active_connections', 'Active WebSocket connections')
system_health = Gauge('erp_ai_system_health', 'Main system health status')

# Pydantic Models for the API layer
class APIQueryRequest(BaseModel):
    role: str = Field(..., description="User role (e.g., admin, finance_manager)")
    question: str = Field(..., description="The user's question")

class APIQueryResponse(BaseModel):
    response: Dict[str, Any] = Field(..., description="The detailed response from the agent system")
    processing_time: float = Field(..., description="Total processing time in seconds")
    chosen_agent: str = Field(..., description="The agent chosen by the orchestrator")

# Global variables
main_system: Optional[MainSystem] = None

# Lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    global main_system
    logger.info("Starting ERP AI Pro API with ATOMIC architecture...")
    try:
        config = SystemConfig()
        main_system = MainSystem(config)
        await main_system.setup()
        system_health.set(1)
        logger.info("MainSystem initialized successfully.")
        os.makedirs("uploads", exist_ok=True)
        yield
    except Exception as e:
        logger.error(f"Fatal startup error: {e}")
        system_health.set(0)
        raise
    finally:
        logger.info("Shutting down ERP AI Pro API...")
        system_health.set(0)

# Create FastAPI app
app = FastAPI(
    title="ERP AI Pro API - ATOMIC Architecture",
    description="Next-generation AI assistant using a specialized agent architecture.",
    version="3.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(GZipMiddleware, minimum_size=1000)

# --- API Endpoints ---

@app.get("/")
async def root():
    return {"message": "ERP AI Pro API v3.0 - ATOMIC Architecture is running."}

@app.get("/health")
async def health_check():
    system_ready = main_system is not None and main_system.llm is not None
    return {
        "status": "healthy" if system_ready else "degraded",
        "system_ready": system_ready,
        "active_llm": main_system.config.base_model_name if system_ready else None
    }

@app.post("/query/text", response_model=APIQueryResponse)
async def query_text(request: APIQueryRequest):
    """Endpoint for text-based queries."""
    request_count.labels(method='POST', endpoint='/query/text').inc()
    if not main_system:
        raise HTTPException(status_code=503, detail="System not initialized")

    start_time = time.time()
    with request_duration.time():
        response_data = await main_system.query(question=request.question, role=request.role)
    processing_time = time.time() - start_time

    return APIQueryResponse(
        response=response_data,
        processing_time=processing_time,
        chosen_agent=response_data.get("chosen_agent", "unknown") # We need to ensure the agent name is returned
    )

@app.post("/query/multimodal", response_model=APIQueryResponse)
async def query_multimodal(role: str, question: str, file: UploadFile = File(...)):
    """Endpoint for multimodal queries (text + image)."""
    request_count.labels(method='POST', endpoint='/query/multimodal').inc()
    if not main_system:
        raise HTTPException(status_code=503, detail="System not initialized")
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are supported")

    start_time = time.time()
    file_path = None
    try:
        file_path = f"uploads/{file.filename}"
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        with request_duration.time():
            response_data = await main_system.query(question=question, role=role, image_path=file_path)
        
        processing_time = time.time() - start_time

        return APIQueryResponse(
            response=response_data,
            processing_time=processing_time,
            chosen_agent=response_data.get("chosen_agent", "MultimodalAgent")
        )
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

# Simplified WebSocket for demonstration
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if not main_system:
                await websocket.send_json({"error": "System not ready"})
                continue

            response = await main_system.query(question=message.get("question", ""), role=message.get("role", "user"))
            await websocket.send_json(response)
            
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected.")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_json({"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
