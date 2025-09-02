"""
Sidebar component for parameter selection
"""
import streamlit as st
from typing import Dict, Any, Tuple
from utils.formatters import get_prediction_type_emoji, get_prediction_type_name

def render_prediction_sidebar() -> Tuple[str, str, int]:
    """Render sidebar for prediction parameters"""
    st.sidebar.header("🎯 Prediction Parameters")
    
    # Prediction types with emojis
    prediction_types = {
        "inventory": "📦 Inventory Forecasting",
        "budget": "💰 Budget Analysis", 
        "resource": "👥 Resource Planning",
        "sales": "📈 Sales Forecasting"
    }
    
    selected_type = st.sidebar.selectbox(
        "Prediction Type",
        options=list(prediction_types.keys()),
        format_func=lambda x: prediction_types[x],
        key="prediction_type"
    )
    
    # Entity options based on prediction type
    entity_options = {
        "inventory": ["SKU001", "SKU002", "SKU003", "SKU004", "SKU005"],
        "budget": ["Marketing", "Engineering", "Operations", "HR"],
        "resource": ["Engineering", "Sales", "Marketing", "Operations"],
        "sales": ["overall"]
    }
    
    # Entity selection
    entity_id = st.sidebar.selectbox(
        "Entity",
        options=entity_options[selected_type],
        key="entity_id"
    )
    
    # Time horizon with description
    time_horizon = st.sidebar.slider(
        "Forecast Horizon (Days)",
        min_value=7,
        max_value=90,
        value=30,
        step=7,
        help="Number of days to predict into the future",
        key="time_horizon"
    )
    
    # Advanced options (expandable)
    with st.sidebar.expander("⚙️ Advanced Options"):
        seasonal_adjustment = st.checkbox(
            "Seasonal Adjustment", 
            value=False,
            help="Apply seasonal factors to predictions"
        )
        
        confidence_threshold = st.slider(
            "Min Confidence Threshold",
            min_value=0.5,
            max_value=0.95,
            value=0.7,
            step=0.05,
            help="Minimum confidence level for recommendations"
        )
    
    # Store advanced options in session state for context
    if 'advanced_options' not in st.session_state:
        st.session_state.advanced_options = {}
    
    st.session_state.advanced_options = {
        'seasonal_adjustment': seasonal_adjustment,
        'confidence_threshold': confidence_threshold
    }
    
    # Info box
    st.sidebar.info(
        f"**{get_prediction_type_name(selected_type)}**\n\n"
        f"Forecasting {entity_id} for the next {time_horizon} days"
    )
    
    return selected_type, entity_id, time_horizon

def render_service_status():
    """Render service status in sidebar"""
    from utils.api_client import api_client
    
    with st.sidebar.expander("🔧 Service Status"):
        health_status = api_client.check_health()
        
        for service, status in health_status.items():
            st.text(f"{service}: {status}")
        
        if st.button("🔄 Refresh Status", key="refresh_status"):
            st.rerun()

def render_quick_actions():
    """Render quick action buttons"""
    st.sidebar.markdown("### 🚀 Quick Actions")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("📊 Demo Data", key="demo_data"):
            st.session_state.show_demo = True
    
    with col2:
        if st.button("📋 Export", key="export_data"):
            st.session_state.show_export = True