# -*- coding: utf-8 -*-
"""
Business Intelligence Module for Enhanced ERP AI Pro
Features: Predictive Analytics, Anomaly Detection, Advanced Reporting, Forecasting
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
import json

# ML Libraries
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
import xgboost as xgb
import lightgbm as lgb
from prophet import Prophet
import optuna

# Data Processing
import polars as pl
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import scipy.stats as stats

# Visualization (for reports)
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Utils
import structlog
from concurrent.futures import ThreadPoolExecutor
import asyncio

logger = structlog.get_logger()

@dataclass
class BIConfig:
    """Configuration for Business Intelligence module."""
    
    # Model Configuration
    forecasting_model: str = "prophet"  # prophet, arima, xgboost, ensemble
    anomaly_detection_model: str = "isolation_forest"  # isolation_forest, one_class_svm
    clustering_model: str = "kmeans"  # kmeans, dbscan, gaussian_mixture
    
    # Data Configuration
    min_data_points: int = 30  # Minimum data points for analysis
    forecast_horizon: int = 90  # Days to forecast
    confidence_interval: float = 0.95
    
    # Performance Configuration
    max_workers: int = 4  # For parallel processing
    cache_timeout: int = 3600  # Cache timeout in seconds
    
    # Feature Engineering
    lag_features: List[int] = None  # Auto-regression lags
    seasonal_features: bool = True
    holiday_features: bool = True
    
    def __post_init__(self):
        if self.lag_features is None:
            self.lag_features = [1, 7, 30]  # 1 day, 1 week, 1 month

class DataProcessor:
    """Advanced data processing for BI analytics."""
    
    def __init__(self, config: BIConfig):
        self.config = config
        self.scaler = StandardScaler()
        
    async def process_sales_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Process sales data for analysis."""
        try:
            # Ensure datetime index
            if 'date' in data.columns:
                data['date'] = pd.to_datetime(data['date'])
                data = data.set_index('date')
            
            # Sort by date
            data = data.sort_index()
            
            # Handle missing values
            data = data.fillna(method='ffill').fillna(method='bfill')
            
            # Feature engineering
            data = await self._add_time_features(data)
            data = await self._add_lag_features(data)
            data = await self._add_seasonal_features(data)
            
            return data
            
        except Exception as e:
            logger.error(f"Error processing sales data: {e}")
            raise

    async def _add_time_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features."""
        data['year'] = data.index.year
        data['month'] = data.index.month
        data['day'] = data.index.day
        data['weekday'] = data.index.weekday
        data['quarter'] = data.index.quarter
        data['is_weekend'] = data.index.weekday >= 5
        data['is_month_end'] = data.index.is_month_end
        data['is_quarter_end'] = data.index.is_quarter_end
        
        return data

    async def _add_lag_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add lagged features for time series analysis."""
        for col in ['revenue', 'sales_volume', 'profit']:
            if col in data.columns:
                for lag in self.config.lag_features:
                    data[f'{col}_lag_{lag}'] = data[col].shift(lag)
        
        return data

    async def _add_seasonal_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add seasonal decomposition features."""
        if not self.config.seasonal_features:
            return data
            
        for col in ['revenue', 'sales_volume']:
            if col in data.columns and len(data) >= 24:  # Need at least 2 years
                try:
                    decomposition = seasonal_decompose(data[col], model='additive', period=12)
                    data[f'{col}_trend'] = decomposition.trend
                    data[f'{col}_seasonal'] = decomposition.seasonal
                    data[f'{col}_residual'] = decomposition.resid
                except Exception as e:
                    logger.warning(f"Seasonal decomposition failed for {col}: {e}")
        
        return data

class ForecastingEngine:
    """Advanced forecasting engine with multiple models."""
    
    def __init__(self, config: BIConfig):
        self.config = config
        self.models = {}
        self.model_performance = {}
        
    async def forecast_revenue(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Forecast revenue using multiple models."""
        try:
            # Prepare data
            if len(data) < self.config.min_data_points:
                raise ValueError(f"Insufficient data points: {len(data)} < {self.config.min_data_points}")
            
            # Run multiple models in parallel
            tasks = [
                self._forecast_prophet(data),
                self._forecast_arima(data),
                self._forecast_xgboost(data),
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results
            forecasts = {}
            for i, result in enumerate(results):
                if not isinstance(result, Exception):
                    model_name = ['prophet', 'arima', 'xgboost'][i]
                    forecasts[model_name] = result
            
            # Ensemble forecast
            ensemble_forecast = await self._ensemble_forecast(forecasts)
            
            return {
                'individual_forecasts': forecasts,
                'ensemble_forecast': ensemble_forecast,
                'model_performance': self.model_performance,
                'forecast_horizon': self.config.forecast_horizon,
                'confidence_interval': self.config.confidence_interval
            }
            
        except Exception as e:
            logger.error(f"Forecasting error: {e}")
            raise

    async def _forecast_prophet(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Prophet forecasting model."""
        try:
            # Prepare data for Prophet
            df = data.reset_index()
            df = df.rename(columns={'date': 'ds', 'revenue': 'y'})
            
            # Create and fit model
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                changepoint_prior_scale=0.05,
                interval_width=self.config.confidence_interval
            )
            
            model.fit(df)
            
            # Make future predictions
            future = model.make_future_dataframe(periods=self.config.forecast_horizon)
            forecast = model.predict(future)
            
            # Calculate performance metrics
            y_true = df['y'].values
            y_pred = forecast['yhat'][:len(y_true)].values
            
            performance = {
                'mse': mean_squared_error(y_true, y_pred),
                'mae': mean_absolute_error(y_true, y_pred),
                'mape': np.mean(np.abs((y_true - y_pred) / y_true)) * 100
            }
            
            self.model_performance['prophet'] = performance
            
            return {
                'forecast': forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(self.config.forecast_horizon),
                'performance': performance,
                'model': 'prophet'
            }
            
        except Exception as e:
            logger.error(f"Prophet forecasting error: {e}")
            return None

    async def _forecast_arima(self, data: pd.DataFrame) -> Dict[str, Any]:
        """ARIMA forecasting model."""
        try:
            # Check stationarity
            revenue_series = data['revenue'].dropna()
            
            # Auto ARIMA order selection
            order = await self._find_optimal_arima_order(revenue_series)
            
            # Fit ARIMA model
            model = ARIMA(revenue_series, order=order)
            fitted_model = model.fit()
            
            # Make forecast
            forecast = fitted_model.forecast(steps=self.config.forecast_horizon)
            forecast_ci = fitted_model.get_forecast(steps=self.config.forecast_horizon).conf_int()
            
            # Calculate performance
            y_true = revenue_series.values
            y_pred = fitted_model.fittedvalues.values
            
            performance = {
                'mse': mean_squared_error(y_true, y_pred),
                'mae': mean_absolute_error(y_true, y_pred),
                'aic': fitted_model.aic,
                'bic': fitted_model.bic
            }
            
            self.model_performance['arima'] = performance
            
            return {
                'forecast': forecast.values,
                'forecast_ci': forecast_ci.values,
                'performance': performance,
                'model': 'arima',
                'order': order
            }
            
        except Exception as e:
            logger.error(f"ARIMA forecasting error: {e}")
            return None

    async def _forecast_xgboost(self, data: pd.DataFrame) -> Dict[str, Any]:
        """XGBoost forecasting model."""
        try:
            # Prepare features
            feature_cols = [col for col in data.columns if col not in ['revenue']]
            X = data[feature_cols].dropna()
            y = data['revenue'].loc[X.index]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Optimize hyperparameters
            study = optuna.create_study(direction='minimize')
            study.optimize(
                lambda trial: self._xgboost_objective(trial, X_train, y_train, X_test, y_test),
                n_trials=50
            )
            
            # Train final model
            model = xgb.XGBRegressor(**study.best_params, random_state=42)
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate performance
            performance = {
                'mse': mean_squared_error(y_test, y_pred),
                'mae': mean_absolute_error(y_test, y_pred),
                'best_params': study.best_params
            }
            
            self.model_performance['xgboost'] = performance
            
            # Generate future forecast (simplified)
            last_features = X.iloc[-1:].values
            future_forecast = []
            
            for _ in range(self.config.forecast_horizon):
                pred = model.predict(last_features)[0]
                future_forecast.append(pred)
                # Update features for next prediction (simplified)
                last_features = np.roll(last_features, -1)
                last_features[0, -1] = pred
            
            return {
                'forecast': future_forecast,
                'performance': performance,
                'model': 'xgboost',
                'feature_importance': dict(zip(feature_cols, model.feature_importances_))
            }
            
        except Exception as e:
            logger.error(f"XGBoost forecasting error: {e}")
            return None

    def _xgboost_objective(self, trial, X_train, y_train, X_test, y_test):
        """Objective function for XGBoost hyperparameter optimization."""
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 50, 300),
            'max_depth': trial.suggest_int('max_depth', 3, 10),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
            'subsample': trial.suggest_float('subsample', 0.8, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.8, 1.0),
        }
        
        model = xgb.XGBRegressor(**params, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        return mean_squared_error(y_test, y_pred)

    async def _find_optimal_arima_order(self, series: pd.Series) -> Tuple[int, int, int]:
        """Find optimal ARIMA order using AIC."""
        best_aic = float('inf')
        best_order = (1, 1, 1)
        
        # Grid search for optimal parameters
        for p in range(3):
            for d in range(2):
                for q in range(3):
                    try:
                        model = ARIMA(series, order=(p, d, q))
                        fitted = model.fit()
                        if fitted.aic < best_aic:
                            best_aic = fitted.aic
                            best_order = (p, d, q)
                    except:
                        continue
        
        return best_order

    async def _ensemble_forecast(self, forecasts: Dict[str, Any]) -> Dict[str, Any]:
        """Create ensemble forecast from multiple models."""
        if not forecasts:
            return None
        
        # Weight models based on performance
        weights = {}
        total_weight = 0
        
        for model_name, forecast in forecasts.items():
            if model_name in self.model_performance:
                # Lower MSE gets higher weight
                weight = 1.0 / (1.0 + self.model_performance[model_name]['mse'])
                weights[model_name] = weight
                total_weight += weight
        
        # Normalize weights
        for model_name in weights:
            weights[model_name] /= total_weight
        
        # Combine forecasts
        ensemble_values = []
        for model_name, forecast in forecasts.items():
            if model_name in weights:
                forecast_values = forecast.get('forecast', [])
                if isinstance(forecast_values, pd.DataFrame):
                    forecast_values = forecast_values['yhat'].values
                elif isinstance(forecast_values, np.ndarray):
                    forecast_values = forecast_values.tolist()
                
                weighted_values = [v * weights[model_name] for v in forecast_values]
                ensemble_values.append(weighted_values)
        
        # Average weighted forecasts
        if ensemble_values:
            ensemble_forecast = np.mean(ensemble_values, axis=0)
            return {
                'forecast': ensemble_forecast.tolist(),
                'weights': weights,
                'model': 'ensemble'
            }
        
        return None

class AnomalyDetector:
    """Advanced anomaly detection for business metrics."""
    
    def __init__(self, config: BIConfig):
        self.config = config
        self.models = {}
        
    async def detect_anomalies(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Detect anomalies in business data."""
        try:
            results = {}
            
            # Detect revenue anomalies
            if 'revenue' in data.columns:
                revenue_anomalies = await self._detect_revenue_anomalies(data)
                results['revenue_anomalies'] = revenue_anomalies
            
            # Detect customer behavior anomalies
            if 'customer_transactions' in data.columns:
                customer_anomalies = await self._detect_customer_anomalies(data)
                results['customer_anomalies'] = customer_anomalies
            
            # Detect inventory anomalies
            if 'inventory_level' in data.columns:
                inventory_anomalies = await self._detect_inventory_anomalies(data)
                results['inventory_anomalies'] = inventory_anomalies
            
            return results
            
        except Exception as e:
            logger.error(f"Anomaly detection error: {e}")
            raise

    async def _detect_revenue_anomalies(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Detect revenue anomalies using Isolation Forest."""
        try:
            # Prepare features
            features = ['revenue']
            if 'profit' in data.columns:
                features.append('profit')
            if 'sales_volume' in data.columns:
                features.append('sales_volume')
            
            X = data[features].dropna()
            
            # Fit Isolation Forest
            isolation_forest = IsolationForest(
                contamination=0.1,  # Expect 10% anomalies
                random_state=42,
                n_estimators=100
            )
            
            anomaly_labels = isolation_forest.fit_predict(X)
            anomaly_scores = isolation_forest.decision_function(X)
            
            # Identify anomalies
            anomalies = X[anomaly_labels == -1]
            
            return {
                'anomaly_dates': anomalies.index.tolist(),
                'anomaly_scores': anomaly_scores[anomaly_labels == -1].tolist(),
                'total_anomalies': len(anomalies),
                'anomaly_percentage': len(anomalies) / len(X) * 100,
                'model': 'isolation_forest'
            }
            
        except Exception as e:
            logger.error(f"Revenue anomaly detection error: {e}")
            return None

    async def _detect_customer_anomalies(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Detect customer behavior anomalies."""
        try:
            # Statistical anomaly detection
            customer_data = data['customer_transactions'].dropna()
            
            # Calculate z-scores
            z_scores = np.abs(stats.zscore(customer_data))
            threshold = 3  # 3 standard deviations
            
            anomalies = customer_data[z_scores > threshold]
            
            return {
                'anomaly_dates': anomalies.index.tolist(),
                'anomaly_values': anomalies.values.tolist(),
                'total_anomalies': len(anomalies),
                'threshold': threshold,
                'model': 'statistical'
            }
            
        except Exception as e:
            logger.error(f"Customer anomaly detection error: {e}")
            return None

    async def _detect_inventory_anomalies(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Detect inventory level anomalies."""
        try:
            inventory_data = data['inventory_level'].dropna()
            
            # Use rolling statistics for anomaly detection
            rolling_mean = inventory_data.rolling(window=7).mean()
            rolling_std = inventory_data.rolling(window=7).std()
            
            # Detect anomalies outside 2 standard deviations
            lower_bound = rolling_mean - 2 * rolling_std
            upper_bound = rolling_mean + 2 * rolling_std
            
            anomalies = inventory_data[(inventory_data < lower_bound) | (inventory_data > upper_bound)]
            
            return {
                'anomaly_dates': anomalies.index.tolist(),
                'anomaly_values': anomalies.values.tolist(),
                'total_anomalies': len(anomalies),
                'model': 'rolling_statistics'
            }
            
        except Exception as e:
            logger.error(f"Inventory anomaly detection error: {e}")
            return None

class CustomerSegmentation:
    """Advanced customer segmentation and analysis."""
    
    def __init__(self, config: BIConfig):
        self.config = config
        
    async def segment_customers(self, customer_data: pd.DataFrame) -> Dict[str, Any]:
        """Segment customers using RFM analysis and clustering."""
        try:
            # RFM Analysis
            rfm_data = await self._calculate_rfm_scores(customer_data)
            
            # K-means clustering
            clusters = await self._perform_clustering(rfm_data)
            
            # Analyze segments
            segment_analysis = await self._analyze_segments(rfm_data, clusters)
            
            return {
                'rfm_scores': rfm_data,
                'clusters': clusters,
                'segment_analysis': segment_analysis,
                'recommendations': await self._generate_recommendations(segment_analysis)
            }
            
        except Exception as e:
            logger.error(f"Customer segmentation error: {e}")
            raise

    async def _calculate_rfm_scores(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate RFM (Recency, Frequency, Monetary) scores."""
        current_date = data['order_date'].max()
        
        rfm = data.groupby('customer_id').agg({
            'order_date': lambda x: (current_date - x.max()).days,  # Recency
            'order_id': 'count',  # Frequency
            'revenue': 'sum'  # Monetary
        }).reset_index()
        
        rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
        
        # Calculate RFM scores (1-5 scale)
        rfm['recency_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
        rfm['frequency_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
        rfm['monetary_score'] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])
        
        # Combined RFM score
        rfm['rfm_score'] = rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str) + rfm['monetary_score'].astype(str)
        
        return rfm

    async def _perform_clustering(self, rfm_data: pd.DataFrame) -> Dict[str, Any]:
        """Perform K-means clustering on RFM data."""
        features = ['recency', 'frequency', 'monetary']
        X = rfm_data[features]
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Find optimal number of clusters
        optimal_clusters = await self._find_optimal_clusters(X_scaled)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=optimal_clusters, random_state=42)
        clusters = kmeans.fit_predict(X_scaled)
        
        rfm_data['cluster'] = clusters
        
        return {
            'cluster_labels': clusters,
            'cluster_centers': kmeans.cluster_centers_,
            'optimal_clusters': optimal_clusters,
            'inertia': kmeans.inertia_
        }

    async def _find_optimal_clusters(self, X: np.ndarray) -> int:
        """Find optimal number of clusters using elbow method."""
        inertias = []
        k_range = range(2, 11)
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(X)
            inertias.append(kmeans.inertia_)
        
        # Find elbow point (simplified)
        diffs = np.diff(inertias)
        elbow_point = np.argmax(diffs) + 2
        
        return min(elbow_point, 6)  # Cap at 6 clusters

    async def _analyze_segments(self, rfm_data: pd.DataFrame, clusters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze customer segments."""
        segment_analysis = {}
        
        for cluster_id in rfm_data['cluster'].unique():
            cluster_data = rfm_data[rfm_data['cluster'] == cluster_id]
            
            analysis = {
                'size': len(cluster_data),
                'avg_recency': cluster_data['recency'].mean(),
                'avg_frequency': cluster_data['frequency'].mean(),
                'avg_monetary': cluster_data['monetary'].mean(),
                'total_value': cluster_data['monetary'].sum(),
                'percentage': len(cluster_data) / len(rfm_data) * 100
            }
            
            # Segment labeling
            if analysis['avg_recency'] <= 30 and analysis['avg_frequency'] >= 5 and analysis['avg_monetary'] >= 1000:
                analysis['label'] = 'VIP Customers'
            elif analysis['avg_recency'] <= 60 and analysis['avg_frequency'] >= 3:
                analysis['label'] = 'Loyal Customers'
            elif analysis['avg_recency'] <= 90 and analysis['avg_monetary'] >= 500:
                analysis['label'] = 'Potential Loyalists'
            elif analysis['avg_recency'] > 180:
                analysis['label'] = 'At Risk'
            else:
                analysis['label'] = 'New Customers'
            
            segment_analysis[f'cluster_{cluster_id}'] = analysis
        
        return segment_analysis

    async def _generate_recommendations(self, segment_analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate marketing recommendations for each segment."""
        recommendations = {}
        
        for segment_id, analysis in segment_analysis.items():
            label = analysis['label']
            
            if label == 'VIP Customers':
                recommendations[segment_id] = [
                    'Offer exclusive products and early access',
                    'Provide personalized customer service',
                    'Create VIP loyalty program',
                    'Request referrals and testimonials'
                ]
            elif label == 'Loyal Customers':
                recommendations[segment_id] = [
                    'Reward loyalty with special discounts',
                    'Cross-sell complementary products',
                    'Encourage social media engagement',
                    'Provide excellent customer support'
                ]
            elif label == 'Potential Loyalists':
                recommendations[segment_id] = [
                    'Send targeted product recommendations',
                    'Offer limited-time promotions',
                    'Provide educational content',
                    'Implement win-back campaigns'
                ]
            elif label == 'At Risk':
                recommendations[segment_id] = [
                    'Send reactivation campaigns',
                    'Offer significant discounts',
                    'Conduct feedback surveys',
                    'Provide personalized offers'
                ]
            else:  # New Customers
                recommendations[segment_id] = [
                    'Welcome email series',
                    'Onboarding tutorials',
                    'First purchase incentives',
                    'Social proof and testimonials'
                ]
        
        return recommendations

class BusinessIntelligence:
    """Main Business Intelligence class combining all analytics."""
    
    def __init__(self, config: BIConfig = None):
        self.config = config or BIConfig()
        self.data_processor = DataProcessor(self.config)
        self.forecasting_engine = ForecastingEngine(self.config)
        self.anomaly_detector = AnomalyDetector(self.config)
        self.customer_segmentation = CustomerSegmentation(self.config)
        
    async def analyze_business_performance(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Comprehensive business performance analysis."""
        try:
            results = {}
            
            # Sales forecasting
            if 'sales_data' in data:
                processed_sales = await self.data_processor.process_sales_data(data['sales_data'])
                forecast_results = await self.forecasting_engine.forecast_revenue(processed_sales)
                results['sales_forecast'] = forecast_results
            
            # Anomaly detection
            if 'metrics_data' in data:
                anomaly_results = await self.anomaly_detector.detect_anomalies(data['metrics_data'])
                results['anomalies'] = anomaly_results
            
            # Customer segmentation
            if 'customer_data' in data:
                segmentation_results = await self.customer_segmentation.segment_customers(data['customer_data'])
                results['customer_segments'] = segmentation_results
            
            # Business insights
            insights = await self._generate_business_insights(results)
            results['insights'] = insights
            
            return results
            
        except Exception as e:
            logger.error(f"Business analysis error: {e}")
            raise

    async def _generate_business_insights(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable business insights."""
        insights = []
        
        # Revenue forecast insights
        if 'sales_forecast' in analysis_results:
            forecast = analysis_results['sales_forecast']
            if 'ensemble_forecast' in forecast:
                ensemble = forecast['ensemble_forecast']
                if ensemble and 'forecast' in ensemble:
                    avg_forecast = np.mean(ensemble['forecast'])
                    insights.append({
                        'type': 'forecast',
                        'priority': 'high',
                        'title': 'Revenue Forecast',
                        'message': f'Expected average daily revenue: ${avg_forecast:,.2f}',
                        'action': 'Monitor daily performance against forecast'
                    })
        
        # Anomaly insights
        if 'anomalies' in analysis_results:
            anomalies = analysis_results['anomalies']
            if 'revenue_anomalies' in anomalies:
                rev_anomalies = anomalies['revenue_anomalies']
                if rev_anomalies and rev_anomalies['total_anomalies'] > 0:
                    insights.append({
                        'type': 'anomaly',
                        'priority': 'high',
                        'title': 'Revenue Anomalies Detected',
                        'message': f'Found {rev_anomalies["total_anomalies"]} revenue anomalies',
                        'action': 'Investigate unusual revenue patterns'
                    })
        
        # Customer segment insights
        if 'customer_segments' in analysis_results:
            segments = analysis_results['customer_segments']
            if 'segment_analysis' in segments:
                for segment_id, analysis in segments['segment_analysis'].items():
                    if analysis['label'] == 'At Risk' and analysis['percentage'] > 20:
                        insights.append({
                            'type': 'customer_retention',
                            'priority': 'medium',
                            'title': 'High At-Risk Customer Percentage',
                            'message': f'{analysis["percentage"]:.1f}% of customers are at risk',
                            'action': 'Implement retention campaigns'
                        })
        
        return insights

# Factory function
def create_business_intelligence(config: BIConfig = None) -> BusinessIntelligence:
    """Create and return a Business Intelligence instance."""
    return BusinessIntelligence(config)