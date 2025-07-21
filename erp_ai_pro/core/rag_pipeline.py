# -*- coding: utf-8 -*-
"""
Core RAG (Retrieval-Augmented Generation) pipeline.
This module orchestrates the retrieval, prompt formatting, and language model generation.
"""
import sys
from pathlib import Path
import asyncio
from tenacity import retry, stop_after_attempt, wait_fixed, wait_random_exponential, retry_if_exception_type

print("Script started.") # Added for debugging

# Add the project root to the Python path for robust imports
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
# from langchain_community.llms import HuggingFacePipeline # Will be replaced or adapted
# from langchain.prompts import PromptTemplate # Will be replaced or adapted
# from langchain_core.runnables import RunnablePassthrough, RunnableParallel # Not needed for Atomic Agents
# from langchain_core.output_parsers import StrOutputParser # Not needed for Atomic Agents
# from langchain.agents import AgentExecutor, create_react_agent # Not needed for Atomic Agents
# from langchain import hub # Not needed for Atomic Agents

# Import Atomic Agents components
from atomic_agents.lib.agents.base_chat_agent import BaseChatAgent
from atomic_agents.lib.models.agent_config import AgentConfig
from atomic_agents.lib.models.chat_memory import ChatMemory
from atomic_agents.lib.tools.tool_factory import ToolFactory # To create tool instances from classes

# Import refactored tools
from erp_ai_pro.core.tools import GetCurrentDateTool, GraphERPLookupTool, VectorSearchTool, \
    GetProductStockLevelTool, GetCustomerOutstandingBalanceTool, PerformCalculationTool

# Import other agent-specific functions (these will need to be refactored into Atomic Agent tools later)
# For now, keep them as they are, but they won't be directly used by the Atomic Agent yet.
from erp_ai_pro.core.agents.sales import CreateOrderTool, GetOrderStatusTool, GetCustomerOutstandingBalanceTool, GetProductStockLevelTool
from erp_ai_pro.core.agents.inventory import GetInventoryOverviewTool, StockInTool, StockOutTool, InventoryCheckTool, GetLowStockAlertsTool
from erp_ai_pro.core.agents.finance import GetRevenueReportTool, GetExpenseReportTool, GetCustomerDebtTool, CreateReceiptTool, CreatePaymentTool
from erp_ai_pro.core.agents.project_management import CreateProjectTool, GetProjectDetailsTool, UpdateProjectStatusTool, CreateTaskTool, AssignTaskTool
from erp_ai_pro.core.agents.workflow_automation import TriggerWorkflowTool, GetWorkflowStatusTool, ApproveWorkflowStepTool
from erp_ai_pro.core.agents.hrm import CreateEmployeeTool, GetEmployeeProfileTool, SubmitLeaveRequestTool, CalculatePayrollTool, CreatePerformanceGoalTool
from erp_ai_pro.core.agents.crm import CreateLeadTool, QualifyLeadTool, CreateOpportunityTool, CreateCustomerAccountTool, CreateSupportTicketTool
from erp_ai_pro.core.agents.computer_use import AutoCreatePurchaseOrderTool, AutoGenerateReportTool, AutoDataEntryTool

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline # For re-ranking
from erp_ai_pro.core.rag_config import RAGConfig

# Prompt for query rewriting/expansion (will need to be adapted for Atomic Agents if used)
# For now, keep it as a string, but it won't be a LangChain PromptTemplate anymore.
QUERY_REWRITE_PROMPT_STR = """You are a helpful AI assistant. Your task is to rephrase or expand the user's question to improve retrieval from a knowledge base.
Consider synonyms, related concepts, and different ways of asking the same question.
Generate up to 3 alternative questions, one per line. If the original question is already good, just repeat it.

Question: {question}
Rewritten Questions:
"""

# Define a retry decorator for LLM calls
# This will retry up to 3 times with exponential backoff for any Exception
llm_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_random_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True
)

class RAGPipeline:
    """A professional, end-to-end RAG pipeline for the ERP assistant."""

    def __init__(self):
        """Initializes the pipeline components to None. Call setup() to load them."""
        self.config = RAGConfig()
        self.vector_store = None
        self.llm = None # This will be the HuggingFace pipeline object, not LangChain's HuggingFacePipeline
        self.reranker_pipeline = None
        self.agent = None # This will be the Atomic Agent
        self.chat_memory = ChatMemory() # Initialize Atomic Agents ChatMemory
        print("RAG Pipeline initialized. Call setup() to load models and data.")

    def setup(self):
        """Loads all necessary components: vector store, embedding model, and LLM."""
        print("--- Setting up RAG Pipeline ---")

        # 1. Load the persistent vector store
        print(f"Attempting to load vector store from: {self.config.vector_store_path}")
        try:
            embedding_function = SentenceTransformerEmbeddings(model_name=self.config.embedding_model_name or "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
            self.vector_store = Chroma(
                persist_directory=self.config.vector_store_path,
                embedding_function=embedding_function,
                collection_name=self.config.collection_name
            )
            print("Vector store loaded successfully.")
        except Exception as e:
            print(f"Error loading vector store: {e}")
            raise # Re-raise to stop execution if vector store fails

        # 2. Initialize the LLM.
        # We will now attempt to load a fine-tuned model, falling back to a base model if not found.
        print(f"Attempting to initialize LLM (base: {self.config.base_model_name})...")

        try:
            from transformers import AutoModelForSeq2SeqLM, AutoModelForCausalLM, AutoTokenizer, pipeline
            from peft import PeftModel
            import torch
            import os

            model_name = self.config.base_model_name
            is_causal_lm = False # Assume seq2seq for T5, will be true for Llama/Gemma

            # Determine model type and load accordingly
            if "t5" in model_name.lower() or "flan" in model_name.lower():
                ModelClass = AutoModelForSeq2SeqLM
                task = "text2text-generation"
            else: # Assume causal LM for others like Llama, Gemma
                ModelClass = AutoModelForCausalLM
                task = "text-generation"
                is_causal_lm = True

            print(f"Loading base model: {model_name} with {ModelClass.__name__}")
            load_dtype = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float32
            load_in_4bit_enabled = False # Set to False for now

            model = ModelClass.from_pretrained(
                model_name,
                torch_dtype=load_dtype,
                load_in_4bit=load_in_4bit_enabled
            )
            tokenizer = AutoTokenizer.from_pretrained(model_name)

            # Load adapter weights if a fine-tuned model path is provided and exists
            finetuned_model_path = self.config.finetuned_model_path
            if finetuned_model_path and os.path.exists(finetuned_model_path):
                print(f"Loading fine-tuned adapter weights from: {finetuned_model_path}")
                model = PeftModel.from_pretrained(model, finetuned_model_path)
                print("Fine-tuned model loaded successfully.")
            else:
                print(f"Fine-tuned model not found at '{finetuned_model_path}'. Using base model.")

            if is_causal_lm and tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            elif not is_causal_lm and tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

            # Configure pipeline_kwargs based on task
            pipeline_kwargs = {
                "max_new_tokens": 256,
                "max_length": 512, # Keep for T5, will be less critical for larger context models
                "temperature": 0.7, # Keep temperature for now, will be handled by pipeline
                "top_k": 50,
            }
            if is_causal_lm: # Add do_sample and top_p for causal LMs
                pipeline_kwargs["do_sample"] = True
                pipeline_kwargs["top_p"] = 0.95

            # Create the transformers pipeline object
            self.llm = pipeline(
                task=task,
                model=model,
                tokenizer=tokenizer,
                **pipeline_kwargs
            )
            print("LLM initialized successfully.")
        except ImportError as e:
            print(f"Warning: Could not import necessary libraries for fine-tuned model loading ({e}). Falling back to basic HuggingFacePipeline.")
            # Fallback to a simple callable if HuggingFacePipeline is not used
            self.llm = lambda prompt: {"generated_text": "Placeholder LLM response."}
            print("LLM initialized with placeholder model.")
        except Exception as e:
            print(f"Error initializing LLM with fine-tuned model: {e}. Falling back to basic HuggingFacePipeline.")
            self.llm = lambda prompt: {"generated_text": "Placeholder LLM response."}
            print("LLM initialized with placeholder model.")

        # 3. Initialize the Re-ranker
        print("Attempting to initialize Re-ranker...")
        try:
            reranker_model_name = self.config.reranker_model_name
            self.reranker_tokenizer = AutoTokenizer.from_pretrained(reranker_model_name)
            self.reranker_model = AutoModelForSequenceClassification.from_pretrained(reranker_model_name)
            self.reranker_pipeline = pipeline(
                "text-classification",
                model=self.reranker_model,
                tokenizer=self.reranker_tokenizer,
                device=0 if torch.cuda.is_available() else -1, # Use GPU if available
            )
            print("Re-ranker initialized successfully.")
        except Exception as e:
            print(f"Error initializing Re-ranker: {e}. Re-ranking will be skipped.")
            self.reranker_pipeline = None

        # 4. Initialize Atomic Agents tools
        print("Initializing Atomic Agents tools...")
        self.all_potential_tools = {
            "get_current_date": GetCurrentDateTool(),
            "graph_erp_lookup": GraphERPLookupTool(llm_model=self.llm),
            "vector_search": VectorSearchTool(self.vector_store, self.config.retrieval_k),
            "get_product_stock_level": GetProductStockLevelTool(),
            "create_order": CreateOrderTool(),
            "get_order_status": GetOrderStatusTool(),
            "get_customer_outstanding_balance": GetCustomerOutstandingBalanceTool(),
            "get_inventory_overview": GetInventoryOverviewTool(),
            "stock_in": StockInTool(),
            "stock_out": StockOutTool(),
            "inventory_check": InventoryCheckTool(),
            "get_low_stock_alerts": GetLowStockAlertsTool(),
            "get_revenue_report": GetRevenueReportTool(),
            "get_expense_report": GetExpenseReportTool(),
            "get_customer_debt": GetCustomerDebtTool(),
            "create_receipt": CreateReceiptTool(),
            "create_payment": CreatePaymentTool(),
            "create_project": CreateProjectTool(),
            "get_project_details": GetProjectDetailsTool(),
            "update_project_status": UpdateProjectStatusTool(),
            "create_task": CreateTaskTool(),
            "assign_task": AssignTaskTool(),
            "trigger_workflow": TriggerWorkflowTool(),
            "get_workflow_status": GetWorkflowStatusTool(),
            "approve_workflow_step": ApproveWorkflowStepTool(),
            "create_employee": CreateEmployeeTool(),
            "get_employee_profile": GetEmployeeProfileTool(),
            "submit_leave_request": SubmitLeaveRequestTool(),
            "calculate_payroll": CalculatePayrollTool(),
            "create_performance_goal": CreatePerformanceGoalTool(),
            "create_lead": CreateLeadTool(),
            "qualify_lead": QualifyLeadTool(),
            "create_opportunity": CreateOpportunityTool(),
            "create_customer_account": CreateCustomerAccountTool(),
            "create_support_ticket": CreateSupportTicketTool(),
            "auto_create_purchase_order": AutoCreatePurchaseOrderTool(),
            "auto_generate_report": AutoGenerateReportTool(),
            "auto_data_entry": AutoDataEntryTool(),
            "perform_calculation": PerformCalculationTool(),
        }
        print("Atomic Agents tools initialized.")

        # 5. Initialize the Atomic Agent
        # The agent will be created dynamically in the query method based on the role and available tools.
        print("Atomic Agent will be initialized dynamically per query.")

    @llm_retry
    async def query(self, role: str, question: str) -> dict:
        """
        Queries the RAG Agent asynchronously.
        Returns a dictionary containing the answer and source documents.
        """
        thought_process = []
        extracted_source_docs = []
        answer = ""

        try:
            # Step 1: Query Rewriting/Expansion (using the HuggingFace pipeline directly)
            print(f"Original Question: {question}")
            rewritten_questions = [question] # Start with original question
            if self.llm: # Only attempt rewriting if LLM is available
                try:
                    # Assuming self.llm is a HuggingFace pipeline that takes a string and returns a dict with 'generated_text'
                    rewrite_input = QUERY_REWRITE_PROMPT_STR.format(question=question)
                    rewritten_output_dict = self.llm(rewrite_input)
                    rewritten_output = rewritten_output_dict[0]['generated_text'] if isinstance(rewritten_output_dict, list) else rewritten_output_dict['generated_text']

                    # Split by newline and clean up, add to list
                    rewritten_questions.extend([q.strip() for q in rewritten_output.split('\n') if q.strip() and q.strip() != question])
                    rewritten_questions = list(set(rewritten_questions)) # Remove duplicates
                    print(f"Rewritten Questions: {rewritten_questions}")
                except Exception as e:
                    print(f"Error during query rewriting: {e}. Proceeding with original question.")

            agent_invocation_question = question # Use original question for agent

            # --- RBAC Enforcement: Dynamically filter tools based on user role ---
            allowed_tool_names = self.config.ROLE_TOOL_MAPPING.get(role, self.config.ROLE_TOOL_MAPPING["default"])

            # Construct the list of actual tool instances for the current role
            current_role_tools = []
            for tool_name in allowed_tool_names:
                tool_instance_or_func = self.all_potential_tools.get(tool_name)
                if tool_instance_or_func:
                    # For Atomic Agents, we need to pass the tool class or an instance of BaseTool
                    # Since I've refactored them to classes with .run methods, I'll pass the instance.
                    # The ToolFactory can wrap these if needed, but for now, direct instance is fine.
                    # Special handling for graph_erp_lookup is now done during initialization of GraphERPLookupTool
                    current_role_tools.append(tool_instance_or_func)
                else:
                    print(f"Warning: Configured tool '{tool_name}' not found in all_potential_tools.")

            if not current_role_tools:
                answer = f"Xin lỗi, vai trò '{role}' của bạn không có quyền truy cập vào bất kỳ công cụ nào. Vui lòng liên hệ quản trị viên."
                return {
                    "answer": answer,
                    "source_documents": [],
                    "thought_process": []
                }

            # Create the Atomic Agent dynamically
            # For now, a simple system prompt. This will need to be more sophisticated.
            system_prompt_content = f"Bạn là trợ lý AI chuyên nghiệp cho hệ thống ERP, hỗ trợ tiếng Việt. Nhiệm vụ của bạn là trả lời chính xác, sử dụng thông minh các công cụ nghiệp vụ bên dưới. Bạn đang đóng vai trò là {role}."
            # Add tool descriptions to the system prompt
            tool_descriptions = "\n".join([f"- {name}: {tool.__doc__.strip() if tool.__doc__ else 'No description'}" for name, tool in self.all_potential_tools.items() if name in allowed_tool_names])
            system_prompt_content += f"\n\nBạn có các công cụ sau:\n{tool_descriptions}"

            from erp_ai_pro.core.llm_providers import HuggingFaceLLMProvider

            atomic_llm_provider = HuggingFaceLLMProvider(self.llm)

            # Create AgentConfig
            agent_config = AgentConfig(
                llm_provider=atomic_llm_provider,
                system_prompt=system_prompt_content,
                tools=current_role_tools, # Pass tool instances directly
                memory=self.chat_memory # Pass the chat memory
            )
            self.agent = BaseChatAgent(config=agent_config)

            # Invoke the Atomic Agent
            # The input to the agent will be the question.
            # The output will be a structured response from the agent.
            agent_response = await self.agent.run(agent_invocation_question)
            answer = agent_response.output # Assuming the agent's output is directly the answer

            # For thought process and source documents, this will depend on Atomic Agents' output structure.
            # For now, I'll simplify this part.
            thought_process.append(f"Agent Response: {agent_response}")
            # If agent_response contains tool calls or observations, extract them here.
            # For now, I'll just add a placeholder for source documents.
            extracted_source_docs.append({"page_content": "Source documents not yet extracted from Atomic Agent output.", "metadata": {"source": "atomic_agent_placeholder"}})

        except Exception as e:
            print(f"Error invoking Atomic Agent: {e}")
            answer = f"Xin lỗi, có lỗi xảy ra khi cố gắng trả lời câu hỏi của bạn: {e}"

        # Apply re-ranking if reranker_pipeline is available and there are extracted_source_docs
        if self.reranker_pipeline and extracted_source_docs:
            print("Applying re-ranking to retrieved documents...")
            rerank_inputs = [[question, doc["page_content"]] for doc in extracted_source_docs]
            rerank_results = self.reranker_pipeline(rerank_inputs)

            scored_documents = []
            for i, doc in enumerate(extracted_source_docs):
                score = next((item["score"] for item in rerank_results[i] if item["label"] == "LABEL_1"), 0.0)
                scored_documents.append((score, doc))

            scored_documents.sort(key=lambda x: x[0], reverse=True)
            extracted_source_docs = [doc for score, doc in scored_documents]
            print(f"Documents re-ranked. Top score: {scored_documents[0][0] if scored_documents else 'N/A'}")

        return {
            "answer": answer,
            "source_documents": extracted_source_docs,
            "thought_process": thought_process
        }

# Example usage (for testing)
if __name__ == '__main__':
    async def main():
        pipeline = RAGPipeline()
        pipeline.setup()

        print("\n--- Performing test query ---")
        test_role = "warehouse_manager"
        test_question = "Làm thế nào để kiểm tra tồn kho hiện tại?"

        result = await pipeline.query(test_role, test_question)

        print(f"\nRole: {test_role}")
        print(f"Question: {test_question}")
        print(f"\nAnswer: {result['answer']}")
        print(f"\nSource Documents:")
        for doc in result['source_documents']:
            print(doc)


        print("\n--- Performing test query with no relevant docs ---")
        test_role_no_docs = "unauthorized_user"
        test_question_no_docs = "Chính sách lương thưởng là gì?"

        result_no_docs = await pipeline.query(test_role_no_docs, test_question_no_docs)

        print(f"\nRole: {test_role_no_docs}")
        print(f"Question: {test_question_no_docs}")
        print(f"\nAnswer: {result_no_docs['answer']}")
        print(f"\nSource Documents:")
        for doc in result_no_docs['source_documents']:
            print(doc)

    import asyncio
    asyncio.run(main())