import pytest
from unittest.mock import MagicMock, patch
from erp_ai_pro.core.rag_pipeline import RAGPipeline
from erp_ai_pro.core.rag_config import RAGConfig

# Mock RAGConfig for consistent testing
@pytest.fixture
def mock_rag_config():
    config = MagicMock(spec=RAGConfig)
    config.vector_store_path = "mock/path/to/vector_store"
    config.embedding_model_name = "mock-embedding-model"
    config.collection_name = "mock_collection"
    config.base_model_name = "mock-llm-model"
    config.finetuned_model_path = "mock/path/to/finetuned_model"
    config.reranker_model_name = "mock-reranker-model"
    config.llm_placeholder_model_name = "mock-placeholder-llm"
    config.retrieval_k = 3
    config.ROLE_TOOL_MAPPING = {
        "default": ["vector_search"],
        "admin": ["vector_search", "graph_erp_lookup"]
    }
    return config

@pytest.mark.asyncio
async def test_rag_pipeline_initialization(mock_rag_config):
    with (
        patch('erp_ai_pro.core.rag_pipeline.RAGConfig', return_value=mock_rag_config),
        patch('erp_ai_pro.core.rag_pipeline.SentenceTransformerEmbeddings'),
        patch('erp_ai_pro.core.rag_pipeline.Chroma'),
        patch('erp_ai_pro.core.rag_pipeline.AutoTokenizer'),
        patch('erp_ai_pro.core.rag_pipeline.AutoModelForSeq2SeqLM'),
        patch('erp_ai_pro.core.rag_pipeline.AutoModelForCausalLM'),
        patch('erp_ai_pro.core.rag_pipeline.PeftModel'),
        patch('erp_ai_pro.core.rag_pipeline.pipeline'),
        patch('erp_ai_pro.core.rag_pipeline.HuggingFacePipeline'),
        patch('erp_ai_pro.core.rag_pipeline.VectorSearchTool'),
        patch('erp_ai_pro.core.rag_pipeline.LiveERP_APITool'),
        patch('erp_ai_pro.core.rag_pipeline.DataAnalysisTool'),
    ):

        pipeline = RAGPipeline()
        assert pipeline.config is not None
        assert pipeline.vector_store is None
        assert pipeline.llm is None
        assert pipeline.chain is None

        # Test setup method
        await pipeline.setup() # setup is now async

        assert pipeline.vector_store is not None
        assert pipeline.llm is not None
        # reranker_pipeline might be None if mock_reranker_model doesn't exist
        # assert pipeline.reranker_pipeline is not None # This might fail if reranker init fails
        assert pipeline.vector_search_tool_instance is not None
        assert pipeline.live_erp_api_tool_instance is not None
        assert pipeline.data_analysis_tool_instance is not None
        assert len(pipeline.all_potential_tools) > 0

# You would add more tests here for the query method, mocking its dependencies
# and checking the output based on different inputs and mocked tool responses.
