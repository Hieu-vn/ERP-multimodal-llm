from pydantic import BaseModel, Field
import datetime
from erp_ai_pro.core.graph_management import neo4j_connection, get_cypher_generation_chain, GRAPH_SCHEMA
from erp_ai_pro.core.erp_client import ERPClient
import numexpr as ne

# Initialize the ERP Client
# In a real app, these would come from a secure config
ERP_API_BASE_URL = "https://api.example-erp.com/v1"
ERP_API_KEY = "your_secret_api_key"
erp_client = ERPClient(base_url=ERP_API_BASE_URL, api_key=ERP_API_KEY)

# Define input and output schemas for GetCurrentDateTool
class GetCurrentDateInput(BaseModel):
    query: str = Field(description="Any string, will be ignored. Use this tool when the user asks for the current date.")

class GetCurrentDateOutput(BaseModel):
    current_date: str = Field(description="The current date in YYYY-MM-DD format.")

class GetCurrentDateTool:
    """
    Returns the current date. Use this tool when the user asks for the current date.
    """
    input_schema = GetCurrentDateInput
    output_schema = GetCurrentDateOutput

    def run(self, query: str) -> GetCurrentDateOutput:
        return GetCurrentDateOutput(current_date=datetime.date.today().strftime("%Y-%m-%d"))

class GraphERPLookupInput(BaseModel):
    question: str = Field(description="The natural language question about entities, relationships, or specific data points in the ERP.")
    role: str = Field(description="The user's role in the ERP system.")

class GraphERPLookupOutput(BaseModel):
    result: str = Field(description="The result of the Cypher query execution.")

class GraphERPLookupTool:
    """
    Generates and executes a Cypher query against the ERP Knowledge Graph based on the user's question and role.
    Use this for questions about entities, relationships, and specific data points in the ERP.
    """
    input_schema = GraphERPLookupInput
    output_schema = GraphERPLookupOutput

    def __init__(self, llm_model):
        self.llm_model = llm_model

    def run(self, question: str, role: str) -> GraphERPLookupOutput:
        try:
            # Generate Cypher query using LLM
            cypher_chain = get_cypher_generation_chain(self.llm_model)
            generated_cypher = cypher_chain.invoke({"question": question, "role": role})
            print(f"Generated Cypher: {generated_cypher}")

            # Execute the generated Cypher query
            result = neo4j_connection.query(generated_cypher)
            return GraphERPLookupOutput(result=str(result))
        except Exception as e:
            return GraphERPLookupOutput(result=f"Error in graph lookup: {e}")

class VectorSearchInput(BaseModel):
    query: str = Field(description="A clear question to search for relevant documents.")
    role: str = Field(description="The user's role in the ERP system.")

class VectorSearchOutput(BaseModel):
    documents: str = Field(description="The concatenated content of relevant documents retrieved from the knowledge base.")

class VectorSearchTool:
    """
    Searches the knowledge base for relevant documents based on the user's query and role.
    Use this tool for general questions, procedural inquiries, or policy lookups.
    """
    input_schema = VectorSearchInput
    output_schema = VectorSearchOutput

    def __init__(self, vector_store, retrieval_k):
        self.vector_store = vector_store
        self.retrieval_k = retrieval_k

    def run(self, query: str, role: str) -> VectorSearchOutput:
        retriever = self.vector_store.as_retriever(search_kwargs={'k': self.retrieval_k, 'filter': {'role': role}})
        docs = retriever.get_relevant_documents(query)
        return VectorSearchOutput(documents="\n\n".join([doc.page_content for doc in docs]))

class GetProductStockLevelInput(BaseModel):
    product_id: str = Field(description="The ID of the product (e.g., 'PROD001').")

class GetProductStockLevelOutput(BaseModel):
    stock_level: str = Field(description="The current stock level for the product.")

class GetProductStockLevelTool:
    """
    Retrieves the current stock level for a given product ID from the live ERP system.
    Use this tool when the user asks for real-time stock information for a specific product.
    """
    input_schema = GetProductStockLevelInput
    output_schema = GetProductStockLevelOutput

    def run(self, product_id: str) -> GetProductStockLevelOutput:
        result = erp_client.get_product_stock_level(product_id)
        if "error" in result:
            return GetProductStockLevelOutput(stock_level=f"Error retrieving stock for {product_id}: {result['error']}")
        stock = result.get("stock_level", "N/A")
        return GetProductStockLevelOutput(stock_level=f"Current stock level for {product_id}: {stock} units.")

# Define input and output schemas for GetCustomerOutstandingBalanceTool
class GetCustomerOutstandingBalanceInput(BaseModel):
    customer_id: str = Field(description="The ID of the customer (e.g., 'CUST001').")

class GetCustomerOutstandingBalanceOutput(BaseModel):
    outstanding_balance: str = Field(description="The outstanding balance for the customer.")

class GetCustomerOutstandingBalanceTool:
    """
    Retrieves the outstanding balance for a given customer ID from the live ERP system.
    Use this tool when the user asks for a customer's current financial balance or outstanding payments.
    """
    input_schema = GetCustomerOutstandingBalanceInput
    output_schema = GetCustomerOutstandingBalanceOutput

    def run(self, customer_id: str) -> GetCustomerOutstandingBalanceOutput:
        result = erp_client.get_customer_outstanding_balance(customer_id)
        if "error" in result:
            return GetCustomerOutstandingBalanceOutput(outstanding_balance=f"Error retrieving balance for {customer_id}: {result['error']}")
        balance = result.get("outstanding_balance", "N/A")
        return GetCustomerOutstandingBalanceOutput(outstanding_balance=f"Outstanding balance for {customer_id}: ${balance:.2f}.")

class PerformCalculationInput(BaseModel):
    expression: str = Field(description="A valid mathematical expression to evaluate (e.g., '100 * 0.15', '2**8').")

class PerformCalculationOutput(BaseModel):
    result: str = Field(description="The result of the calculation.")

class PerformCalculationTool:
    """
    Performs a safe mathematical calculation.
    Use this tool when the user asks for calculations.
    Only supports basic arithmetic, functions, and comparisons.
    """
    input_schema = PerformCalculationInput
    output_schema = PerformCalculationOutput

    def run(self, expression: str) -> PerformCalculationOutput:
        try:
            # Use numexpr for safe evaluation of mathematical expressions
            result = ne.evaluate(expression)
            return PerformCalculationOutput(result=f"Result of '{expression}': {result}")
        except Exception as e:
            return PerformCalculationOutput(result=f"Error performing calculation '{expression}': Invalid or unsupported expression. Please use a simple mathematical expression.")
