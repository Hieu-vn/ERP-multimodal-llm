# -*- coding: utf-8 -*-
"""
Core RAG (Retrieval-Augmented Generation) pipeline.
This module orchestrates the retrieval, prompt formatting, and language model generation.
"""
import sys
from pathlib import Path

# Add the project root to the Python path for robust imports
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser

from config.rag_config import RAGConfig

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
        print(f"Loading vector store from: {self.config.vector_store_path}")
        embedding_function = SentenceTransformerEmbeddings(model_name=self.config.embedding_model_name)
        self.vector_store = Chroma(
            persist_directory=self.config.vector_store_path,
            embedding_function=embedding_function,
            collection_name=self.config.collection_name
        )
        print("Vector store loaded successfully.")

        # 2. Initialize the LLM. 
        # For now, we use a standard HuggingFace model as a placeholder.
        # This will be replaced by our fine-tuned model later.
        print("Initializing placeholder LLM (google/flan-t5-base)...")
        self.llm = HuggingFacePipeline.from_model_id(
            model_id="google/flan-t5-base",
            task="text2text-generation",
            pipeline_kwargs={"max_new_tokens": 256, "top_k": 50, "temperature": 0.1},
        )
        print("LLM initialized successfully.")

        # 3. Build the RAG chain using LangChain Expression Language (LCEL)
        # This is the modern, composable way to build chains.
        
        # Define the prompt template
        template = """You are an expert ERP system assistant. Your task is to answer the user's question based ONLY on the context provided.
        If the context does not contain the answer, state that you don't have enough information.
        
        CONTEXT:
        {context}
        
        QUESTION:
        {question}
        
        ANSWER:
        """
        prompt = PromptTemplate(template=template, input_variables=["context", "question"])

        # Define the retriever, with role-based filtering
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={'k': self.config.retrieval_k}
        )

        # Create the processing chain
        self.chain = (
            RunnableParallel(
                # The retriever is called in parallel with the question passthrough
                context=lambda x: retriever.get_relevant_documents(x["question"], search_kwargs={"filter": {"role": x["role"]}}),
                question=RunnablePassthrough()
            )
            | {
                "context": lambda x: "\n---\n".join([doc.page_content for doc in x["context"]]),
                "question": lambda x: x["question"]["question"],
                "role": lambda x: x["question"]["role"],
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )

        print("RAG chain built successfully.")
        print("--- RAG Pipeline setup complete ---")

    def query(self, role: str, question: str) -> dict:
        """ 
        Queries the RAG chain.
        Returns a dictionary containing the answer and source documents.
        """
        if not self.chain:
            raise RuntimeError("Pipeline has not been set up. Please call setup() first.")

        # The retriever needs to be called separately to get the source documents for the response
        retriever = self.vector_store.as_retriever(search_kwargs={'k': self.config.retrieval_k, 'filter': {'role': role}})
        source_documents = retriever.get_relevant_documents(question)

        # Invoke the full chain to get the final answer
        answer = self.chain.invoke({"role": role, "question": question})
        
        return {
            "answer": answer,
            "source_documents": [doc.to_json() for doc in source_documents]
        }

# Example usage (for testing)
if __name__ == '__main__':
    pipeline = RAGPipeline()
    pipeline.setup()

    print("\n--- Performing test query ---")
    test_role = "warehouse_manager"
    test_question = "Làm thế nào để kiểm tra tồn kho hiện tại?"
    
    result = pipeline.query(test_role, test_question)
    
    print(f"\nRole: {test_role}")
    print(f"Question: {test_question}")
    print(f"\nAnswer: {result['answer']}")
    print(f"\nSource Documents:")
    for doc in result['source_documents']:
        print(doc)