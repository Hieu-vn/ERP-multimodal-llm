# -*- coding: utf-8 -*-
"""
Data models for the API using Pydantic.
Ensures type safety and clear API contracts.
"""
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    """Request model for a user query."""
    role: str = Field(..., description="The user's role in the ERP system (e.g., 'warehouse_manager').")
    question: str = Field(..., description="The user's question in natural language.")

class QueryResponse(BaseModel):
    """Response model for a user query."""
    answer: str = Field(..., description="The AI-generated answer.")
    source_documents: list[dict] = Field(..., description="List of source documents retrieved from the knowledge base to generate the answer.")
