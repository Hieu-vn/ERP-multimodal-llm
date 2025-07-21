# -*- coding: utf-8 -*-
"""
Live ERP Agent for ERP AI Pro
Handles real-time interactions with the ERP system APIs.
"""

import logging
from typing import Dict, Any, List

import structlog

# Import the tools this agent will use
from erp_ai_pro.core.tools import LiveERP_APITool, DataAnalysisTool

logger = structlog.get_logger()


class LiveERPAgent:
    """
    The specialized agent for executing live calls to ERP system APIs.
    It is equipped with a specific set of tools for this purpose.
    """

    def __init__(self):
        # Instantiate the toolsets this agent can use
        self.live_api_tool = LiveERP_APITool()
        self.data_analysis_tool = DataAnalysisTool()
        
        # Create a dispatch table to map tool names to methods
        self.tool_dispatch = {
            "get_product_stock_level": self.live_api_tool.get_product_stock_level,
            "get_customer_outstanding_balance": self.live_api_tool.get_customer_outstanding_balance,
            "perform_calculation": self.data_analysis_tool.perform_calculation,
        }
        logger.info("LiveERPAgent initialized.")

    async def execute(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        The main execution method for this agent.
        It finds and executes the requested tool with the given input.

        Args:
            tool_name: The name of the tool to execute (e.g., 'get_product_stock_level').
            tool_input: The arguments for the tool (e.g., {'product_id': 'PROD001'}).
        """
        logger.info(f"LiveERPAgent executing tool: '{tool_name}' with input: {tool_input}")

        if tool_name not in self.tool_dispatch:
            return {"error": f"Tool '{tool_name}' not found in LiveERPAgent's toolkit."}

        try:
            tool_function = self.tool_dispatch[tool_name]
            
            # The @tool decorator from LangChain makes the function directly callable
            # We pass the arguments to it using dictionary unpacking
            result = tool_function.func(**tool_input)
            
            return {
                "status": "success",
                "tool_name": tool_name,
                "result": result
            }
        except Exception as e:
            logger.error(f"LiveERPAgent tool execution failed: {e}")
            return {"error": str(e)}
