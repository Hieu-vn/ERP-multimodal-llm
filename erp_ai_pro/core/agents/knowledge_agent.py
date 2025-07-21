import asyncio
from typing import Dict, Any, List
from erp_ai_pro.core.tools import VectorSearchTool, graph_erp_lookup
from erp_ai_pro.core.rag_config import RAGConfig

class KnowledgeAgent:
    """
    Agent chuyên xử lý truy vấn kiến thức cho hệ thống ERP AI Pro.
    Sử dụng vector search, LLM và RBAC để trả lời câu hỏi dựa trên vai trò người dùng.
    """
    def __init__(self, config, llm):
        self.config = config or RAGConfig()
        self.llm = llm
        # Khởi tạo vector search tool
        self.vector_search_tool = VectorSearchTool(self._init_vector_store(), self.config.retrieval_k)

    def _init_vector_store(self):
        # Khởi tạo vector store (ChromaDB)
        from langchain_community.vectorstores import Chroma
        from langchain_community.embeddings import SentenceTransformerEmbeddings
        embedding_function = SentenceTransformerEmbeddings(model_name=self.config.embedding_model_name)
        return Chroma(
            persist_directory=self.config.vector_store_path,
            embedding_function=embedding_function,
            collection_name=self.config.collection_name
        )

    async def execute(self, question: str, role: str) -> Dict[str, Any]:
        """
        Xử lý truy vấn kiến thức: tìm context, gọi LLM sinh câu trả lời, trả về answer, source, thought process.
        """
        thought_process = []
        source_documents = []
        answer = ""
        try:
            # 1. Vector search lấy context
            context = self.vector_search_tool.vector_search(question, role)
            thought_process.append(f"Vector search context:\n{context}")
            source_documents.append({"page_content": context, "metadata": {"source": "vector_search"}})

            # 2. Gọi LLM sinh câu trả lời
            prompt = self._build_prompt(question, context)
            llm_response = await self._call_llm(prompt)
            answer = llm_response
            thought_process.append(f"LLM answer: {answer}")
        except Exception as e:
            answer = f"Xin lỗi, có lỗi xảy ra khi xử lý truy vấn: {e}"
            thought_process.append(str(e))
        return {
            "answer": answer,
            "source_documents": source_documents,
            "thought_process": thought_process
        }

    def _build_prompt(self, question: str, context: str) -> str:
        return f"""Bạn là trợ lý AI ERP chuyên nghiệp. Dưới đây là ngữ cảnh truy xuất được từ hệ thống:
{context}

Câu hỏi của người dùng: {question}

Hãy trả lời ngắn gọn, chính xác, có trích dẫn nguồn nếu có thể."""

    async def _call_llm(self, prompt: str) -> str:
        # Hỗ trợ cả vLLM (async) và HuggingFace pipeline (sync)
        if hasattr(self.llm, 'acomplete'):  # vLLM async
            sampling_params = self._get_sampling_params()
            result = await self.llm.acomplete(prompt, sampling_params)
            return result.outputs[0].text.strip()
        elif callable(self.llm):  # HuggingFace pipeline
            # pipeline có thể không async, nên dùng run_in_executor
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda: self.llm(prompt, max_new_tokens=256)[0]["generated_text"])
            return result.strip()
        else:
            raise RuntimeError("LLM không hỗ trợ kiểu gọi async hoặc pipeline.")

    def _get_sampling_params(self):
        """Helper to create sampling parameters for vLLM."""
        from vllm import SamplingParams
        return SamplingParams(
            temperature=0.7, # Default temperature
            top_p=0.9,       # Default top_p
            max_tokens=1024  # A reasonable limit for an answer
        )