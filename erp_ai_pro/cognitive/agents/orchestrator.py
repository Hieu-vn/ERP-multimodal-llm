# -*- coding: utf-8 -*-
"""
Orchestrator Agent for ERP AI Pro
The central brain that routes requests to specialized agents.
"""

import logging
from typing import Dict, Any

import structlog

# This import will be updated later when config is centralized.
from erp_ai_pro.config.config import SystemConfig

logger = structlog.get_logger()

# The prompt is the core of the Orchestrator's logic.
ORCHESTRATOR_SYSTEM_PROMPT = """You are a highly intelligent Orchestrator AI for a complex ERP system. 
Your primary role is to analyze a user's query and route it to the most appropriate specialized agent. 
You must respond with ONLY the name of the chosen agent.

Here are the available agents and their specializations:

1.  **LiveERPAgent**:
    - Use for any action that creates, reads, updates, or deletes (CRUD) data in the live ERP system.
    - This is the primary agent for real-time, transactional tasks.
    - **Task Management Examples**: "Create a new task for @nhanvien_A to design the homepage", "What are my tasks?", "List all tasks for project PROJ-WEB", "Update task T-1 to 'Hoàn thành'".
    - **Other Examples**: "What is the current stock for product PROD001?", "What is the balance for customer CUST002?"

2.  **BusinessIntelligenceAgent**:
    - Use for requests requiring deep analysis, aggregation, forecasting, or finding complex relationships in data.
    - This agent answers "Why?" and "What if?" questions.
    - **Example queries**: "Forecast our revenue for the next quarter.", "Which products are most often sold together?", "Analyze customer churn for the last year.", "What was our best-selling product category in Q2?"

3.  **KnowledgeAgent**:
    - Use for general questions, policy lookups, definitions, or information retrieval from the static knowledge base (e.g., company handbooks, regulations).
    - Use this when the user is asking for information, not for an action.
    - **Example queries**: "What is our company's return policy?", "Explain the process for new employee onboarding.", "How do I request a new laptop?"

4.  **MultimodalAgent**:
    - Use ONLY when the user's query includes an image.
    - This agent will analyze the image first.
    - **Example queries**: "What product is shown in this image?", "Extract the total amount from this invoice scan.", "Based on this chart, what was the sales trend?"

5.  **FallbackAgent**:
    - Use if no other agent is suitable or if the query is ambiguous or conversational.
    - **Example queries**: "Hi", "Can you help me?", "Not sure what I need."

---

User Query: "{question}"

Based on the query, which agent should be invoked? Respond with only the agent's class name (e.g., LiveERPAgent, BusinessIntelligenceAgent).
Chosen Agent:
"""


class OrchestratorAgent:
    """
    The central agent that decides which specialized agent should handle a request.
    """

    def __init__(self, llm, config: SystemConfig):
        self.llm = llm
        self.config = config
        logger.info("OrchestratorAgent initialized.")

    async def route_request(self, question: str, has_image: bool = False) -> str:
        """
        Determines the best agent to handle the user's request.
        """
        logger.info(f"Orchestrator routing question: '{question}'")

        if has_image:
            logger.info("Image detected, routing to MultimodalAgent.")
            return "MultimodalAgent"

        if not self.llm:
            logger.error("Orchestrator's LLM is not configured.")
            return "FallbackAgent"

        prompt = ORCHESTRATOR_SYSTEM_PROMPT.format(question=question)
        chosen_agent = ""

        try:
            # Check the type of the LLM object without a hard import of vllm
            llm_type_name = type(self.llm).__name__

            if llm_type_name == 'LLM':
                from vllm import SamplingParams
                sampling_params = SamplingParams(temperature=0.0, max_tokens=20)
                outputs = self.llm.generate([prompt], sampling_params=sampling_params)
                chosen_agent = outputs[0].outputs[0].text.strip()
            else: # Assuming Hugging Face pipeline
                outputs = self.llm(prompt, max_new_tokens=20)
                chosen_agent = outputs[0]['generated_text'].replace(prompt, "").strip()
        
        except Exception as e:
            logger.error(f"Error during LLM call in Orchestrator: {e}")
            return "FallbackAgent"

        logger.info(f"LLM chose agent: {chosen_agent}")
        
        valid_agents = ["KnowledgeAgent", "BusinessIntelligenceAgent", "LiveERPAgent", "FallbackAgent"]
        if chosen_agent in valid_agents:
            return chosen_agent
        else:
            logger.warning(f"LLM returned an invalid agent name: '{chosen_agent}'. Using FallbackAgent.")
            return "FallbackAgent"