# ERP AI Pro Version - API Documentation

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Main API Endpoints](#main-api-endpoints)
4. [Core Components](#core-components)
5. [Agent Functions](#agent-functions)
6. [Data Models](#data-models)
7. [Tools and Utilities](#tools-and-utilities)
8. [Configuration](#configuration)
9. [Data Ingestion](#data-ingestion)
10. [Vector Store Management](#vector-store-management)
11. [Fine-tuning](#fine-tuning)
12. [Graph Management](#graph-management)
13. [Setup and Deployment](#setup-and-deployment)
14. [Examples](#examples)

## Overview

The ERP AI Pro Version is an advanced AI-powered assistant for ERP (Enterprise Resource Planning) systems. It leverages Retrieval-Augmented Generation (RAG) technology, combining vector search, graph databases, and language models to provide intelligent responses to business queries.

### Key Features
- **Multi-modal Knowledge Base**: Combines vector search with Neo4j graph database
- **Role-based Access Control**: Different access levels for different user roles
- **Specialized Agents**: Dedicated functionality for Sales, Inventory, and Finance
- **RESTful API**: FastAPI-based web service
- **Model Fine-tuning**: Support for custom model training
- **Scalable Architecture**: Production-ready deployment configuration

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   RAG Pipeline  │    │   Knowledge     │
│   Web Server    │───▶│   Core Engine   │───▶│   Base          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Agent Tools   │    │   Vector Store  │    │   Neo4j Graph   │
│   (Sales/Inv/   │    │   (ChromaDB)    │    │   Database      │
│   Finance)      │    └─────────────────┘    └─────────────────┘
└─────────────────┘
```

## Main API Endpoints

### Primary Application (`main.py`)

#### Base Configuration
- **Title**: ERP AI Pro Version API
- **Description**: AI-powered assistant for ERP systems, leveraging Retrieval-Augmented Generation
- **Version**: 1.0.0

#### Endpoints

##### POST `/query`
Process a natural language query and return an AI-generated answer with source documents.

**Request Model**: `QueryRequest`
```json
{
  "role": "warehouse_manager",
  "question": "What is the current stock level for Product ABC?"
}
```

**Response Model**: `QueryResponse`
```json
{
  "answer": "Product ABC currently has 150 units in stock...",
  "source_documents": [
    {
      "page_content": "Product ABC inventory data...",
      "metadata": {"source": "inventory_db", "role": "warehouse_manager"}
    }
  ],
  "thought_process": ["Searching inventory database...", "Found product ABC..."]
}
```

**Usage Example**:
```python
import requests

response = requests.post("http://localhost:8000/query", json={
    "role": "sales_rep", 
    "question": "Show me outstanding orders for customer XYZ"
})
print(response.json())
```

##### GET `/health`
Health check endpoint to verify API status.

**Response**:
```json
{
  "status": "ok",
  "message": "ERP AI Pro Version API is running."
}
```

### Deployment API Server (`deployment/api_server_rag.py`)

Alternative production-ready server with enhanced features:

#### Enhanced Features
- **Singleton Pattern**: Ensures models are loaded only once
- **Dependency Injection**: Clean, testable architecture
- **Startup Pre-loading**: Models loaded on server startup

#### Endpoints

##### GET `/health`
Enhanced health check with pipeline status.

**Response**:
```json
{
  "status": "ok",
  "pipeline_ready": true
}
```

##### POST `/query`
Enhanced query endpoint with dependency injection.

## Core Components

### RAG Pipeline (`erp_ai_core/rag_pipeline.py`)

The core orchestration engine that combines retrieval, prompt formatting, and language model generation.

#### Class: `RAGPipeline`

##### `__init__()`
Initialize the RAG pipeline with configuration.

```python
from erp_ai_core.rag_pipeline import RAGPipeline

pipeline = RAGPipeline()
```

##### `setup()`
Load and initialize all pipeline components.

```python
pipeline.setup()  # Loads models, vector store, and tools
```

##### `async query(role: str, question: str) -> dict`
Process a user query with role-based access control.

**Parameters**:
- `role` (str): User role (e.g., "sales_rep", "warehouse_manager", "admin")
- `question` (str): Natural language question

**Returns**: Dictionary with:
- `answer` (str): AI-generated response
- `source_documents` (list): Retrieved source documents
- `thought_process` (list): Step-by-step reasoning

**Example**:
```python
result = await pipeline.query(
    role="warehouse_manager",
    question="What products are running low on stock?"
)
print(result["answer"])
```

#### Configuration
The pipeline uses `RAGConfig` for configuration management:

```python
from config.rag_config import RAGConfig

config = RAGConfig()
# Customize configuration
config.retrieval_k = 5  # Retrieve top 5 documents
config.embedding_model_name = "all-MiniLM-L6-v2"
```

## Agent Functions

### Sales Agent (`erp_ai_core/agent_sales.py`)

Handles sales-related operations and customer management.

#### Functions

##### `get_product_stock_level(product_id: str) -> Dict[str, Any]`
Check product inventory levels.

**Parameters**:
- `product_id` (str): Unique product identifier

**Returns**: 
```python
{
    "success": True,
    "data": {
        "product_id": "ABC123",
        "stock_level": 150,
        "unit": "pieces"
    }
}
```

**Example**:
```python
from erp_ai_core.agent_sales import get_product_stock_level

result = get_product_stock_level("PROD001")
if result["success"]:
    stock = result["data"]["stock_level"]
    print(f"Current stock: {stock}")
```

##### `create_order(order_data: Dict[str, Any]) -> Dict[str, Any]`
Create a new sales order.

**Parameters**:
- `order_data` (dict): Order information

**Example**:
```python
order_data = {
    "customer_id": "CUST001",
    "products": [
        {"product_id": "PROD001", "quantity": 10, "price": 25.00}
    ],
    "total": 250.00
}

result = create_order(order_data)
```

##### `get_order_status(order_id: str) -> Dict[str, Any]`
Check order status and tracking information.

##### `get_customer_outstanding_balance(customer_id: str) -> Dict[str, Any]`
Retrieve customer outstanding balance and payment history.

### Inventory Agent (`erp_ai_core/agent_inventory.py`)

Manages inventory operations and warehouse functions.

#### Functions

##### `get_inventory_overview() -> Dict[str, Any]`
Get comprehensive inventory summary.

**Returns**:
```python
{
    "success": True,
    "data": {
        "total_products": 500,
        "low_stock_items": 15,
        "total_value": 125000.00
    }
}
```

##### `stock_in(stock_data: Dict[str, Any]) -> Dict[str, Any]`
Record incoming inventory.

**Example**:
```python
stock_data = {
    "product_id": "PROD001",
    "quantity": 100,
    "unit_cost": 20.00,
    "supplier": "SUP001"
}

result = stock_in(stock_data)
```

##### `stock_out(stock_data: Dict[str, Any]) -> Dict[str, Any]`
Record outgoing inventory.

##### `inventory_check() -> Dict[str, Any]`
Perform inventory reconciliation.

##### `get_low_stock_alerts() -> Dict[str, Any]`
Get list of products below minimum stock levels.

### Finance Agent (`erp_ai_core/agent_finance.py`)

Handles financial operations and reporting.

#### Functions

##### `get_revenue_report(params: Dict[str, Any]) -> Dict[str, Any]`
Generate revenue reports with filtering.

**Parameters**:
```python
params = {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "channel": "online",
    "region": "north"
}
```

##### `get_expense_report(params: Dict[str, Any]) -> Dict[str, Any]`
Generate expense reports and analysis.

##### `get_customer_debt(customer_id: str) -> Dict[str, Any]`
Check customer debt and payment history.

##### `create_receipt(receipt_data: Dict[str, Any]) -> Dict[str, Any]`
Create payment receipts.

##### `create_payment(payment_data: Dict[str, Any]) -> Dict[str, Any]`
Process payment transactions.

## Data Models

### Core Models (`erp_ai_core/models.py`)

#### `SourceDocument`
Represents a source document from the knowledge base.

```python
from erp_ai_core.models import SourceDocument

doc = SourceDocument(
    page_content="Product ABC has 150 units in stock",
    metadata={"source": "inventory", "last_updated": "2024-01-15"}
)
```

#### `QueryRequest`
Request model for user queries.

**Fields**:
- `role` (str, required): User's role in the ERP system
- `question` (str, required): Natural language question

```python
from erp_ai_core.models import QueryRequest

request = QueryRequest(
    role="warehouse_manager",
    question="What products need restocking?"
)
```

#### `QueryResponse`
Response model containing AI-generated answers.

**Fields**:
- `answer` (str): AI-generated response
- `source_documents` (List[SourceDocument]): Retrieved documents
- `thought_process` (List[str], optional): Reasoning steps

## Tools and Utilities

### Core Tools (`erp_ai_core/tools.py`)

#### `get_current_date(query: str) -> str`
Get current date in YYYY-MM-DD format.

**Usage**:
```python
from erp_ai_core.tools import get_current_date

date = get_current_date("What's today's date?")
print(date)  # "2024-01-15"
```

#### `graph_erp_lookup(question: str, role: str, llm_model) -> str`
Query the Neo4j knowledge graph with natural language.

**Example**:
```python
result = graph_erp_lookup(
    question="Show me all orders for customer ABC",
    role="sales_rep",
    llm_model=llm
)
```

#### Class: `VectorSearchTool`
Search the vector knowledge base.

```python
from erp_ai_core.tools import VectorSearchTool

search_tool = VectorSearchTool(vector_store, retrieval_k=5)
results = search_tool.vector_search(
    query="inventory procedures",
    role="warehouse_manager"
)
```

#### Class: `LiveERP_APITool`
Interface with live ERP systems.

#### Class: `DataAnalysisTool`
Perform mathematical calculations and data analysis.

```python
from erp_ai_core.tools import DataAnalysisTool

calc_tool = DataAnalysisTool()
result = calc_tool.perform_calculation("150 * 25.50")
```

## Configuration

### RAG Configuration (`config/rag_config.py`)

#### Class: `RAGConfig`
Central configuration management for the RAG pipeline.

**Key Parameters**:

##### Knowledge Base
- `knowledge_base_path`: Path to source knowledge file
- `vector_store_path`: ChromaDB storage location
- `collection_name`: Vector collection identifier

##### Models
- `embedding_model_name`: Sentence transformer model
- `base_model_name`: Base LLM model
- `finetuned_model_path`: Custom fine-tuned model
- `reranker_model_name`: Re-ranking model

##### Database
- `neo4j_uri`: Neo4j connection string
- `neo4j_username`: Database username
- `neo4j_password`: Database password

##### Access Control
- `ROLE_TOOL_MAPPING`: Role-based tool access

**Example**:
```python
from config.rag_config import RAGConfig

config = RAGConfig()
config.retrieval_k = 3
config.embedding_model_name = "all-MiniLM-L6-v2"

# Role-based access
admin_tools = config.ROLE_TOOL_MAPPING["admin"]
```

### Environment Variables
Create a `.env` file for configuration:

```bash
# Knowledge Base
ERP_KNOWLEDGE_BASE_PATH=data_preparation/sample_erp_knowledge.json
VECTOR_STORE_PATH=data_preparation/vector_store
CHROMA_COLLECTION_NAME=erp_knowledge

# Models
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
BASE_MODEL_NAME=google/flan-t5-base
RETRIEVAL_K=3

# Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

# API
ERP_API_BASE_URL=http://localhost:9000/api
ERP_API_TOKEN=demo-token
```

## Data Ingestion

### ETL Pipeline (`data_ingestion/etl_erp_data.py`)

Extracts, transforms, and loads ERP data from CSV files.

#### Key Functions

##### `extract_data(file_path: str) -> pd.DataFrame`
Extract data from CSV files.

```python
from data_ingestion.etl_erp_data import extract_data

customers_df = extract_data("path/to/customers.csv")
```

##### `transform_customers(df_customers: pd.DataFrame)`
Transform customer data with validation and cleaning.

##### `transform_products(df_products: pd.DataFrame)`
Transform product data with pricing and inventory information.

##### `transform_employees(df_employees: pd.DataFrame)`
Transform employee data with role and department mapping.

##### `run_etl()`
Execute the complete ETL pipeline.

```python
from data_ingestion.etl_erp_data import run_etl

# Process all CSV files and prepare data
run_etl()
```

#### Configuration (`data_ingestion/config.py`)
Set file paths for data sources:

```python
BASE_DIR = "/path/to/data"
CUSTOMER_CSV = os.path.join(BASE_DIR, "customers.csv")
PRODUCT_CSV = os.path.join(BASE_DIR, "products.csv")
ORDER_CSV = os.path.join(BASE_DIR, "orders.csv")
EMPLOYEE_CSV = os.path.join(BASE_DIR, "employees.csv")
```

## Vector Store Management

### Vector Store Creation (`run_create_vector_store.py`)

Creates and persists the ChromaDB vector store from the knowledge base.

#### Function: `create_vector_store()`
Set up the vector database for semantic search.

**Usage**:
```bash
python run_create_vector_store.py
```

**Process**:
1. Load knowledge base JSON file
2. Convert to LangChain Document format
3. Generate embeddings using sentence transformers
4. Create and persist ChromaDB collection

**Example programmatic usage**:
```python
from run_create_vector_store import create_vector_store

# Creates vector store from configured knowledge base
create_vector_store()
```

## Fine-tuning

### Model Fine-tuning (`finetuning/finetune_with_unsloth.py`)

Advanced model fine-tuning capabilities using Unsloth for efficient training.

#### Class: `FinetuneConfig`
Configuration for fine-tuning parameters.

```python
from finetuning.finetune_with_unsloth import FinetuneConfig

config = FinetuneConfig(
    model_name="unsloth/Meta-Llama-3.1-8B-bnb-4bit",
    max_seq_length=2048,
    lora_r=16,
    lora_alpha=16
)
```

#### Class: `ERPModelFinetuner`
Main fine-tuning orchestrator.

##### Key Methods

##### `load_model_and_tokenizer()`
Load base model with LoRA configuration.

```python
finetuner = ERPModelFinetuner(config)
model, tokenizer = finetuner.load_model_and_tokenizer()
```

##### `load_dataset(dataset_path: str) -> Dataset`
Load training dataset from JSON/CSV.

##### `train(train_dataset, eval_dataset=None)`
Execute the training process.

```python
# Complete fine-tuning workflow
finetuner.setup_google_drive()  # If using Colab
train_dataset = finetuner.load_dataset("training_data.json")
finetuner.train(train_dataset)
finetuner.save_model("./fine_tuned_model")
```

##### `push_to_hub(repo_name: str, token: str)`
Upload trained model to Hugging Face Hub.

## Graph Management

### Neo4j Integration (`erp_ai_core/graph_management.py`)

Manages connections and queries to the Neo4j knowledge graph.

#### Graph Schema
```cypher
Nodes:
- Product {name: STRING, stock: INTEGER, price: FLOAT}
- Customer {name: STRING, industry: STRING, role: STRING}
- Order {order_id: STRING, date: DATE, total: FLOAT}
- Employee {name: STRING, department: STRING, role: STRING}

Relationships:
- (Customer)-[:PLACED]->(Order)
- (Order)-[:CONTAINS]->(Product)
- (Employee)-[:MANAGES]->(Employee)
```

#### Class: `Neo4jConnection`
Database connection manager.

```python
from erp_ai_core.graph_management import Neo4jConnection

conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "password")
result = conn.query("MATCH (p:Product) RETURN p.name, p.stock")
conn.close()
```

#### Function: `get_cypher_generation_chain(llm)`
Create LLM chain for natural language to Cypher conversion.

```python
cypher_chain = get_cypher_generation_chain(llm_model)
cypher_query = cypher_chain.invoke({
    "question": "Show me all products with low stock",
    "role": "warehouse_manager"
})
```

## Setup and Deployment

### Installation

1. **Install Dependencies**:
```bash
pip install -r requirements.pro.txt
```

2. **Setup Environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Initialize Vector Store**:
```bash
python run_create_vector_store.py
```

4. **Start Neo4j Database**:
```bash
docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j
```

### Running the Application

#### Development Server
```bash
# Main application
python main.py

# Or using uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Production Server
```bash
uvicorn deployment.api_server_rag:app --host 0.0.0.0 --port 8000 --workers 4
```

### Infrastructure (`infrastructure/main.tf`)

Terraform configuration for cloud deployment (AWS/GCP/Azure).

## Examples

### Complete Workflow Example

```python
import asyncio
from erp_ai_core.rag_pipeline import RAGPipeline
from erp_ai_core.models import QueryRequest, QueryResponse

async def main():
    # Initialize the pipeline
    pipeline = RAGPipeline()
    pipeline.setup()
    
    # Process queries
    queries = [
        {"role": "sales_rep", "question": "What are our top-selling products?"},
        {"role": "warehouse_manager", "question": "Which products need restocking?"},
        {"role": "finance_manager", "question": "Show me this month's revenue report"}
    ]
    
    for query in queries:
        result = await pipeline.query(
            role=query["role"],
            question=query["question"]
        )
        print(f"Q: {query['question']}")
        print(f"A: {result['answer']}")
        print("---")

if __name__ == "__main__":
    asyncio.run(main())
```

### API Client Example

```python
import requests
import json

class ERPAIClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def query(self, role, question):
        response = requests.post(
            f"{self.base_url}/query",
            json={"role": role, "question": question}
        )
        return response.json()
    
    def health_check(self):
        response = requests.get(f"{self.base_url}/health")
        return response.json()

# Usage
client = ERPAIClient()

# Check system health
health = client.health_check()
print(f"System status: {health['status']}")

# Query the system
result = client.query(
    role="warehouse_manager",
    question="What's the current stock level for Product XYZ?"
)
print(f"Answer: {result['answer']}")
```

### Custom Tool Development

```python
from langchain.tools import tool
from typing import Dict, Any

@tool
def custom_erp_function(query: str, parameters: Dict[str, Any]) -> str:
    """
    Custom ERP function for specific business logic.
    Add your domain-specific functionality here.
    """
    # Implement your custom logic
    result = perform_custom_operation(parameters)
    return f"Custom operation result: {result}"

# Register with the pipeline
from erp_ai_core.rag_pipeline import RAGPipeline

pipeline = RAGPipeline()
pipeline.register_custom_tool(custom_erp_function)
```

### Role-based Query Examples

```python
# Sales Representative queries
sales_queries = [
    "Show me all orders for customer ABC Corp",
    "What's the outstanding balance for customer XYZ?",
    "List all products with their current prices"
]

# Warehouse Manager queries
warehouse_queries = [
    "Which products are below minimum stock levels?",
    "Show me today's incoming shipments",
    "Generate an inventory report for the past week"
]

# Finance Manager queries
finance_queries = [
    "What's our revenue for this quarter?",
    "Show me the expense breakdown by department",
    "List all overdue invoices"
]

# Process role-specific queries
for role, queries in [
    ("sales_rep", sales_queries),
    ("warehouse_manager", warehouse_queries),
    ("finance_manager", finance_queries)
]:
    print(f"\n=== {role.title()} Queries ===")
    for question in queries:
        result = await pipeline.query(role=role, question=question)
        print(f"Q: {question}")
        print(f"A: {result['answer'][:100]}...")
```

---

## Support and Contributing

### Error Handling
All functions return standardized error responses:

```python
{
    "success": False,
    "error": "Description of the error",
    "error_code": "ERROR_TYPE"
}
```

### Logging
The system uses Python's logging module. Configure log levels in your environment:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Performance Monitoring
Monitor API performance and model inference times:

```python
# Enable timing logs in RAG pipeline
config.enable_timing_logs = True
```

For production deployments, consider integrating with monitoring tools like Prometheus, Grafana, or cloud-native monitoring services.

---

This documentation covers all public APIs, functions, and components in the ERP AI Pro Version system. For additional support or customization requirements, refer to the source code comments and configuration files.