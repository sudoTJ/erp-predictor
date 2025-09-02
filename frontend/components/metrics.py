"""
Metrics display components
"""
import streamlit as st
from typing import List, Dict, Any, Tuple
import numpy as np
from utils.formatters import format_currency, format_percentage, format_large_number, get_confidence_color

def display_key_metrics(predictions: List[Dict[str, Any]], prediction_type: str, metadata: Dict[str, Any]):
    """Display key metrics in columns"""
    if not predictions:
        st.warning("No predictions available for metrics display")
        return
    
    values = [p['predicted_value'] for p in predictions]
    confidences = [p['confidence'] for p in predictions]
    
    # Calculate metrics
    total_value = sum(values)
    avg_value = np.mean(values)
    avg_confidence = np.mean(confidences)
    trend_pct = ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
    
    # Display in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if prediction_type in ["budget", "sales"]:
            display_value = format_currency(total_value)
            metric_name = "Total Projected"
        else:
            display_value = format_large_number(avg_value)
            metric_name = "Average Predicted"
        
        st.metric(
            label=metric_name,
            value=display_value,
            delta=f"{trend_pct:+.1f}%" if abs(trend_pct) > 0.1 else None
        )
    
    with col2:
        confidence_color = get_confidence_color(avg_confidence)
        st.metric(
            label="Avg Confidence",
            value=f"{avg_confidence:.1%}",
            help="Average confidence across all predictions"
        )
        
        # Color indicator
        if confidence_color == "green":
            st.success("High confidence")
        elif confidence_color == "orange":
            st.warning("Medium confidence")
        else:
            st.error("Low confidence")
    
    with col3:
        st.metric(
            label="Data Points",
            value=metadata.get('data_points', 'N/A'),
            help="Number of historical data points used for training"
        )
    
    with col4:
        volatility = np.std(values) / np.mean(values) if np.mean(values) != 0 else 0
        st.metric(
            label="Volatility",
            value=f"{volatility:.1%}",
            help="Measure of prediction variability"
        )

def display_prediction_summary(predictions: List[Dict[str, Any]], prediction_type: str):
    """Display summary statistics"""
    if not predictions:
        return
    
    values = [p['predicted_value'] for p in predictions]
    
    with st.expander("📊 Detailed Statistics", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Value Statistics")
            
            stats_data = {
                "Minimum": min(values),
                "Maximum": max(values),
                "Average": np.mean(values),
                "Median": np.median(values),
                "Standard Deviation": np.std(values)
            }
            
            for label, value in stats_data.items():
                if prediction_type in ["budget", "sales"]:
                    formatted_value = format_currency(value)
                else:
                    formatted_value = format_large_number(value)
                st.text(f"{label}: {formatted_value}")
        
        with col2:
            st.subheader("Confidence Statistics")
            
            confidences = [p['confidence'] for p in predictions]
            
            conf_stats = {
                "Minimum Confidence": min(confidences),
                "Maximum Confidence": max(confidences),
                "Average Confidence": np.mean(confidences),
                "Confidence Range": max(confidences) - min(confidences)
            }
            
            for label, value in conf_stats.items():
                st.text(f"{label}: {value:.1%}")

def display_risk_indicators(predictions: List[Dict[str, Any]], prediction_type: str):
    """Display risk indicators and warnings"""
    if not predictions:
        return
    
    values = [p['predicted_value'] for p in predictions]
    confidences = [p['confidence'] for p in predictions]
    
    # Calculate risk indicators
    low_confidence_count = sum(1 for c in confidences if c < 0.6)
    high_volatility = np.std(values) / np.mean(values) > 0.3 if np.mean(values) != 0 else False
    declining_trend = values[-1] < values[0] * 0.9
    
    risks = []
    
    if low_confidence_count > len(predictions) * 0.3:
        risks.append("⚠️ Over 30% of predictions have low confidence")
    
    if high_volatility:
        risks.append("⚠️ High volatility detected in predictions")
    
    if declining_trend:
        risks.append("⚠️ Significant declining trend identified")
    
    if prediction_type == "inventory":
        if any(v < 10 for v in values):
            risks.append("⚠️ Stock-out risk detected in forecast period")
    
    elif prediction_type == "budget":
        if any(v > np.mean(values) * 1.5 for v in values):
            risks.append("⚠️ Budget spike risk detected")
    
    if risks:
        st.subheader("🚨 Risk Indicators")
        for risk in risks:
            st.warning(risk)
    else:
        st.success("✅ No significant risks detected in predictions")

def display_model_info(metadata: Dict[str, Any]):
    """Display model information"""
    with st.expander("🤖 Model Information", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.text(f"Model Type: {metadata.get('model_used', 'Unknown').replace('_', ' ').title()}")
            st.text(f"Training Data Points: {metadata.get('data_points', 'N/A')}")
        
        with col2:
            st.text(f"Last Updated: {metadata.get('last_updated', 'Unknown')[:19].replace('T', ' ')}")
            st.text(f"Average Confidence: {metadata.get('confidence_avg', 0):.1%}")
        
        # Model performance indicator
        data_points = metadata.get('data_points', 0)
        if data_points > 50:
            st.success("✅ Sufficient training data")
        elif data_points > 20:
            st.warning("⚠️ Limited training data")
        else:
            st.error("❌ Insufficient training data")

def display_insights_panel(insights: List[str]):
    """Display insights in a formatted panel"""
    if not insights:
        st.info("No specific insights available for this prediction")
        return
    
    st.subheader("💡 Business Insights")
    
    for i, insight in enumerate(insights, 1):
        # Add icons based on insight content
        if any(word in insight.lower() for word in ['increase', 'grow', 'higher']):
            st.success(f"📈 {insight}")
        elif any(word in insight.lower() for word in ['decrease', 'decline', 'lower']):
            st.error(f"📉 {insight}")
        elif any(word in insight.lower() for word in ['stable', 'steady']):
            st.info(f"📊 {insight}")
        elif any(word in insight.lower() for word in ['consider', 'recommend']):
            st.warning(f"💡 {insight}")
        else:
            st.write(f"• {insight}")

def display_action_recommendations(predictions: List[Dict[str, Any]], prediction_type: str, insights: List[str]):
    """Display actionable recommendations"""
    st.subheader("🎯 Recommended Actions")
    
    values = [p['predicted_value'] for p in predictions]
    confidences = [p['confidence'] for p in predictions]
    
    recommendations = []
    
    # Generate recommendations based on prediction type and patterns
    if prediction_type == "inventory":
        avg_demand = np.mean(values)
        if avg_demand > 500:
            recommendations.append("Consider bulk ordering to meet high demand")
        elif avg_demand < 50:
            recommendations.append("Review product lifecycle - demand appears low")
        
        if np.std(values) / np.mean(values) > 0.3:
            recommendations.append("Implement flexible inventory management due to high variability")
    
    elif prediction_type == "budget":
        total_projected = sum(values)
        recommendations.append(f"Plan for total projected spending of {format_currency(total_projected)}")
        
        if any("higher" in insight.lower() for insight in insights):
            recommendations.append("Review budget controls and approval processes")
    
    elif prediction_type == "sales":
        total_projected = sum(values)
        recommendations.append(f"Prepare for projected revenue of {format_currency(total_projected)}")
        
        if any("grow" in insight.lower() for insight in insights):
            recommendations.append("Consider scaling sales operations")
    
    # Add confidence-based recommendations
    avg_confidence = np.mean(confidences)
    if avg_confidence < 0.7:
        recommendations.append("Collect additional data to improve prediction accuracy")
    
    # Display recommendations
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            st.write(f"{i}. {rec}")
    else:
        st.write("Monitor predictions and adjust strategy as needed.")