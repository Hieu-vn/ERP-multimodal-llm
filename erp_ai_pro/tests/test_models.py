import pytest
from erp_ai_pro.core.models import SourceDocument, QueryRequest, QueryResponse

def test_source_document_model():
    doc = SourceDocument(page_content="Test content", metadata={"source": "test_file.txt"})
    assert doc.page_content == "Test content"
    assert doc.metadata["source"] == "test_file.txt"

def test_query_request_model():
    req = QueryRequest(role="admin", question="What is the current stock?")
    assert req.role == "admin"
    assert req.question == "What is the current stock?"

def test_query_response_model():
    resp = QueryResponse(
        answer="The stock is 100 units.",
        source_documents=[SourceDocument(page_content="Stock data", metadata={"id": "1"})],
        thought_process=["Thought: ..."]
    )
    assert resp.answer == "The stock is 100 units."
    assert len(resp.source_documents) == 1
    assert resp.source_documents[0].page_content == "Stock data"
    assert resp.thought_process[0] == "Thought: ..."

def test_query_response_model_no_thought_process():
    resp = QueryResponse(
        answer="The stock is 100 units.",
        source_documents=[SourceDocument(page_content="Stock data", metadata={"id": "1"})]
    )
    assert resp.answer == "The stock is 100 units."
    assert resp.thought_process is None
