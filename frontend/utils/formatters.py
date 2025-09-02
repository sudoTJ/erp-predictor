"""
Data formatting utilities
"""
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime

def format_predictions_for_display(predictions: List[Dict[str, Any]]) -> pd.DataFrame:
    """Format prediction data for display in Streamlit"""
    if not predictions:
        return pd.DataFrame()
    
    df = pd.DataFrame(predictions)
    
    # Format date column
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    
    # Format predicted_value with 2 decimal places
    if 'predicted_value' in df.columns:
        df['predicted_value'] = df['predicted_value'].round(2)
    
    # Format confidence as percentage
    if 'confidence' in df.columns:
        df['confidence'] = (df['confidence'] * 100).round(1)
    
    # Rename columns for better display
    column_mapping = {
        'date': 'Date',
        'predicted_value': 'Predicted Value', 
        'confidence': 'Confidence (%)'
    }
    
    df = df.rename(columns=column_mapping)
    return df

def format_currency(amount: float) -> str:
    """Format number as currency"""
    return f"${amount:,.2f}"

def format_percentage(value: float) -> str:
    """Format decimal as percentage"""
    return f"{value:.1%}"

def format_large_number(number: float) -> str:
    """Format large numbers with appropriate suffixes"""
    if number >= 1_000_000:
        return f"{number/1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number/1_000:.1f}K"
    else:
        return f"{number:.1f}"

def get_prediction_type_emoji(prediction_type: str) -> str:
    """Get emoji for prediction type"""
    emoji_map = {
        "inventory": "📦",
        "budget": "💰", 
        "resource": "👥",
        "sales": "📈"
    }
    return emoji_map.get(prediction_type, "📊")

def get_prediction_type_name(prediction_type: str) -> str:
    """Get display name for prediction type"""
    name_map = {
        "inventory": "Inventory Forecasting",
        "budget": "Budget Analysis",
        "resource": "Resource Planning", 
        "sales": "Sales Forecasting"
    }
    return name_map.get(prediction_type, prediction_type.title())

def get_confidence_color(confidence: float) -> str:
    """Get color for confidence level"""
    if confidence >= 0.8:
        return "green"
    elif confidence >= 0.6:
        return "orange" 
    else:
        return "red"

def format_insight_with_emoji(insight: str) -> str:
    """Add appropriate emoji to insights"""
    insight = insight.strip()
    
    if any(word in insight.lower() for word in ['increase', 'grow', 'higher', 'rising']):
        return f"📈 {insight}"
    elif any(word in insight.lower() for word in ['decrease', 'decline', 'lower', 'falling']):
        return f"📉 {insight}"
    elif any(word in insight.lower() for word in ['stable', 'steady', 'consistent']):
        return f"📊 {insight}"
    elif any(word in insight.lower() for word in ['consider', 'recommend']):
        return f"💡 {insight}"
    elif any(word in insight.lower() for word in ['warning', 'alert', 'risk']):
        return f"⚠️ {insight}"
    elif any(word in insight.lower() for word in ['confidence', 'data', 'collection']):
        return f"ℹ️ {insight}"
    else:
        return f"• {insight}"