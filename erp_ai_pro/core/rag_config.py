# -*- coding: utf-8 -*-
"""
Configuration for the RAG pipeline.
"""
import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class RAGConfig:
    # Path to the source knowledge base file
    knowledge_base_path: str = os.getenv("ERP_KNOWLEDGE_BASE_PATH", "erp_ai_pro/data_preparation/sample_erp_knowledge.json")

    # Path to the persistent ChromaDB vector store
    vector_store_path: str = os.getenv("VECTOR_STORE_PATH", "data_preparation/vector_store")

    # Name of the ChromaDB collection
    collection_name: str = os.getenv("CHROMA_COLLECTION_NAME", "erp_knowledge")

    # Sentence Transformer model for creating embeddings
    embedding_model_name: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

    # Number of search results to retrieve from the vector store
    retrieval_k: int = int(os.getenv("RETRIEVAL_K", 3))

    # --- LLM Configuration ---
    # This section is designed to be compatible with a future Model Registry.
    # The base model identifier from Hugging Face Hub.
    base_model_name: str = os.getenv("BASE_MODEL_NAME", "google/flan-t5-base")

    # The fine-tuned adapter path. This can be a local path or a Hub identifier.
    # In a production MLOps setup, this would be populated by the CI/CD pipeline
    # after a new model is trained and registered.
    # Set to an empty string or None to use the base model only.
    finetuned_model_path: str = os.getenv("FINETUNED_MODEL_PATH", "path/to/your/finetuned_erp_model") # Placeholder path

    # --- Re-ranker Configuration ---
    reranker_model_name: str = os.getenv("RERANKER_MODEL_NAME", "cross-encoder/ms-marco-MiniLM-L-6-v2") # Example re-ranker model

    # --- Neo4j Configuration ---
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_username: str = os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "password")

    # --- Role-Based Access Control (RBAC) Configuration ---
    # Defines which tools are accessible to which user roles.
    # Keys are roles, values are lists of tool names (as strings).
    # If a role is not listed, it will have access to a default set of tools.
    ROLE_TOOL_MAPPING: dict[str, list[str]] = field(default_factory=lambda: {
        "admin": [
            "get_current_date", "vector_search", "graph_erp_lookup", "perform_calculation",
            # Full access to all modules
            "get_product_stock_level", "create_order", "get_order_status", "get_customer_outstanding_balance",
            "get_inventory_overview", "stock_in", "stock_out", "inventory_check", "get_low_stock_alerts",
            "get_revenue_report", "get_expense_report", "get_customer_debt", "create_receipt", "create_payment",
            "create_project", "get_project_details", "update_project_status", "create_task", "assign_task",
            "trigger_workflow", "get_workflow_status", "approve_workflow_step",
            "create_employee", "get_employee_profile", "submit_leave_request", "calculate_payroll", "create_performance_goal",
            "create_lead", "qualify_lead", "create_opportunity", "create_customer_account", "create_support_ticket",
            "auto_create_purchase_order", "auto_generate_report", "auto_data_entry"
        ],
        "finance_manager": [
            "get_current_date", "vector_search", "graph_erp_lookup", "perform_calculation",
            # Finance specific tools
            "get_revenue_report", "get_expense_report", "get_customer_debt", "create_receipt", "create_payment",
            "calculate_payroll", "get_customer_outstanding_balance",
            # General business tools
            "get_project_details", "auto_generate_report"
        ],
        "sales_manager": [
            "get_current_date", "vector_search", "graph_erp_lookup",
            # Sales & CRM tools
            "create_lead", "qualify_lead", "create_opportunity", "create_customer_account", "create_support_ticket",
            "get_product_stock_level", "create_order", "get_order_status", "get_customer_outstanding_balance",
            # Project management for sales projects
            "create_project", "get_project_details", "create_task"
        ],
        "sales_rep": [
            "get_current_date", "vector_search", "graph_erp_lookup",
            # Limited sales tools
            "create_lead", "create_opportunity", "get_customer_outstanding_balance",
            "get_product_stock_level", "get_order_status"
        ],
        "warehouse_manager": [
            "get_current_date", "vector_search", "graph_erp_lookup",
            # Inventory management tools
            "get_product_stock_level", "get_inventory_overview", "stock_in", "stock_out", 
            "inventory_check", "get_low_stock_alerts",
            # Project management for warehouse projects
            "create_project", "get_project_details", "create_task", "assign_task"
        ],
        "inventory_clerk": [
            "get_current_date", "vector_search", "graph_erp_lookup",
            # Basic inventory operations
            "get_product_stock_level", "get_inventory_overview", "stock_in", "stock_out", "inventory_check"
        ],
        "project_manager": [
            "get_current_date", "vector_search", "graph_erp_lookup", "perform_calculation",
            # Full project management access
            "create_project", "get_project_details", "update_project_status", "create_task", "assign_task",
            # Workflow automation
            "trigger_workflow", "get_workflow_status", "approve_workflow_step",
            # Basic resource access
            "get_employee_profile", "auto_generate_report"
        ],
        "hr_manager": [
            "get_current_date", "vector_search", "graph_erp_lookup", "perform_calculation",
            # Full HR access
            "create_employee", "get_employee_profile", "submit_leave_request", "calculate_payroll", "create_performance_goal",
            # Workflow for HR processes
            "trigger_workflow", "get_workflow_status", "approve_workflow_step",
            "auto_generate_report", "auto_data_entry"
        ],
        "hr_specialist": [
            "get_current_date", "vector_search", "graph_erp_lookup",
            # Limited HR access
            "get_employee_profile", "submit_leave_request", "create_performance_goal"
        ],
        "customer_service": [
            "get_current_date", "vector_search", "graph_erp_lookup",
            # Customer support tools
            "create_support_ticket", "get_customer_outstanding_balance", "create_customer_account",
            "get_order_status", "get_product_stock_level"
        ],
        "analyst": [
            "get_current_date", "vector_search", "graph_erp_lookup", "perform_calculation",
            # Read-only access for analysis
            "get_revenue_report", "get_expense_report", "get_project_details",
            "get_employee_profile", "auto_generate_report"
        ],
        "ceo": [
            "get_current_date", "vector_search", "graph_erp_lookup", "perform_calculation",
            # Executive dashboard access
            "get_revenue_report", "get_expense_report", "get_project_details",
            "approve_workflow_step", "auto_generate_report"
        ],
        "default": [
            "get_current_date", "vector_search"
        ]
    })
