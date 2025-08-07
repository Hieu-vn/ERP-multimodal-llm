# -*- coding: utf-8 -*-
"""
Live ERP Agent for ERP AI Pro
Handles real-time interactions with the ERP system by executing specific tools.
"""

import logging
from typing import Dict, Any, List, Callable

import structlog

# Import all available tools from the tools layer
from erp_ai_pro.tools import tools

logger = structlog.get_logger()

class LiveERPAgent:
    """
    The specialized agent for executing live calls to the ERP system.
    It acts as a dispatcher, calling the appropriate tool based on the orchestrator's request.
    """

    def __init__(self):
        # Instantiate all available tools
        self.available_tools = {
            # Base Tools
            "get_current_date": tools.GetCurrentDateTool(),
            "perform_calculation": tools.PerformCalculationTool(),
            
            # Task Management Tools
            "create_task": tools.CreateTaskTool(),
            "get_tasks_by_assignee": tools.GetTasksByAssigneeTool(),
            "get_tasks_by_project": tools.GetTasksByProjectTool(),
            "update_task_status": tools.UpdateTaskStatusTool(),

            # Placeholder Tools
            "graph_erp_lookup": tools.GraphERPLookupTool(),
            "vector_search": tools.VectorSearchTool(),
        }
        logger.info(f"LiveERPAgent initialized with {len(self.available_tools)} tools.")

    def get_tool(self, tool_name: str) -> Optional[Callable]:
        """Returns the runnable method of a tool if it exists."""
        tool = self.available_tools.get(tool_name)
        return tool.run if tool else None

    async def execute(self, tool_name: str, tool_input: Dict[str, Any], allowed_tools: List[str]) -> Dict[str, Any]:
        """
        The main execution method for this agent.
        It finds and executes the requested tool with the given input, respecting RBAC.

        Args:
            tool_name: The name of the tool to execute.
            tool_input: The arguments for the tool.
            allowed_tools: The list of tools the user is allowed to run.
        """
        logger.info(f"LiveERPAgent attempting to execute tool: '{tool_name}' with input: {tool_input}")

        # 1. RBAC Check
        if tool_name not in allowed_tools:
            error_msg = f"Access Denied: Role does not have permission to use tool '{tool_name}'."
            logger.warning(error_msg)
            return {"error": error_msg}

        # 2. Get Tool
        tool_function = self.get_tool(tool_name)
        if not tool_function:
            error_msg = f"Tool '{tool_name}' not found in LiveERPAgent's toolkit."
            logger.error(error_msg)
            return {"error": error_msg}

        # 3. Execute Tool
        try:
            # Note: LangChain tools often use .run() or .invoke(). We standardize on .run()
            result = tool_function(**tool_input)
            
            return {
                "status": "success",
                "tool_name": tool_name,
                "result": result
            }
        except Exception as e:
            logger.error(f"LiveERPAgent tool '{tool_name}' execution failed: {e}", exc_info=True)
            return {"error": str(e)}