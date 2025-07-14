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
from langchain_community.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub # Để tải prompt cho agent
from erp_ai_core.tools import get_current_date, graph_erp_lookup, VectorSearchTool, LiveERP_APITool, DataAnalysisTool # Import các công cụ
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline # For re-ranking
from erp_ai_core.agent_sales import get_product_stock_level, create_order, get_order_status, get_customer_outstanding_balance
from erp_ai_core.agent_inventory import get_inventory_overview, stock_in, stock_out, inventory_check, get_low_stock_alerts
from erp_ai_core.agent_finance import get_revenue_report, get_expense_report, get_customer_debt, create_receipt, create_payment

from config.rag_config import RAGConfig

# Prompt for query rewriting/expansion
QUERY_REWRITE_PROMPT = PromptTemplate.from_template(
    """You are a helpful AI assistant. Your task is to rephrase or expand the user's question to improve retrieval from a knowledge base.
    Consider synonyms, related concepts, and different ways of asking the same question.
    Generate up to 3 alternative questions, one per line. If the original question is already good, just repeat it.

    Question: {question}
    Rewritten Questions:
    """
)

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
        self.llm = None
        self.chain = None
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
                hf_pipeline = pipeline(
                    task=task,
                    model=model,
                    tokenizer=tokenizer,
                    **pipeline_kwargs
                )

                self.llm = HuggingFacePipeline(pipeline=hf_pipeline)
                print("LLM initialized successfully.")
        except ImportError as e:
            print(f"Warning: Could not import necessary libraries for fine-tuned model loading ({e}). Falling back to basic HuggingFacePipeline.")
            self.llm = HuggingFacePipeline.from_model_id(
                model_id=self.config.llm_placeholder_model_name,
                task="text2text-generation",
                pipeline_kwargs={"max_new_tokens": 256, "top_k": 50, "temperature": 0.1},
            )
            print("LLM initialized with placeholder model.")
        except Exception as e:
            print(f"Error initializing LLM with fine-tuned model: {e}. Falling back to basic HuggingFacePipeline.")
            self.llm = HuggingFacePipeline.from_model_id(
                model_id=self.config.llm_placeholder_model_name,
                task="text2text-generation",
                pipeline_kwargs={"max_new_tokens": 256, "top_k": 50, "temperature": 0.1},
            )
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

        # 4. Build the RAG chain using LangChain Agents
        print("Attempting to build RAG Agent...")
        try:
            # Initialize VectorSearchTool
            self.vector_search_tool_instance = VectorSearchTool(self.vector_store, self.config.retrieval_k)

            # Initialize LiveERP_APITool
            self.live_erp_api_tool_instance = LiveERP_APITool()

            # Initialize DataAnalysisTool
            self.data_analysis_tool_instance = DataAnalysisTool()

            # Store all potential tools as attributes for dynamic access in query()
            self.all_potential_tools = {
                "get_current_date": get_current_date,
                "vector_search": self.vector_search_tool_instance.vector_search,
                "graph_erp_lookup": graph_erp_lookup,
                # SALES AGENT
                "get_product_stock_level": get_product_stock_level,
                "create_order": create_order,
                "get_order_status": get_order_status,
                "get_customer_outstanding_balance": get_customer_outstanding_balance,
                # INVENTORY AGENT
                "get_inventory_overview": get_inventory_overview,
                "stock_in": stock_in,
                "stock_out": stock_out,
                "inventory_check": inventory_check,
                "get_low_stock_alerts": get_low_stock_alerts,
                # FINANCE AGENT
                "get_revenue_report": get_revenue_report,
                "get_expense_report": get_expense_report,
                "get_customer_debt": get_customer_debt,
                "create_receipt": create_receipt,
                "create_payment": create_payment,
                # DATA ANALYSIS
                "perform_calculation": self.data_analysis_tool_instance.perform_calculation
            }

            # Define the prompt for the ReAct Agent (will be used dynamically in query())
            self.agent_prompt_template = """Bạn là trợ lý AI chuyên nghiệp cho hệ thống ERP, hỗ trợ tiếng Việt. Nhiệm vụ của bạn là trả lời chính xác, sử dụng thông minh các công cụ nghiệp vụ bên dưới:\n\nBạn có các công cụ sau:\n{tools}\n\n**Hướng dẫn sử dụng tool:**\n- **`vector_search`**: Dùng cho câu hỏi kiến thức tổng quát, quy trình, định nghĩa, chính sách.\n- **`graph_erp_lookup`**: Dùng cho truy vấn dữ liệu quan hệ, số liệu, danh sách, hoặc các truy vấn phức tạp về mối quan hệ.\n- **`get_product_stock_level`**: Kiểm tra tồn kho sản phẩm.\n- **`create_order`**: Tạo đơn hàng mới.\n- **`get_order_status`**: Kiểm tra trạng thái đơn hàng.\n- **`get_customer_outstanding_balance`**: Kiểm tra công nợ khách hàng.\n- **`get_inventory_overview`**: Lấy tổng quan tồn kho.\n- **`stock_in`**: Nhập kho.\n- **`stock_out`**: Xuất kho.\n- **`inventory_check`**: Kiểm kê kho.\n- **`get_low_stock_alerts`**: Cảnh báo tồn kho tối thiểu.\n- **`get_revenue_report`**: Lấy báo cáo doanh thu.\n- **`get_expense_report`**: Lấy báo cáo chi phí.\n- **`get_customer_debt`**: Kiểm tra công nợ khách hàng.\n- **`create_receipt`**: Lập phiếu thu.\n- **`create_payment`**: Lập phiếu chi.\n\nHãy chọn đúng công cụ cho từng loại câu hỏi nghiệp vụ.\n\nSử dụng format reasoning như sau:\n\nQuestion: câu hỏi đầu vào\nThought: phân tích từng bước, chọn tool phù hợp\nAction: tên tool\nAction Input: input cho tool\nObservation: kết quả trả về\n... (có thể lặp lại nhiều lần)\nThought: Đã đủ thông tin\nFinal Answer: câu trả lời cuối cùng\n\nBắt đầu!\n\nQuestion: {input}\nThought:{agent_scratchpad}\n"""
            # No self.chain initialization here, it will be done dynamically in query()
            print("RAG Agent components initialized. AgentExecutor will be built dynamically per query.")

    @llm_retry
    async def query(self, role: str, question: str) -> dict:
        """ 
        Queries the RAG Agent asynchronously.
        Returns a dictionary containing the answer and source documents.
        """
        # if not self.chain: # No longer needed as chain is built dynamically
        #     raise RuntimeError("Pipeline has not been set up. Please call setup() first.")

        thought_process = []
        extracted_source_docs = []
        answer = "" # Will be filled by agent

        try:
            # Step 1: Query Rewriting/Expansion
            print(f"Original Question: {question}")
            rewritten_questions = [question] # Start with original question
            if self.llm: # Only attempt rewriting if LLM is available
                try:
                    rewrite_chain = QUERY_REWRITE_PROMPT | self.llm | StrOutputParser()
                    rewritten_output = await rewrite_chain.ainvoke({"question": question})
                    # Split by newline and clean up, add to list
                    rewritten_questions.extend([q.strip() for q in rewritten_output.split('\n') if q.strip() and q.strip() != question])
                    rewritten_questions = list(set(rewritten_questions)) # Remove duplicates
                    print(f"Rewritten Questions: {rewritten_questions}")
                except Exception as e:
                    print(f"Error during query rewriting: {e}. Proceeding with original question.")
            
            # For now, we will just use the original question for the agent invocation
            # In a more advanced setup, the agent might iterate through rewritten questions
            # or the tools themselves might handle multiple queries.
            agent_invocation_question = question # Use original question for agent

            # --- RBAC Enforcement: Dynamically filter tools based on user role ---
            allowed_tool_names = self.config.ROLE_TOOL_MAPPING.get(role, self.config.ROLE_TOOL_MAPPING["default"])
            
            # Construct the list of actual tool functions/instances for the current role
            current_role_tools = []
            for tool_name in allowed_tool_names:
                tool_func = self.all_potential_tools.get(tool_name)
                if tool_func:
                    # Special handling for graph_erp_lookup to pass llm_model
                    if tool_name == "graph_erp_lookup":
                        current_role_tools.append(lambda q, r: tool_func(q, r, self.llm))
                    else:
                        current_role_tools.append(tool_func)
                else:
                    print(f"Warning: Configured tool '{tool_name}' not found in all_potential_tools.")

            if not current_role_tools:
                answer = f"Xin lỗi, vai trò '{role}' của bạn không có quyền truy cập vào bất kỳ công cụ nào. Vui lòng liên hệ quản trị viên."
                return {
                    "answer": answer,
                    "source_documents": [],
                    "thought_process": []
                }

            # Create the Agent with the filtered tools
            agent_prompt = PromptTemplate.from_template(self.agent_prompt_template)
            agent = create_react_agent(self.llm, current_role_tools, agent_prompt)
            
            # Create the AgentExecutor dynamically
            agent_executor = AgentExecutor(agent=agent, tools=current_role_tools, verbose=True, handle_parsing_errors=True, return_intermediate_steps=True)

            # Invoke the AgentExecutor
            agent_result = await agent_executor.ainvoke({"input": agent_invocation_question, "role": role}) # Pass role to agent if needed
            answer = agent_result.get("output", agent_result.get("answer", "Không thể tạo câu trả lời từ Agent."))

            # Format the thought process for XAI and extract source documents from tool observations
            if "intermediate_steps" in agent_result:
                for step in agent_result["intermediate_steps"]:
                    action = step[0]
                    observation = step[1]
                    thought_process.append(f"Thought: {action.log.strip()}\nAction: {action.tool}\nAction Input: {action.tool_input}\nObservation: {observation}")

                    # Check if the vector_search tool was used and extract its output
                    if action.tool == "vector_search":
                        # Assuming observation contains the concatenated document content
                        # For now, we'll just add a placeholder indicating content came from vector search
                        extracted_source_docs.append({"page_content": observation, "metadata": {"source": "vector_search_tool_output"}})

        except Exception as e:
            print(f"Error invoking Agent: {e}")
            answer = f"Xin lỗi, có lỗi xảy ra khi cố gắng trả lời câu hỏi của bạn: {e}"
        
        # Apply re-ranking if reranker_pipeline is available and there are extracted_source_docs
        if self.reranker_pipeline and extracted_source_docs:
            print("Applying re-ranking to retrieved documents...")
            # Prepare documents for re-ranking: list of (query, document_text) pairs
            # For simplicity, we'll use the original question as the query for re-ranking
            # In a more advanced setup, you might use a rewritten query or sub-queries.
            rerank_inputs = [[question, doc["page_content"]] for doc in extracted_source_docs]
            
            # Perform re-ranking
            # The output of the pipeline will be a list of dictionaries with 'label' and 'score'
            # We assume a binary classification model where 'LABEL_1' indicates relevance.
            rerank_results = self.reranker_pipeline(rerank_inputs)

            # Pair original documents with their re-ranking scores
            scored_documents = []
            for i, doc in enumerate(extracted_source_docs):
                # Find the score for LABEL_1 (relevant) or similar, depending on model output
                score = next((item["score"] for item in rerank_results[i] if item["label"] == "LABEL_1"), 0.0)
                scored_documents.append((score, doc))
            
            # Sort documents by score in descending order
            scored_documents.sort(key=lambda x: x[0], reverse=True)
            extracted_source_docs = [doc for score, doc in scored_documents]
            print(f"Documents re-ranked. Top score: {scored_documents[0][0] if scored_documents else 'N/A'}")

        return {
            "answer": answer,
            "source_documents": extracted_source_docs, # Updated to use extracted_source_docs
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
