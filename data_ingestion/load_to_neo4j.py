# load_to_neo4j.py
from neo4j import GraphDatabase
import os

# --- Neo4j Connection Details ---
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "password" # Thay bằng password bạn đã đặt cho Neo4j

# --- Simulated Data from Step 1.3 (for demonstration) ---
# In a real scenario, this data would come from the run_etl() function
simulated_nodes = [
    {
        "entity_type": "Customer",
        "id": "CUST001",
        "properties": {
            "name": "Nguyen Van A",
            "email": "nguyenvana@example.com",
            "phone": "0901234567",
            "address": "123 Le Loi",
            "type": "Individual",
            "status": "Active",
            "industry": "Retail"
        }
    },
    {
        "entity_type": "Product",
        "id": "PROD001",
        "properties": {
            "SKU": "SKU001",
            "name": "Laptop XYZ",
            "description": "High performance laptop",
            "price": 1200.00,
            "category": "Electronics",
            "unit_of_measure": "EA",
            "status": "Active",
            "cost_price": 800.00
        }
    },
    {
        "entity_type": "Employee",
        "id": "EMP001",
        "properties": {
            "name": "Le Van F",
            "email": "levanf@example.com",
            "department": "Sales",
            "role": "Sales Manager",
            "hire_date": "2020-01-01"
        }
    },
    {
        "entity_type": "Order",
        "id": "ORD001",
        "properties": {
            "order_date": "2024-01-15",
            "total_amount": 1225.50,
            "status": "Completed",
            "order_type": "Sales"
        }
    },
    {
        "entity_type": "OrderItem",
        "id": "oi_uuid_1", # Placeholder for actual UUID
        "properties": {
            "quantity": 1,
            "unit_price": 1200.00,
            "line_total": 1200.00
        }
    },
    {
        "entity_type": "OrderItem",
        "id": "oi_uuid_2", # Placeholder for actual UUID
        "properties": {
            "quantity": 1,
            "unit_price": 25.50,
            "line_total": 25.50
        }
    },
    {
        "entity_type": "Customer",
        "id": "CUST002",
        "properties": {
            "name": "Cong Ty B",
            "email": "congtyb@example.com",
            "phone": "0287654321",
            "address": "456 Tran Hung Dao",
            "type": "Corporate",
            "status": "Active",
            "industry": "Manufacturing"
        }
    },
    {
        "entity_type": "Product",
        "id": "PROD003",
        "properties": {
            "SKU": "SKU003",
            "name": "Ban Lam Viec",
            "description": "Modern office desk",
            "price": 150.00,
            "category": "Furniture",
            "unit_of_measure": "EA",
            "status": "Active",
            "cost_price": 90.00
        }
    },
    {
        "entity_type": "Employee",
        "id": "EMP002",
        "properties": {
            "name": "Nguyen Thi G",
            "email": "nguyenthig@example.com",
            "department": "Marketing",
            "role": "Marketing Specialist",
            "hire_date": "2021-03-15"
        }
    },
    {
        "entity_type": "Order",
        "id": "ORD002",
        "properties": {
            "order_date": "2024-02-20",
            "total_amount": 150.00,
            "status": "Pending",
            "order_type": "Sales"
        }
    },
    {
        "entity_type": "OrderItem",
        "id": "oi_uuid_3", # Placeholder for actual UUID
        "properties": {
            "quantity": 1,
            "unit_price": 150.00,
            "line_total": 150.00
        }
    },
]

simulated_relationships = [
    {
        "from_entity_type": "Customer",
        "from_entity_id": "CUST001",
        "to_entity_type": "Order",
        "to_entity_id": "ORD001",
        "relationship_type": "PLACED",
        "properties": {}
    },
    {
        "from_entity_type": "Employee",
        "from_entity_id": "EMP001",
        "to_entity_type": "Order",
        "to_entity_id": "ORD001",
        "relationship_type": "CREATED",
        "properties": {}
    },
    {
        "from_entity_type": "Order",
        "from_entity_id": "ORD001",
        "to_entity_type": "OrderItem",
        "to_entity_id": "oi_uuid_1",
        "relationship_type": "CONTAINS",
        "properties": {}
    },
    {
        "from_entity_type": "OrderItem",
        "from_entity_id": "oi_uuid_1",
        "to_entity_type": "Product",
        "to_entity_id": "PROD001",
        "relationship_type": "REFERENCES",
        "properties": {}
    },
    {
        "from_entity_type": "Order",
        "from_entity_id": "ORD001",
        "to_entity_type": "OrderItem",
        "to_entity_id": "oi_uuid_2",
        "relationship_type": "CONTAINS",
        "properties": {}
    },
    {
        "from_entity_type": "OrderItem",
        "from_entity_id": "oi_uuid_2",
        "to_entity_type": "Product",
        "to_entity_id": "PROD002",
        "relationship_type": "REFERENCES",
        "properties": {}
    },
    {
        "from_entity_type": "Customer",
        "from_entity_id": "CUST002",
        "to_entity_type": "Order",
        "to_entity_id": "ORD002",
        "relationship_type": "PLACED",
        "properties": {}
    },
    {
        "from_entity_type": "Employee",
        "from_entity_id": "EMP002",
        "to_entity_type": "Order",
        "to_entity_id": "ORD002",
        "relationship_type": "CREATED",
        "properties": {}
    },
    {
        "from_entity_type": "Order",
        "from_entity_id": "ORD002",
        "to_entity_type": "OrderItem",
        "to_entity_id": "oi_uuid_3",
        "relationship_type": "CONTAINS",
        "properties": {}
    },
    {
        "from_entity_type": "OrderItem",
        "from_entity_id": "oi_uuid_3",
        "to_entity_type": "Product",
        "to_entity_id": "PROD003",
        "relationship_type": "REFERENCES",
        "properties": {}
    },
]

# --- Loading Functions ---

class Neo4jLoader:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self.driver.close()

    def _create_nodes_tx(self, tx, nodes_batch):
        query = """
        UNWIND $nodes AS node
        MERGE (n:{{node.entity_type}} {{id: node.id}})
        SET n += node.properties
        """
        tx.run(query, nodes=nodes_batch)

    def load_nodes(self, nodes):
        print(f"Loading {len(nodes)} nodes...")
        batch_size = 1000 # Adjust batch size as needed
        for i in range(0, len(nodes), batch_size):
            batch = nodes[i:i + batch_size]
            with self.driver.session() as session:
                session.write_transaction(self._create_nodes_tx, batch)
            print(f"Loaded {min(i + batch_size, len(nodes))} nodes.")
        print("All nodes loaded.")

    def _create_relationships_tx(self, tx, relationships_batch):
        query = """
        UNWIND $relationships AS rel
        MATCH (from_node:{{rel.from_entity_type}} {{id: rel.from_entity_id}})
        MATCH (to_node:{{rel.to_entity_type}} {{id: rel.to_entity_id}})
        MERGE (from_node)-[r:{{rel.relationship_type}}]->(to_node)
        SET r += rel.properties
        """
        tx.run(query, relationships=relationships_batch)

    def load_relationships(self, relationships):
        print(f"Loading {len(relationships)} relationships...")
        batch_size = 1000 # Adjust batch size as needed
        for i in range(0, len(relationships), batch_size):
            batch = relationships[i:i + batch_size]
            with self.driver.session() as session:
                session.write_transaction(self._create_relationships_tx, batch)
            print(f"Loaded {min(i + batch_size, len(relationships))} relationships.")
        print("All relationships loaded.")

# --- Main Execution ---
if __name__ == "__main__":
    loader = None
    try:
        loader = Neo4jLoader(URI, USERNAME, PASSWORD)
        print("Connected to Neo4j.")

        # Clear existing data (optional, for clean runs during development)
        # with loader.driver.session() as session:
        #     session.run("MATCH (n) DETACH DELETE n")
        # print("Cleared existing data in Neo4j.")

        # 1. Load Nodes
        loader.load_nodes(simulated_nodes)

        # 2. Load Relationships
        loader.load_relationships(simulated_relationships)

        print("Data loading to Neo4j completed successfully.")

    except Exception as e:
        print(f"Error during Neo4j data loading: {e}")
    finally:
        if loader:
            loader.close()
            print("Neo4j connection closed.")
