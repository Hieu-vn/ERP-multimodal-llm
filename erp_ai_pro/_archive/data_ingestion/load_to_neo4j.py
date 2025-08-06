# load_to_neo4j.py
from neo4j import GraphDatabase
import os
from etl_erp_data import run_etl # Import the ETL function

# --- Neo4j Connection Details ---
# It's better to get these from environment variables in a real application
URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# --- Loading Functions ---

class Neo4jLoader:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.verify_connection()

    def close(self):
        self.driver.close()

    def verify_connection(self):
        """Verifies the connection to the database."""
        try:
            with self.driver.session() as session:
                session.run("RETURN 1")
            print("Successfully connected to Neo4j.")
        except Exception as e:
            print(f"Error connecting to Neo4j: {e}")
            raise

    def clear_database(self):
        """Clears all nodes and relationships from the database."""
        print("Clearing existing data in Neo4j...")
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("Database cleared.")

    def _create_nodes_tx(self, tx, nodes_batch):
        # This query is now more robust, using labels from the entity_type
        query = """
        UNWIND $nodes AS node
        // Use apoc.create.node for dynamic labels
        CALL apoc.create.node([node.entity_type], {id: node.id}) YIELD node AS n
        SET n += node.properties
        """
        tx.run(query, nodes=nodes_batch)

    def load_nodes(self, nodes):
        if not nodes:
            print("No nodes to load.")
            return
        print(f"Loading {len(nodes)} nodes...")
        batch_size = 1000
        for i in range(0, len(nodes), batch_size):
            batch = nodes[i:i + batch_size]
            with self.driver.session() as session:
                session.write_transaction(self._create_nodes_tx, batch)
            print(f"Loaded {min(i + batch_size, len(nodes))} of {len(nodes)} nodes.")
        print("All nodes loaded.")

    def _create_relationships_tx(self, tx, relationships_batch):
        # This query is now more robust, using dynamic labels and relationship types
        query = """
        UNWIND $relationships AS rel
        MATCH (from_node) WHERE from_node.id = rel.from_entity_id
        MATCH (to_node) WHERE to_node.id = rel.to_entity_id
        // Use apoc.create.relationship for dynamic relationship types
        CALL apoc.create.relationship(from_node, rel.relationship_type, rel.properties, to_node) YIELD rel as r
        RETURN count(r)
        """
        tx.run(query, relationships=relationships_batch)

    def load_relationships(self, relationships):
        if not relationships:
            print("No relationships to load.")
            return
        print(f"Loading {len(relationships)} relationships...")
        batch_size = 500 # Relationships can be more complex, smaller batch size
        for i in range(0, len(relationships), batch_size):
            batch = relationships[i:i + batch_size]
            with self.driver.session() as session:
                session.write_transaction(self._create_relationships_tx, batch)
            print(f"Loaded {min(i + batch_size, len(relationships))} of {len(relationships)} relationships.")
        print("All relationships loaded.")

# --- Main Execution ---
if __name__ == "__main__":
    loader = None
    try:
        # 1. Run the ETL process to get the transformed data
        nodes, relationships = run_etl()

        # 2. Initialize the Neo4j Loader
        loader = Neo4jLoader(URI, USERNAME, PASSWORD)

        # 3. Clear existing data for a clean import
        loader.clear_database()

        # 4. Load the new data
        loader.load_nodes(nodes)
        loader.load_relationships(relationships)

        print("\nData loading pipeline to Neo4j completed successfully.")

    except Exception as e:
        print(f"\nAn error occurred during the data loading pipeline: {e}")
    finally:
        if loader:
            loader.close()
            print("Neo4j connection closed.")
