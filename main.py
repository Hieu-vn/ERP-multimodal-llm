# -*- coding: utf-8 -*-
"""
Main FastAPI application for the ERP AI Pro version.
Exposes the RAG pipeline as a RESTful API.
"""
from fastapi import FastAPI, HTTPException
from erp_ai_core.models import QueryRequest, QueryResponse
from erp_ai_core.rag_pipeline import RAGPipeline
import asyncio

app = FastAPI(
    title="ERP AI Pro Version API",
    description="AI-powered assistant for ERP systems, leveraging Retrieval-Augmented Generation.",
    version="1.0.0"
)

# Initialize the RAG pipeline globally
rag_pipeline = RAGPipeline()

@app.on_event("startup")
async def startup_event():
    """Load the RAG pipeline components on application startup."""
    print("Application startup: Initializing RAG pipeline...")
    try:
        # Run setup in a separate thread to avoid blocking the event loop
        await asyncio.to_thread(rag_pipeline.setup)
        print("RAG pipeline initialized successfully.")
    except Exception as e:
        print(f"Error during RAG pipeline initialization: {e}")
        # Depending on severity, you might want to exit or disable functionality
        raise

@app.post("/query", response_model=QueryResponse)
async def query_erp_ai(request: QueryRequest):
    """Process a natural language query and return an AI-generated answer with source documents."""
    try:
        response = await rag_pipeline.query(role=request.role, question=request.question)
        return QueryResponse(
            answer=response["answer"],
            source_documents=response["source_documents"]
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint to verify API status."""
    return {"status": "ok", "message": "ERP AI Pro Version API is running."}
