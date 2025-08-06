# -*- coding: utf-8 -*-
"""
Role-Based Access Control (RBAC) for ERP AI Pro
This file defines the mapping between user roles and the tools they are allowed to access.
"""

# Defines which tools are accessible to which user roles.
# Keys are roles, values are lists of tool names (as strings).
# If a role is not listed, it will have access to a default set of tools.
ROLE_TOOL_MAPPING: dict[str, list[str]] = {
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
}

def get_allowed_tools_for_role(role: str) -> list[str]:
    """
    Returns the list of allowed tool names for a given user role.
    Falls back to the 'default' role if the specific role is not found.
    """
    return ROLE_TOOL_MAPPING.get(role, ROLE_TOOL_MAPPING.get("default", []))
