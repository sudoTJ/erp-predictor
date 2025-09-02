"""
Business insights generation utilities
Enhanced with DGPT AI-powered insights
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from models.schemas import PredictionPoint
import logging
import asyncio

logger = logging.getLogger(__name__)

class InsightGenerator:
    """Generate business insights from predictions and historical data"""
    
    def __init__(self):
        # Lazy import to avoid circular dependencies
        self._dgpt_client = None
    
    @property
    def dgpt_client(self):
        """Lazy load DGPT client to avoid circular imports"""
        if self._dgpt_client is None:
            try:
                from services.dgpt_client import dgpt_client
                self._dgpt_client = dgpt_client
            except ImportError as e:
                logger.warning(f"DGPT client not available: {e}")
                self._dgpt_client = None
        return self._dgpt_client
    
    async def generate_insights_async(self, predictions: List[PredictionPoint], 
                                    prediction_type: str, 
                                    historical_df: pd.DataFrame = None,
                                    entity_id: str = None,
                                    prediction_data: Dict[str, Any] = None) -> List[str]:
        """Generate enhanced insights using DGPT + fallback static insights"""
        try:
            insights = []
            
            if not predictions:
                return ["Insufficient data for insights"]
            
            # Try to generate AI-powered insights first
            ai_insights = await self._generate_ai_insights(
                predictions, prediction_type, historical_df, entity_id, prediction_data
            )
            
            if ai_insights:
                logger.info(f"Using {len(ai_insights)} AI-powered insights")
                insights.extend(ai_insights)
            else:
                logger.info("Falling back to static insights generation")
                # Fallback to static insights
                static_insights = self._generate_static_insights(predictions, prediction_type, historical_df)
                insights.extend(static_insights)
            
            return insights[:6]  # Limit to top 6 insights
            
        except Exception as e:
            logger.error(f"Enhanced insight generation error: {e}")
            # Final fallback to basic static insights
            return self._generate_static_insights(predictions, prediction_type, historical_df)
    
    async def generate_insights(self, predictions: List[PredictionPoint],
                         prediction_type: str, 
                         historical_df: pd.DataFrame = None,
                         entity_id: str = None,
                         prediction_data: Dict[str, Any] = None) -> List[str]:
        """Generate business insights based on predictions (async version)"""
        try:
            logger.info("Starting async insights generation")
            return await self.generate_insights_async(predictions, prediction_type, historical_df, entity_id, prediction_data)
        except Exception as e:
            logger.error(f"Async insights generation error: {e}")
            logger.info("Falling back to static insights")
            return self._generate_static_insights(predictions, prediction_type, historical_df)
    
    async def _generate_ai_insights(self, 
                                   predictions: List[PredictionPoint], 
                                   prediction_type: str, 
                                   historical_df: pd.DataFrame = None,
                                   entity_id: str = None,
                                   prediction_data: Dict[str, Any] = None) -> List[str]:
        """Generate AI-powered insights using DGPT"""
        try:
            logger.info(f"Starting AI insights generation for {prediction_type}:{entity_id}")
            
            if not self.dgpt_client:
                logger.warning("DGPT client not available - skipping AI insights")
                return []
            
            # Prepare prediction data for DGPT
            if not prediction_data:
                logger.debug("Creating prediction data payload for AI analysis")
                prediction_data = {
                    'predictions': [
                        {
                            'predicted_value': float(p.predicted_value),
                            'confidence': float(p.confidence),
                            'date': p.date.isoformat() if hasattr(p.date, 'isoformat') else str(p.date)
                        } for p in predictions
                    ],
                    'prediction_type': prediction_type,
                    'entity_id': entity_id or 'unknown',
                    'metadata': {
                        'model_used': 'linear_regression',
                        'data_points': len(predictions)
                    }
                }
                logger.debug(f"Prepared {len(prediction_data['predictions'])} prediction points for AI analysis")
            
            # Prepare historical context if available
            historical_context = None
            if historical_df is not None and not historical_df.empty:
                try:
                    logger.debug("Processing historical context for AI analysis")
                    logger.debug(f"Historical dataframe shape: {historical_df.shape}")
                    logger.debug(f"Historical dataframe columns: {list(historical_df.columns)}")
                    logger.debug(f"Historical dataframe index type: {type(historical_df.index)}")
                    
                    # Safely handle date range
                    date_range = "unknown"
                    try:
                        if hasattr(historical_df, 'index') and len(historical_df.index) > 0:
                            min_date = historical_df.index.min()
                            max_date = historical_df.index.max()
                            # Convert timestamps to strings safely
                            min_str = min_date.strftime('%Y-%m-%d') if hasattr(min_date, 'strftime') else str(min_date)
                            max_str = max_date.strftime('%Y-%m-%d') if hasattr(max_date, 'strftime') else str(max_date)
                            date_range = f"{min_str} to {max_str}"
                            logger.debug(f"Historical date range: {date_range}")
                    except Exception as date_error:
                        logger.warning(f"Could not determine date range: {date_error}")
                        date_range = "date_range_unknown"
                    
                    # Safely calculate average value
                    avg_value = 0.0
                    try:
                        if len(historical_df.columns) > 0:
                            # Get the first numeric column
                            numeric_cols = historical_df.select_dtypes(include=[np.number]).columns
                            if len(numeric_cols) > 0:
                                first_numeric_col = numeric_cols[0]
                                mean_val = historical_df[first_numeric_col].mean()
                                avg_value = float(mean_val) if pd.notna(mean_val) else 0.0
                                logger.debug(f"Historical average value ({first_numeric_col}): {avg_value}")
                            else:
                                logger.warning("No numeric columns found in historical data")
                    except Exception as avg_error:
                        logger.warning(f"Could not calculate historical average: {avg_error}")
                        avg_value = 0.0
                    
                    historical_context = {
                        'data_points': len(historical_df),
                        'date_range': date_range,
                        'avg_value': avg_value
                    }
                    logger.info(f"Historical context prepared: {historical_context}")
                    
                except Exception as ctx_error:
                    logger.error(f"Error preparing historical context: {ctx_error}")
                    historical_context = {
                        'data_points': len(historical_df) if historical_df is not None else 0,
                        'date_range': 'context_error',
                        'avg_value': 0.0
                    }
            else:
                logger.debug("No historical context available")
            
            logger.info("Calling DGPT API for AI insights generation")
            # Generate AI insights
            ai_insights = await self.dgpt_client.generate_insights(
                prediction_data, prediction_type, historical_context
            )
            
            if ai_insights:
                logger.info(f"Successfully generated {len(ai_insights)} AI insights")
                logger.debug(f"AI insights: {ai_insights}")
            else:
                logger.warning("DGPT returned no insights")
            
            return ai_insights
            
        except Exception as e:
            logger.error(f"AI insights generation error: {e}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Prediction type: {prediction_type}, Entity: {entity_id}")
            if historical_df is not None:
                logger.error(f"Historical DF info - Shape: {historical_df.shape}, Columns: {list(historical_df.columns)}")
            return []
    
    def _generate_static_insights(self, predictions: List[PredictionPoint], 
                                 prediction_type: str, 
                                 historical_df: pd.DataFrame = None) -> List[str]:
        """Generate static rule-based insights (fallback method)"""
        try:
            insights = []
            
            if not predictions:
                return ["Insufficient data for insights"]
            
            # Calculate trend analysis
            trend_insights = self._analyze_trend(predictions, prediction_type)
            insights.extend(trend_insights)
            
            # Add confidence-based insights
            confidence_insights = self._analyze_confidence(predictions)
            insights.extend(confidence_insights)
            
            # Add historical context insights
            if historical_df is not None and not historical_df.empty:
                context_insights = self._analyze_historical_context(predictions, historical_df, prediction_type)
                insights.extend(context_insights)
            
            # Add prediction type specific insights
            specific_insights = self._get_type_specific_insights(predictions, prediction_type)
            insights.extend(specific_insights)
            
            return insights[:6]  # Limit to top 6 insights
            
        except Exception as e:
            logger.error(f"Static insight generation error: {e}")
            return ["Unable to generate detailed insights - basic trend analysis applied"]
    
    def _analyze_trend(self, predictions: List[PredictionPoint], prediction_type: str) -> List[str]:
        """Analyze trend from predictions"""
        insights = []
        
        if len(predictions) < 2:
            return insights
        
        first_value = predictions[0].predicted_value
        last_value = predictions[-1].predicted_value
        
        if first_value == 0:
            return insights
        
        trend_pct = ((last_value - first_value) / first_value * 100)
        
        if prediction_type == "inventory":
            if trend_pct > 10:
                insights.append(f"Expected {trend_pct:.1f}% increase in demand over forecast period")
                insights.append("Consider increasing inventory levels to meet growing demand")
            elif trend_pct < -10:
                insights.append(f"Expected {abs(trend_pct):.1f}% decrease in demand")
                insights.append("Consider reducing inventory to avoid overstocking")
            else:
                insights.append("Demand expected to remain stable")
                insights.append("Current inventory levels appear adequate")
        
        elif prediction_type == "budget":
            if trend_pct > 15:
                insights.append(f"Budget spending trending {trend_pct:.1f}% higher")
                insights.append("Review spending controls and budget allocation")
            elif trend_pct < -15:
                insights.append(f"Budget spending trending {abs(trend_pct):.1f}% lower")
                insights.append("Potential opportunity for budget reallocation")
            else:
                insights.append("Budget spending on track with historical patterns")
        
        elif prediction_type == "resource":
            if trend_pct > 10:
                insights.append(f"Resource utilization expected to increase by {trend_pct:.1f}%")
                insights.append("Consider capacity planning and resource allocation")
            elif trend_pct < -10:
                insights.append(f"Resource utilization expected to decrease by {abs(trend_pct):.1f}%")
                insights.append("Potential opportunity for resource optimization")
            else:
                insights.append("Resource utilization expected to remain stable")
        
        elif prediction_type == "sales":
            if trend_pct > 10:
                insights.append(f"Sales revenue expected to grow by {trend_pct:.1f}%")
                insights.append("Positive growth trend - consider scaling operations")
            elif trend_pct < -10:
                insights.append(f"Sales revenue expected to decline by {abs(trend_pct):.1f}%")
                insights.append("Review sales strategy and market conditions")
            else:
                insights.append("Sales revenue expected to remain steady")
        
        return insights
    
    def _analyze_confidence(self, predictions: List[PredictionPoint]) -> List[str]:
        """Analyze confidence levels"""
        insights = []
        
        avg_confidence = np.mean([p.confidence for p in predictions])
        min_confidence = min(p.confidence for p in predictions)
        
        if avg_confidence > 0.85:
            insights.append("High confidence predictions based on strong historical patterns")
        elif avg_confidence < 0.7:
            insights.append("Prediction confidence is moderate - consider additional data collection")
        
        if min_confidence < 0.6:
            insights.append("Long-term predictions have lower confidence - monitor closely")
        
        return insights
    
    def _analyze_historical_context(self, predictions: List[PredictionPoint], 
                                  historical_df: pd.DataFrame, prediction_type: str) -> List[str]:
        """Analyze predictions in context of historical data"""
        insights = []
        
        try:
            target_col = self._get_target_column(prediction_type)
            if target_col not in historical_df.columns:
                return insights
            
            historical_values = historical_df[target_col].values
            predicted_values = [p.predicted_value for p in predictions]
            
            # Compare with historical average
            hist_avg = np.mean(historical_values)
            pred_avg = np.mean(predicted_values)
            
            if pred_avg > hist_avg * 1.2:
                insights.append("Predicted values significantly higher than historical average")
            elif pred_avg < hist_avg * 0.8:
                insights.append("Predicted values significantly lower than historical average")
            
            # Analyze volatility
            hist_std = np.std(historical_values)
            pred_std = np.std(predicted_values)
            
            if pred_std > hist_std * 1.5:
                insights.append("Increased volatility expected compared to historical patterns")
            elif pred_std < hist_std * 0.5:
                insights.append("Lower volatility expected - more stable period ahead")
            
        except Exception as e:
            logger.warning(f"Historical context analysis error: {e}")
        
        return insights
    
    def _get_type_specific_insights(self, predictions: List[PredictionPoint], 
                                  prediction_type: str) -> List[str]:
        """Generate prediction type specific insights"""
        insights = []
        values = [p.predicted_value for p in predictions]
        
        if prediction_type == "inventory":
            max_demand = max(values)
            min_demand = min(values)
            
            if max_demand > min_demand * 2:
                insights.append("High demand variability - consider flexible inventory strategy")
            
            # Check for seasonal patterns (simplified)
            if len(values) >= 7:
                weekly_avg = np.mean(values[:7])
                if len(values) >= 14:
                    second_week_avg = np.mean(values[7:14])
                    if abs(second_week_avg - weekly_avg) / weekly_avg > 0.2:
                        insights.append("Weekly demand patterns detected - optimize replenishment timing")
        
        elif prediction_type == "budget":
            total_predicted = sum(values)
            if len(values) >= 30:  # Monthly prediction
                insights.append(f"Total predicted spending for period: ${total_predicted:,.0f}")
        
        elif prediction_type == "sales":
            total_revenue = sum(values)
            if len(values) >= 30:
                insights.append(f"Projected revenue for period: ${total_revenue:,.0f}")
        
        return insights
    
    def _get_target_column(self, prediction_type: str) -> str:
        """Get target column name for each prediction type"""
        target_mapping = {
            "inventory": "quantity",
            "budget": "amount",
            "resource": "utilization_rate", 
            "sales": "total_amount"
        }
        return target_mapping.get(prediction_type, "")

# Global instance
insight_generator = InsightGenerator()