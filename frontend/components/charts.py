"""
Chart components using Plotly
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st
from typing import List, Dict, Any
from utils.formatters import get_prediction_type_name

def create_prediction_chart(predictions: List[Dict[str, Any]], prediction_type: str) -> go.Figure:
    """Create main prediction chart with confidence bands"""
    if not predictions:
        return go.Figure()
    
    # Extract data
    dates = [p['date'][:10] for p in predictions]  # Extract date only
    values = [p['predicted_value'] for p in predictions]
    confidences = [p['confidence'] for p in predictions]
    
    # Create figure
    fig = go.Figure()
    
    # Add prediction line
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines+markers',
        name='Predicted Values',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=6),
        hovertemplate='<b>Date</b>: %{x}<br>' +
                     '<b>Predicted Value</b>: %{y}<br>' +
                     '<b>Confidence</b>: %{customdata:.1%}<extra></extra>',
        customdata=confidences
    ))
    
    # Add confidence bands
    upper_bound = [v * (1 + (1-c) * 0.2) for v, c in zip(values, confidences)]
    lower_bound = [v * (1 - (1-c) * 0.2) for v, c in zip(values, confidences)]
    
    fig.add_trace(go.Scatter(
        x=dates + dates[::-1],
        y=upper_bound + lower_bound[::-1],
        fill='toself',
        fillcolor='rgba(31,119,180,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Confidence Band',
        hoverinfo="skip",
        showlegend=False
    ))
    
    # Customize layout
    title_map = {
        "inventory": "📦 Inventory Demand Forecast",
        "budget": "💰 Budget Spending Forecast", 
        "resource": "👥 Resource Utilization Forecast",
        "sales": "📈 Sales Revenue Forecast"
    }
    
    unit_map = {
        "inventory": "Units",
        "budget": "Amount ($)",
        "resource": "Utilization Rate",
        "sales": "Revenue ($)"
    }
    
    fig.update_layout(
        title=title_map.get(prediction_type, "Forecast"),
        xaxis_title="Date",
        yaxis_title=unit_map.get(prediction_type, "Value"),
        hovermode='x unified',
        template="plotly_white",
        height=500,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    return fig

def create_confidence_chart(predictions: List[Dict[str, Any]]) -> go.Figure:
    """Create confidence level chart"""
    if not predictions:
        return go.Figure()
    
    dates = [p['date'][:10] for p in predictions]
    confidences = [p['confidence'] * 100 for p in predictions]  # Convert to percentage
    
    fig = go.Figure()
    
    # Add confidence line with color gradient
    colors = ['green' if c >= 80 else 'orange' if c >= 60 else 'red' for c in confidences]
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=confidences,
        mode='lines+markers',
        name='Confidence Level',
        line=dict(color='#2E8B57', width=2),
        marker=dict(size=6, color=colors),
        fill='tozeroy',
        fillcolor='rgba(46,139,87,0.2)',
        hovertemplate='<b>Date</b>: %{x}<br>' +
                     '<b>Confidence</b>: %{y:.1f}%<extra></extra>'
    ))
    
    # Add horizontal lines for confidence thresholds
    fig.add_hline(y=80, line_dash="dash", line_color="green", 
                 annotation_text="High Confidence", annotation_position="bottom right")
    fig.add_hline(y=60, line_dash="dash", line_color="orange",
                 annotation_text="Medium Confidence", annotation_position="bottom right")
    
    fig.update_layout(
        title="🎯 Prediction Confidence Over Time",
        xaxis_title="Date",
        yaxis_title="Confidence (%)",
        yaxis=dict(range=[0, 100]),
        template="plotly_white",
        height=300,
        showlegend=False
    )
    
    return fig

def create_summary_metrics_chart(predictions: List[Dict[str, Any]], prediction_type: str) -> go.Figure:
    """Create summary metrics chart"""
    if not predictions:
        return go.Figure()
    
    values = [p['predicted_value'] for p in predictions]
    
    # Calculate metrics
    total_sum = sum(values)
    average = sum(values) / len(values)
    minimum = min(values)
    maximum = max(values)
    
    # Create bar chart
    metrics = ['Total', 'Average', 'Minimum', 'Maximum']
    metric_values = [total_sum, average, minimum, maximum]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=metrics,
        y=metric_values,
        marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'],
        hovertemplate='<b>%{x}</b>: %{y:.2f}<extra></extra>'
    ))
    
    unit_map = {
        "inventory": "Units",
        "budget": "$",
        "resource": "Rate",
        "sales": "$"
    }
    
    fig.update_layout(
        title=f"📊 Summary Metrics ({unit_map.get(prediction_type, '')})",
        template="plotly_white",
        height=300,
        showlegend=False
    )
    
    return fig

def create_trend_analysis_chart(predictions: List[Dict[str, Any]]) -> go.Figure:
    """Create trend analysis chart"""
    if len(predictions) < 2:
        return go.Figure()
    
    dates = [p['date'][:10] for p in predictions]
    values = [p['predicted_value'] for p in predictions]
    
    # Calculate moving average
    window = min(7, len(values) // 2)
    if window >= 2:
        moving_avg = pd.Series(values).rolling(window=window, center=True).mean()
    else:
        moving_avg = values
    
    fig = go.Figure()
    
    # Add actual values
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines+markers',
        name='Predictions',
        line=dict(color='lightblue', width=1),
        marker=dict(size=4)
    ))
    
    # Add trend line
    fig.add_trace(go.Scatter(
        x=dates,
        y=moving_avg,
        mode='lines',
        name=f'{window}-Day Trend',
        line=dict(color='red', width=3)
    ))
    
    fig.update_layout(
        title="📈 Trend Analysis",
        xaxis_title="Date",
        yaxis_title="Value",
        template="plotly_white",
        height=300,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    return fig