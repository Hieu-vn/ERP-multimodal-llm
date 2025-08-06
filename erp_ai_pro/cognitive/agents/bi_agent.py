# -*- coding: utf-8 -*-
"""
Business Intelligence Agent for ERP AI Pro
Acts as an interface to the powerful BI module.
"""

import logging
from typing import Dict, Any
import pandas as pd
import numpy as np
import structlog

# Import the existing, powerful BI module
from erp_ai_pro.core.business_intelligence import BusinessIntelligence, BIConfig

logger = structlog.get_logger()

def create_sample_data() -> Dict[str, pd.DataFrame]:
    """Creates sample data for the BI agent to analyze."""
    # Sample sales data
    sales_data = {
        'date': pd.to_datetime(pd.date_range(start='2023-01-01', periods=100)),
        'revenue': np.random.randint(1000, 5000, size=100),
        'sales_volume': np.random.randint(50, 200, size=100),
        'profit': np.random.randint(200, 1000, size=100)
    }
    sales_df = pd.DataFrame(sales_data)

    # Sample metrics data
    metrics_data = {
        'date': pd.to_datetime(pd.date_range(start='2023-01-01', periods=100)),
        'revenue': sales_df['revenue'],
        'customer_transactions': np.random.randint(10, 50, size=100),
        'inventory_level': np.random.randint(500, 1000, size=100)
    }
    metrics_df = pd.DataFrame(metrics_data)

    # Sample customer data
    customer_data = {
        'customer_id': [f'CUST{i:03}' for i in range(20)],
        'order_date': pd.to_datetime(np.random.choice(pd.date_range(start='2023-01-01', periods=100), size=50)),
        'order_id': [f'ORD{i:03}' for i in range(50)],
        'revenue': np.random.randint(100, 1000, size=50)
    }
    customer_df = pd.DataFrame(customer_data)
    
    return {
        "sales_data": sales_df,
        "metrics_data": metrics_df,
        "customer_data": customer_df
    }

def summarize_results(results: Dict[str, Any]) -> str:
    """Summarizes the BI analysis results into a human-readable string."""
    summary = "Business Intelligence Analysis Summary:\n\n"

    if "sales_forecast" in results and results["sales_forecast"]:
        summary += "**Sales Forecast:**\n"
        ensemble_forecast = results["sales_forecast"].get("ensemble_forecast", {})
        if ensemble_forecast and "forecast" in ensemble_forecast:
            avg_forecast = np.mean(ensemble_forecast['forecast'])
            summary += f"- The average daily revenue is forecasted to be ${avg_forecast:,.2f}.\n"
        summary += "\n"

    if "anomalies" in results and results["anomalies"]:
        summary += "**Anomaly Detection:**\n"
        revenue_anomalies = results["anomalies"].get("revenue_anomalies", {})
        if revenue_anomalies and revenue_anomalies["total_anomalies"] > 0:
            summary += f"- Detected {revenue_anomalies['total_anomalies']} anomalies in revenue data.\n"
        else:
            summary += "- No significant revenue anomalies detected.\n"
        summary += "\n"

    if "customer_segments" in results and results["customer_segments"]:
        summary += "**Customer Segmentation:**\n"
        segment_analysis = results["customer_segments"].get("segment_analysis", {})
        if segment_analysis:
            for segment_id, analysis in segment_analysis.items():
                summary += f"- {analysis['label']}: {analysis['size']} customers ({analysis['percentage']:.1f}% of total)\n"
        summary += "\n"

    if "insights" in results and results["insights"]:
        summary += "**Actionable Insights:**\n"
        for insight in results["insights"]:
            summary += f"- **{insight['title']}**: {insight['message']}. **Action**: {insight['action']}.\n"

    return summary

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
                              If empty, sample data will be generated.
        """
        logger.info(f"BusinessIntelligenceAgent executing request.")

        data_to_analyze = analysis_request.get("data")
        if not data_to_analyze:
            logger.info("No data provided, generating sample data for BI analysis.")
            data_to_analyze = create_sample_data()

        try:
            results = await self.bi_engine.analyze_business_performance(data_to_analyze)
            summary = summarize_results(results)
            return {
                "status": "success",
                "summary": summary,
                "raw_results": results
            }
        except Exception as e:
            logger.error(f"BI Agent execution failed: {e}")
            return {"error": str(e)}
