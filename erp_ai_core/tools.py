from langchain.tools import tool
import datetime
from erp_ai_core.graph_management import neo4j_connection, get_cypher_generation_chain, GRAPH_SCHEMA

@tool
def get_current_date(query: str) -> str:
    """
    Returns the current date. Use this tool when the user asks for the current date.
    The input query can be any string, it will be ignored.
    """
    return datetime.date.today().strftime("%Y-%m-%d")

@tool
def graph_erp_lookup(question: str, role: str, llm_model) -> str:
    """
    Generates and executes a Cypher query against the ERP Knowledge Graph based on the user's question and role.
    Use this for questions about entities, relationships, and specific data points in the ERP.
    Input should be the natural language question and the user's role.
    """
    try:
        # Generate Cypher query using LLM
        cypher_chain = get_cypher_generation_chain(llm_model)
        generated_cypher = cypher_chain.invoke({"question": question, "role": role})
        print(f"Generated Cypher: {generated_cypher}")

        # Execute the generated Cypher query
        result = neo4j_connection.query(generated_cypher)
        return str(result)
    except Exception as e:
        return f"Error in graph lookup: {e}"

class VectorSearchTool:
    def __init__(self, vector_store, retrieval_k):
        self.vector_store = vector_store
        self.retrieval_k = retrieval_k

    @tool
    def vector_search(self, query: str, role: str) -> str:
        """
        Searches the knowledge base for relevant documents based on the user's query and role.
        Use this tool for general questions, procedural inquiries, or policy lookups.
        Input should be a clear question and the user's role.
        """
        retriever = self.vector_store.as_retriever(search_kwargs={'k': self.retrieval_k, 'filter': {'role': role}})
        docs = retriever.get_relevant_documents(query)
        return "\n\n".join([doc.page_content for doc in docs])

class LiveERP_APITool:
    def __init__(self):
        pass # No external connection needed for mock

    @tool
    def get_product_stock_level(self, product_id: str) -> str:
        """
        Retrieves the current stock level for a given product ID from the live ERP system.
        Use this tool when the user asks for real-time stock information for a specific product.
        Input should be the product ID (e.g., 'PROD001').
        """
        mock_stock_data = {
            "PROD001": 150,
            "PROD002": 75,
            "PROD003": 200,
        }
        stock = mock_stock_data.get(product_id, "N/A")
        if stock != "N/A":
            return f"Current stock level for {product_id}: {stock} units."
        else:
            return f"Product {product_id} not found or stock information unavailable."

    @tool
    def get_customer_outstanding_balance(self, customer_id: str) -> str:
        """
        Retrieves the outstanding balance for a given customer ID from the live ERP system.
        Use this tool when the user asks for a customer's current financial balance or outstanding payments.
        Input should be the customer ID (e.g., 'CUST001').
        """
        mock_balance_data = {
            "CUST001": 1250.50,
            "CUST002": 0.00,
            "CUST003": 500.75,
        }
        balance = mock_balance_data.get(customer_id, "N/A")
        if balance != "N/A":
            return f"Outstanding balance for {customer_id}: ${balance:.2f}."
        else:
            return f"Customer {customer_id} not found or balance information unavailable."

class DataAnalysisTool:
    def __init__(self):
        pass

    @tool
    def perform_calculation(self, expression: str) -> str:
        """
        Performs a simple mathematical calculation or evaluates a Python expression.
        Use this tool when the user asks for calculations or data analysis that can be expressed as a Python expression.
        Input should be a valid Python expression (e.g., '100 * 0.15', 'sum([1, 2, 3])').
        Be careful with complex expressions or potential security risks.
        """
        try:
            # WARNING: Evaluating arbitrary expressions can be a security risk.
            # In a production environment, consider using a safer evaluation method
            # or a restricted set of allowed operations.
            result = eval(expression)
            return f"Result of '{expression}': {result}"
        except Exception as e:
            return f"Error performing calculation '{expression}': {e}"