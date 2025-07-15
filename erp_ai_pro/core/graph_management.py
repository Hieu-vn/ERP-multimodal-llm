from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from neo4j import GraphDatabase
from erp_ai_pro.core.rag_config import RAGConfig

# Define your graph schema (simplified for example)
GRAPH_SCHEMA = """
Nodes:
- Product {name: STRING, stock: INTEGER, price: FLOAT}
- Customer {name: STRING, industry: STRING, role: STRING}
- Order {order_id: STRING, date: DATE, total: FLOAT}
- Employee {name: STRING, department: STRING, role: STRING}

Relationships:
- (Customer)-[:PLACED]->(Order)
- (Order)-[:CONTAINS]->(Product)
- (Employee)-[:MANAGES]->(Employee)
- (Employee)-[:WORKS_IN]->(Department)

Important:
- Customer.role can be 'sales_rep', 'admin', 'customer'.
- Employee.role can be 'sales_manager', 'sales_rep', 'hr'.
"""

# Prompt for Cypher generation, now with role awareness
CYPHER_GENERATION_TEMPLATE = """
You are an expert in Cypher query language and an ERP system.
Your task is to translate a user's natural language question into a Cypher query, considering the provided graph schema and the user's role.

**Graph Schema:**
{graph_schema}

**User Role:** {role}

**IMPORTANT SECURITY RULE:**
If the user's role is 'sales_rep', you MUST add a WHERE clause to the Cypher query to filter results ONLY for customers or orders associated with that specific sales representative. Assume the sales_rep's name is available and can be matched (e.g., Customer.sales_rep_name = 'John Doe'). If the question is about general company data not tied to a specific sales rep, do not apply this filter.

**Examples (for sales_rep 'John Doe'):**
Question: "Show me all orders placed by customers managed by John Doe."
Cypher: MATCH (s:Employee {{name: 'John Doe', role: 'sales_rep'}})-[:MANAGES_CUSTOMER]->(c:Customer)-[:PLACED]->(o:Order) RETURN o

Question: "What is the stock of Product A?"
Cypher: MATCH (p:Product {{name: 'Product A'}}) RETURN p.stock

**Question:** {question}
**Cypher Query:**
"""
CYPHER_PROMPT = PromptTemplate.from_template(CYPHER_GENERATION_TEMPLATE)

class Neo4jConnection:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self.driver.close()

    def query(self, cypher_query: str) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(cypher_query)
            return [record.data() for record in result]

# Initialize Neo4j connection using RAGConfig
rag_config = RAGConfig()
neo4j_connection = Neo4jConnection(
    rag_config.neo4j_uri,
    rag_config.neo4j_username,
    rag_config.neo4j_password
)

# Chain for Cypher generation
def get_cypher_generation_chain(llm):
    return (
        RunnablePassthrough.assign(graph_schema=lambda x: GRAPH_SCHEMA)
        | CYPHER_PROMPT
        | llm.bind(stop=["\nCypher Query:"]) # Stop generation after the query
        | StrOutputParser()
    )
