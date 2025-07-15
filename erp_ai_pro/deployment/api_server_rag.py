# -*- coding: utf-8 -*-
"""
FastAPI server to expose the RAG-powered ERP assistant.
This represents the professional, production-ready entry point for the AI service.
"""
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from fastapi import FastAPI, HTTPException, Depends
from erp_ai_pro.core.models import QueryRequest, QueryResponse
from erp_ai_pro.core.rag_pipeline import RAGPipeline

# --- Application Setup ---
app = FastAPI(
    title="ERP AI Pro Assistant API",
    description="An AI assistant for ERP systems, powered by a state-of-the-art RAG pipeline.",
    version="1.0.0"
)

# --- Singleton Pattern for RAG Pipeline ---
# This ensures that the heavy models are loaded only once during the application's lifecycle.
class PipelineSingleton:
    _instance: RAGPipeline = None

    @classmethod
    def get_instance(cls) -> RAGPipeline:
        if cls._instance is None:
            print("Initializing RAGPipeline instance for the first time.")
            cls._instance = RAGPipeline()
            cls._instance.setup()  # Load models and data
        return cls._instance

def get_pipeline() -> RAGPipeline:
    """Dependency injector for the RAG pipeline."""
    return PipelineSingleton.get_instance()


@app.on_event("startup")
def startup_event():
    """Actions to perform on application startup."""
    print("Server starting up... Triggering initial pipeline loading.")
    # This will pre-load the model on startup instead of waiting for the first request.
    get_pipeline()
    print("Startup complete. Pipeline is ready.")

@app.get("/health", tags=["Monitoring"])
def health_check():
    """Health check endpoint to verify if the server is running."""
    return {"status": "ok", "pipeline_ready": PipelineSingleton._instance is not None}

@app.post("/query", tags=["AI Assistant"], response_model=QueryResponse)
async def handle_query(request: QueryRequest, pipeline: RAGPipeline = Depends(get_pipeline)):
    """
    Receives a user query and returns a RAG-powered answer.
    This endpoint uses FastAPI's dependency injection for clean, testable code.
    """
    if not pipeline:
        raise HTTPException(status_code=503, detail="RAG pipeline is not available.")

    print(f"Received query for role '{request.role}': '{request.question}'")

    try:
        result = await pipeline.query(role=request.role, question=request.question)
        return QueryResponse(answer=result['answer'], source_documents=[doc['metadata'] for doc in result['source_documents']])
    except Exception as e:
        print(f"An error occurred during query processing: {e}")
        raise HTTPException(status_code=500, detail="An error occurred in the RAG pipeline.")

# To run this server:
# uvicorn deployment.api_server_rag:app --reload --host 0.0.0.0 --port 8000