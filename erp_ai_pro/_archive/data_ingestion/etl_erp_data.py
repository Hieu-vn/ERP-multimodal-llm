# etl_erp_data.py
import pandas as pd
import uuid
from datetime import datetime
import os
import sys

# Add the parent directory to sys.path to allow importing config
# This assumes etl_erp_data.py is inside data_ingestion/
# and config.py is also inside data_ingestion/
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from config import CUSTOMER_CSV, PRODUCT_CSV, ORDER_CSV, EMPLOYEE_CSV

# --- Helper Functions ---
def generate_uuid():
    """Generates a UUID for entities that might not have a unique ID from source."""
    return str(uuid.uuid4())

def clean_string(s):
    """Cleans and strips string values, returns None if empty."""
    if pd.isna(s) or str(s).strip() == '':
        return None
    return str(s).strip()

def parse_date(date_str):
    """Parses date strings into YYYY-MM-DD format."""
    if pd.isna(date_str):
        return None
    for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y'):
        try:
            return datetime.strptime(str(date_str), fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return None # Or raise an error for unparseable dates

# --- Extraction Functions ---
def extract_data(file_path):
    """Extracts data from a CSV file using pandas."""
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return pd.DataFrame()
    try:
        df = pd.read_csv(file_path)
        print(f"Successfully extracted {len(df)} rows from {os.path.basename(file_path)}")
        return df
    except Exception as e:
        print(f"Error extracting data from {file_path}: {e}")
        return pd.DataFrame()

# --- Transformation Functions ---

def transform_customers(df_customers):
    """Transforms customer DataFrame into Knowledge Graph nodes."""
    nodes = []
    for _, row in df_customers.iterrows():
        nodes.append({
            "entity_type": "Customer",
            "id": clean_string(row.get('CustomerID')) or generate_uuid(),
            "properties": {
                "name": clean_string(row.get('CustomerName')),
                "email": clean_string(row.get('Email')),
                "phone": clean_string(row.get('Phone')),
                "address": clean_string(row.get('Address')),
                "type": clean_string(row.get('CustomerType')) or "Individual",
                "status": clean_string(row.get('Status')) or "Active",
                "industry": clean_string(row.get('Industry')),
            }
        })
    print(f"Transformed {len(nodes)} Customer nodes.")
    return nodes

def transform_products(df_products):
    """Transforms product DataFrame into Knowledge Graph nodes."""
    nodes = []
    for _, row in df_products.iterrows():
        nodes.append({
            "entity_type": "Product",
            "id": clean_string(row.get('ProductID')) or generate_uuid(),
            "properties": {
                "SKU": clean_string(row.get('SKU')),
                "name": clean_string(row.get('ProductName')),
                "description": clean_string(row.get('Description')),
                "price": float(row.get('Price')) if pd.notna(row.get('Price')) else None,
                "category": clean_string(row.get('Category')),
                "unit_of_measure": clean_string(row.get('UnitOfMeasure')),
                "status": clean_string(row.get('Status')) or "Active",
                "cost_price": float(row.get('CostPrice')) if pd.notna(row.get('CostPrice')) else None,
            }
        })
    print(f"Transformed {len(nodes)} Product nodes.")
    return nodes

def transform_employees(df_employees):
    """Transforms employee DataFrame into Knowledge Graph nodes."""
    nodes = []
    for _, row in df_employees.iterrows():
        nodes.append({
            "entity_type": "Employee",
            "id": clean_string(row.get('EmployeeID')) or generate_uuid(),
            "properties": {
                "name": clean_string(row.get('EmployeeName')),
                "email": clean_string(row.get('Email')),
                "department": clean_string(row.get('Department')),
                "role": clean_string(row.get('Role')),
                "hire_date": parse_date(row.get('HireDate')),
            }
        })
    print(f"Transformed {len(nodes)} Employee nodes.")
    return nodes

def transform_orders_and_relationships(df_orders, customer_nodes, product_nodes, employee_nodes):
    """
    Transforms order DataFrame into Order and OrderItem nodes,
    and creates relationships between them and other entities.
    """
    order_nodes = []
    order_item_nodes = []
    relationships = []

    # Create maps for quick lookup of existing node IDs
    customer_id_map = {node['id']: node for node in customer_nodes}
    product_id_map = {node['id']: node for node in product_nodes}
    employee_id_map = {node['id']: node for node in employee_nodes}

    # Group order items by OrderID to process each order once
    grouped_orders = df_orders.groupby('OrderID')

    for order_id_from_source, group in grouped_orders:
        # Take the first row for order-level details (assuming consistent across items for same order)
        first_row = group.iloc[0]
        order_id = clean_string(order_id_from_source) or generate_uuid()
        customer_id_source = clean_string(first_row.get('CustomerID'))
        sales_employee_id_source = clean_string(first_row.get('SalesEmployeeID'))

        # Create Order node
        order_nodes.append({
            "entity_type": "Order",
            "id": order_id,
            "properties": {
                "order_date": parse_date(first_row.get('OrderDate')),
                "total_amount": float(first_row.get('TotalAmount')) if pd.notna(first_row.get('TotalAmount')) else None,
                "status": clean_string(first_row.get('OrderStatus')) or "Pending",
                "order_type": "Sales", # Assuming sales order for now
            }
        })

        # Create PLACED relationship (Customer -> Order)
        if customer_id_source and customer_id_source in customer_id_map:
            relationships.append({
                "from_entity_type": "Customer",
                "from_entity_id": customer_id_source,
                "to_entity_type": "Order",
                "to_entity_id": order_id,
                "relationship_type": "PLACED",
                "properties": {}
            })
        else:
            print(f"Warning: Customer {customer_id_source} for Order {order_id} not found in transformed customers.")

        # Create CREATED relationship (Employee -> Order)
        if sales_employee_id_source and sales_employee_id_source in employee_id_map:
            relationships.append({
                "from_entity_type": "Employee",
                "from_entity_id": sales_employee_id_source,
                "to_entity_type": "Order",
                "to_entity_id": order_id,
                "relationship_type": "CREATED",
                "properties": {}
            })
        else:
            print(f"Warning: Sales Employee {sales_employee_id_source} for Order {order_id} not found in transformed employees.")

        # Process OrderItems for this order
        for _, item_row in group.iterrows():
            order_item_id = generate_uuid() # OrderItem doesn't have a source ID, so generate UUID
            product_id_source = clean_string(item_row.get('ProductID'))

            order_item_nodes.append({
                "entity_type": "OrderItem",
                "id": order_item_id,
                "properties": {
                    "quantity": int(item_row.get('Quantity')) if pd.notna(item_row.get('Quantity')) else None,
                    "unit_price": float(item_row.get('UnitPrice')) if pd.notna(item_row.get('UnitPrice')) else None,
                    "line_total": (float(item_row.get('Quantity')) * float(item_row.get('UnitPrice'))) if (pd.notna(item_row.get('Quantity')) and pd.notna(item_row.get('UnitPrice'))) else None,
                }
            })

            # Create CONTAINS relationship (Order -> OrderItem)
            relationships.append({
                "from_entity_type": "Order",
                "from_entity_id": order_id,
                "to_entity_type": "OrderItem",
                "to_entity_id": order_item_id,
                "relationship_type": "CONTAINS",
                "properties": {}
            })

            # Create REFERENCES relationship (OrderItem -> Product)
            if product_id_source and product_id_source in product_id_map:
                relationships.append({
                    "from_entity_type": "OrderItem",
                    "from_entity_id": order_item_id,
                    "to_entity_type": "Product",
                    "to_entity_id": product_id_source,
                    "relationship_type": "REFERENCES",
                    "properties": {}
                })
            else:
                print(f"Warning: Product {product_id_source} for OrderItem {order_item_id} not found in transformed products.")

    print(f"Transformed {len(order_nodes)} Order nodes, {len(order_item_nodes)} OrderItem nodes, and {len(relationships)} relationships.")
    return order_nodes, order_item_nodes, relationships

# --- Main ETL Function ---
def run_etl():
    """Orchestrates the entire ETL process."""
    print("--- Starting ERP Data ETL Process ---")

    # 1. Extract
    df_customers = extract_data(CUSTOMER_CSV)
    df_products = extract_data(PRODUCT_CSV)
    df_employees = extract_data(EMPLOYEE_CSV)
    df_orders = extract_data(ORDER_CSV)

    # 2. Transform
    # Transform master data first as they are referenced by transactional data
    customer_nodes = transform_customers(df_customers)
    product_nodes = transform_products(df_products)
    employee_nodes = transform_employees(df_employees)

    # Pass transformed master data nodes for relationship mapping
    order_nodes, order_item_nodes, order_relationships = transform_orders_and_relationships(
        df_orders, customer_nodes, product_nodes, employee_nodes
    )

    # Combine all nodes and relationships
    all_nodes = customer_nodes + product_nodes + employee_nodes + order_nodes + order_item_nodes
    all_relationships = order_relationships

    print(f"Total nodes to be created: {len(all_nodes)}")
    print(f"Total relationships to be created: {len(all_relationships)}")
    print("--- ETL Process Completed ---")

    return all_nodes, all_relationships

if __name__ == "__main__":
    nodes, relationships = run_etl()

    # Example of how to inspect the output
    print("\n--- Sample Transformed Nodes (first 5) ---")
    for node in nodes[:5]: # Print first 5 nodes
        print(node)
    
    print("\n--- Sample Transformed Relationships (first 5) ---")
    for rel in relationships[:5]: # Print first 5 relationships
        print(rel)