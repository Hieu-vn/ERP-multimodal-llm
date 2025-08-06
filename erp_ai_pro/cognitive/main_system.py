# -*- coding: utf-8 -*-
"""
Main System for ERP AI Pro - ATOMIC Agent Architecture
This file initializes and orchestrates the specialized agents.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Corrected imports for the new 3-layer architecture
from erp_ai_pro.config.config import SystemConfig
from erp_ai_pro.cognitive.rbac import get_allowed_tools_for_role

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import structlog

# Corrected imports for the new 3-layer architecture
from erp_ai_pro.cognitive.agents.orchestrator import OrchestratorAgent
from erp_ai_pro.cognitive.agents.knowledge_agent import KnowledgeAgent
from erp_ai_pro.cognitive.agents.multimodal_agent import MultimodalAgent
from erp_ai_pro.cognitive.agents.bi_agent import BusinessIntelligenceAgent
from erp_ai_pro.cognitive.agents.live_erp_agent import LiveERPAgent

logger = structlog.get_logger()

class MainSystem:
    """The main orchestrating class that manages the ATOMIC agents."""

    def __init__(self, config: SystemConfig = None):
        self.config = config or SystemConfig()
        self.llm = None
        self.agents = {}
        logger.info("MainSystem initialized.")

    async def setup(self):
        """Initializes the LLM and all specialized agents."""
        logger.info("Setting up MainSystem...")
        await self._setup_llm()

        if self.llm is None:
            logger.error("LLM initialization failed. System cannot start.")
            return

        self.agents["OrchestratorAgent"] = OrchestratorAgent(self.llm, self.config)
        self.agents["KnowledgeAgent"] = KnowledgeAgent(self.config, self.llm)
        self.agents["MultimodalAgent"] = MultimodalAgent(self.config)
        self.agents["BusinessIntelligenceAgent"] = BusinessIntelligenceAgent()
        self.agents["LiveERPAgent"] = LiveERPAgent()
        self.agents["FallbackAgent"] = self._fallback_agent

        logger.info("All agents initialized. MainSystem setup complete.")

    async def _setup_llm(self):
        """Sets up the primary language model for the system."""
        try:
            from vllm import LLM
            self.llm = LLM(
                model=self.config.base_model_name,
                tensor_parallel_size=torch.cuda.device_count() if torch.cuda.is_available() else 1,
                gpu_memory_utilization=0.8
            )
            logger.info(f"VLLM model loaded successfully: {self.config.base_model_name}")
        except Exception as e:
            logger.warning(f"VLLM failed, falling back to Hugging Face transformers: {e}")
            try:
                tokenizer = AutoTokenizer.from_pretrained(self.config.base_model_name)
                model = AutoModelForCausalLM.from_pretrained(
                    self.config.base_model_name,
                    torch_dtype=torch.float16,
                    device_map="auto"
                )
                self.llm = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    torch_dtype=torch.float16,
                    device_map="auto",
                )
                logger.info(f"Successfully loaded model '{self.config.base_model_name}' with Hugging Face transformers.")
            except Exception as hf_e:
                logger.error(f"Hugging Face fallback also failed: {hf_e}")
                self.llm = None

    async def query(self, question: str, role: str, **kwargs) -> Dict[str, Any]:
        """The main entry point for processing a user query."""
        if not self.llm:
            return {"error": "LLM not initialized. System is not ready."}

        # RBAC: Dynamically filter tools based on user role using the new RBAC module
        allowed_tool_names = get_allowed_tools_for_role(role)
        
        # In a real scenario, you would pass the allowed tools to the agent.
        # For now, we will just log them.
        logger.info(f"Allowed tools for role '{role}': {allowed_tool_names}")

        orchestrator = self.agents["OrchestratorAgent"]
        image_path = kwargs.get("image_path")

        # The orchestrator needs to be aware of the allowed tools
        chosen_agent_name = await orchestrator.route_request(
            question, 
            has_image=bool(image_path),
            allowed_tools=allowed_tool_names
        )
        chosen_agent = self.agents.get(chosen_agent_name)

        if not chosen_agent:
            logger.warning(f"Orchestrator chose an unknown agent: '{chosen_agent_name}'. Using Fallback.")
            chosen_agent = self.agents["FallbackAgent"]

        logger.info(f"Executing chosen agent: {chosen_agent_name}")
        try:
            # The agent execution logic needs to be updated to handle the filtered tools
            # This is a placeholder for the next development phase
            if chosen_agent_name == "KnowledgeAgent":
                result = await chosen_agent.execute(question=question, role=role)
            elif chosen_agent_name == "MultimodalAgent":
                result = await chosen_agent.execute(image_path=image_path, question=question)
            elif chosen_agent_name == "BusinessIntelligenceAgent":
                analysis_request = {"data": {}} 
                result = await chosen_agent.execute(analysis_request)
            elif chosen_agent_name == "LiveERPAgent":
                # This part needs significant refactoring to use the dynamic tools
                tool_name = "get_product_stock_level" # Placeholder
                if tool_name in allowed_tool_names:
                    tool_input = {"product_id": "PROD001"} # Placeholder
                    result = await chosen_agent.execute(tool_name, tool_input)
                else:
                    result = {"error": f"Tool '{tool_name}' is not allowed for role '{role}'."}
            else:
                result = await chosen_agent(question)
            
            result["chosen_agent"] = chosen_agent_name
            return result

        except Exception as e:
            logger.error(f"An error occurred during agent execution: {e}")
            return {"error": str(e), "chosen_agent": chosen_agent_name}

    async def _fallback_agent(self, question: str) -> Dict[str, Any]:
        """A simple agent for handling queries that cannot be routed."""
        return {
            "answer": f"I am not sure how to handle your request: '{question}'. Could you please rephrase?",
            "source": "fallback_agent"
        }


def create_main_system(config: SystemConfig = None) -> MainSystem:
    """Create and return the main system instance."""
    return MainSystem(config)

"""
Main System for ERP AI Pro - ATOMIC Agent Architecture
This file initializes and orchestrates the specialized agents.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from erp_ai_pro.core.config import SystemConfig

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import structlog


from erp_ai_pro.core.agents.orchestrator import OrchestratorAgent
from erp_ai_pro.core.agents.knowledge_agent import KnowledgeAgent
from erp_ai_pro.core.agents.multimodal_agent import MultimodalAgent
from erp_ai_pro.core.agents.bi_agent import BusinessIntelligenceAgent
from erp_ai_pro.core.agents.live_erp_agent import LiveERPAgent

logger = structlog.get_logger()





class MainSystem:
    """The main orchestrating class that manages the ATOMIC agents."""

    def __init__(self, config: SystemConfig = None):
        self.config = config or SystemConfig()
        self.llm = None
        self.agents = {}
        logger.info("MainSystem initialized.")

    async def setup(self):
        """Initializes the LLM and all specialized agents."""
        logger.info("Setting up MainSystem...")
        await self._setup_llm()

        if self.llm is None:
            logger.error("LLM initialization failed. System cannot start.")
            return

        self.agents["OrchestratorAgent"] = OrchestratorAgent(self.llm, self.config)
        self.agents["KnowledgeAgent"] = KnowledgeAgent(self.config, self.llm)
        self.agents["MultimodalAgent"] = MultimodalAgent(self.config)
        self.agents["BusinessIntelligenceAgent"] = BusinessIntelligenceAgent()
        self.agents["LiveERPAgent"] = LiveERPAgent()
        self.agents["FallbackAgent"] = self._fallback_agent

        logger.info("All agents initialized. MainSystem setup complete.")

    async def _setup_llm(self):
        """Sets up the primary language model for the system."""
        try:
            from vllm import LLM
            self.llm = LLM(
                model=self.config.base_model_name,
                tensor_parallel_size=torch.cuda.device_count() if torch.cuda.is_available() else 1,
                gpu_memory_utilization=0.8
            )
            logger.info(f"VLLM model loaded successfully: {self.config.base_model_name}")
        except Exception as e:
            logger.warning(f"VLLM failed, falling back to Hugging Face transformers: {e}")
            try:
                tokenizer = AutoTokenizer.from_pretrained(self.config.base_model_name)
                model = AutoModelForCausalLM.from_pretrained(
                    self.config.base_model_name,
                    torch_dtype=torch.float16,
                    device_map="auto"
                )
                self.llm = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    torch_dtype=torch.float16,
                    device_map="auto",
                )
                logger.info(f"Successfully loaded model '{self.config.base_model_name}' with Hugging Face transformers.")
            except Exception as hf_e:
                logger.error(f"Hugging Face fallback also failed: {hf_e}")
                self.llm = None

    async def query(self, question: str, role: str, **kwargs) -> Dict[str, Any]:
        """The main entry point for processing a user query."""
        if not self.llm:
            return {"error": "LLM not initialized. System is not ready."}

        # RBAC: Dynamically filter tools based on user role
        allowed_tool_names = self.config.ROLE_TOOL_MAPPING.get(role, self.config.ROLE_TOOL_MAPPING.get("default", []))
        
        # In a real scenario, you would pass the allowed tools to the agent.
        # For now, we will just log them.
        logger.info(f"Allowed tools for role '{role}': {allowed_tool_names}")

        orchestrator = self.agents["OrchestratorAgent"]
        image_path = kwargs.get("image_path")

        chosen_agent_name = await orchestrator.route_request(question, has_image=bool(image_path))
        chosen_agent = self.agents.get(chosen_agent_name)

        if not chosen_agent:
            logger.warning(f"Orchestrator chose an unknown agent: '{chosen_agent_name}'. Using Fallback.")
            chosen_agent = self.agents["FallbackAgent"]

        logger.info(f"Executing chosen agent: {chosen_agent_name}")
        try:
            if chosen_agent_name == "KnowledgeAgent":
                result = await chosen_agent.execute(question=question, role=role)
            elif chosen_agent_name == "MultimodalAgent":
                result = await chosen_agent.execute(image_path=image_path, question=question)
            elif chosen_agent_name == "BusinessIntelligenceAgent":
                # Note: In a real scenario, data would be fetched or passed in.
                # This is a placeholder for demonstration.
                analysis_request = {"data": {}} 
                result = await chosen_agent.execute(analysis_request)
            elif chosen_agent_name == "LiveERPAgent":
                # Note: In a real scenario, the tool name and input would be
                # extracted from the user's query by the orchestrator.
                tool_name = "get_product_stock_level"
                tool_input = {"product_id": "PROD001"}
                result = await chosen_agent.execute(tool_name, tool_input)
            else:
                result = await chosen_agent(question)
            
            result["chosen_agent"] = chosen_agent_name
            return result

        except Exception as e:
            logger.error(f"An error occurred during agent execution: {e}")
            return {"error": str(e), "chosen_agent": chosen_agent_name}

    async def _fallback_agent(self, question: str) -> Dict[str, Any]:
        """A simple agent for handling queries that cannot be routed."""
        return {
            "answer": f"I am not sure how to handle your request: '{question}'. Could you please rephrase?",
            "source": "fallback_agent"
        }


def create_main_system(config: SystemConfig = None) -> MainSystem:
    """Create and return the main system instance."""
    return MainSystem(config)