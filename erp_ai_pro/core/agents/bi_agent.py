# -*- coding: utf-8 -*-
"""
Business Intelligence Agent for ERP AI Pro
Acts as an interface to the powerful BI module.
"""

import logging
from typing import Dict, Any
import pandas as pd
import structlog

# Import the existing, powerful BI module
from erp_ai_pro.core.business_intelligence import BusinessIntelligence, BIConfig

logger = structlog.get_logger()


class BusinessIntelligenceAgent:
    """
    The specialized agent for handling complex business intelligence queries.
    It uses the main BusinessIntelligence class to perform its tasks.
    """

    def __init__(self, bi_config: BIConfig = None):
        self.bi_engine = BusinessIntelligence(bi_config)
        logger.info("BusinessIntelligenceAgent initialized.")

    async def execute(self, analysis_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        The main execution method for this agent.
        It runs a comprehensive business performance analysis.

        Args:
            analysis_request: A dictionary containing the necessary dataframes.
                              Example: {
                                  'sales_data': pd.DataFrame(...),
                                  'customer_data': pd.DataFrame(...)
                              }
        """
        logger.info(f"BusinessIntelligenceAgent executing request: {analysis_request.get('type')}")

        # This agent expects pre-loaded data. The data loading logic
        # will be handled by the Orchestrator or a dedicated data-loading tool.
        if not analysis_request.get("data"):
            return {"error": "No data provided for BI analysis."}

        try:
            results = await self.bi_engine.analyze_business_performance(analysis_request["data"])
            return {
                "status": "success",
                "analysis_results": results
            }
        except Exception as e:
            logger.error(f"BI Agent execution failed: {e}")
            return {"error": str(e)}
