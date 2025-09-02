"""
Business insights generation utilities
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from models.schemas import PredictionPoint
import logging

logger = logging.getLogger(__name__)

class InsightGenerator:
    """Generate business insights from predictions and historical data"""
    
    def generate_insights(self, predictions: List[PredictionPoint], 
                         prediction_type: str, historical_df: pd.DataFrame = None) -> List[str]:
        """Generate business insights based on predictions"""
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
            logger.error(f"Insight generation error: {e}")
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