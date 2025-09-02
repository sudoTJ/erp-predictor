"""
Main Streamlit application - ERP Prediction Dashboard
Enhanced modular architecture with local development support
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import logging

from config.settings import config
from components.sidebar import render_prediction_sidebar, render_service_status, render_quick_actions
from components.charts import create_prediction_chart, create_confidence_chart, create_summary_metrics_chart, create_trend_analysis_chart
from components.metrics import display_key_metrics, display_prediction_summary, display_risk_indicators, display_model_info, display_insights_panel, display_action_recommendations
from utils.api_client import api_client
from utils.formatters import format_predictions_for_display, format_insight_with_emoji

# Configure Streamlit page
st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout=config.LAYOUT,
    initial_sidebar_state=config.SIDEBAR_STATE
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main application function"""
    
    # Header
    st.title("🚀 ERP Prediction Dashboard")
    st.markdown("**AI-powered business intelligence for your ERP system**")
    
    # Sidebar for parameters
    prediction_type, entity_id, time_horizon = render_prediction_sidebar()
    
    # Service status in sidebar
    render_service_status()
    
    # Quick actions in sidebar  
    render_quick_actions()
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col2:
        # Generate prediction button
        if st.button("🔮 Generate Prediction", type="primary", use_container_width=True):
            with st.spinner("🔍 Analyzing data and generating predictions..."):
                result = api_client.make_prediction(
                    prediction_type=prediction_type,
                    entity_id=entity_id, 
                    time_horizon=time_horizon,
                    context=st.session_state.get('advanced_options', {})
                )
                
                if result:
                    st.session_state['current_prediction'] = result
                    st.success("✅ Prediction generated successfully!")
                else:
                    st.error("❌ Failed to generate prediction")
    
    with col1:
        # Display current parameters
        st.info(f"**Current Selection:** {prediction_type.title()} prediction for {entity_id} over {time_horizon} days")
    
    # Display results if available
    if 'current_prediction' in st.session_state:
        display_prediction_results(st.session_state['current_prediction'])
    else:
        display_welcome_content()

def display_prediction_results(result):
    """Display prediction results with charts and insights"""
    predictions = result.get('predictions', [])
    insights = result.get('insights', [])
    metadata = result.get('metadata', {})
    prediction_type = result.get('prediction_type', '')
    entity_id = result.get('entity_id', '')
    
    # Key metrics at the top
    st.markdown("## 📊 Key Metrics")
    display_key_metrics(predictions, prediction_type, metadata)
    
    # Main prediction chart
    st.markdown("## 📈 Prediction Forecast")
    
    chart_col, info_col = st.columns([3, 1])
    
    with chart_col:
        if predictions:
            fig = create_prediction_chart(predictions, prediction_type)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("No prediction data available")
    
    with info_col:
        # Display model info
        display_model_info(metadata)
        
        # Risk indicators
        display_risk_indicators(predictions, prediction_type)
    
    # Secondary charts
    if predictions:
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            confidence_fig = create_confidence_chart(predictions)
            st.plotly_chart(confidence_fig, use_container_width=True)
        
        with chart_col2:
            if len(predictions) > 7:
                trend_fig = create_trend_analysis_chart(predictions)
                st.plotly_chart(trend_fig, use_container_width=True)
            else:
                summary_fig = create_summary_metrics_chart(predictions, prediction_type)
                st.plotly_chart(summary_fig, use_container_width=True)
    
    # Insights and recommendations
    col1, col2 = st.columns([1, 1])
    
    with col1:
        display_insights_panel(insights)
        
    with col2:
        display_action_recommendations(predictions, prediction_type, insights)
    
    # Detailed data section
    with st.expander("📋 Detailed Prediction Data", expanded=False):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if predictions:
                df = format_predictions_for_display(predictions)
                st.dataframe(df, use_container_width=True)
                
                # Export option
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"{prediction_type}_{entity_id}_forecast_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            display_prediction_summary(predictions, prediction_type)

def display_welcome_content():
    """Display welcome content when no predictions are shown"""
    st.markdown("## 🎯 Welcome to the ERP Prediction System")
    
    st.markdown("""
    This dashboard provides AI-powered predictions for your ERP data across multiple business domains:
    
    ### 📦 **Inventory Forecasting**
    - Predict product demand trends
    - Optimize stock levels and reduce holding costs
    - Avoid stockouts and overstock situations
    
    ### 💰 **Budget Analysis** 
    - Forecast department spending patterns
    - Identify budget variances early
    - Enable proactive budget management
    
    ### 👥 **Resource Planning**
    - Predict team utilization rates
    - Plan capacity and hiring needs
    - Optimize resource allocation
    
    ### 📈 **Sales Forecasting**
    - Forecast revenue trends
    - Identify growth opportunities
    - Support strategic planning
    
    ---
    
    **🚀 Quick Start:**
    1. Select a prediction type from the sidebar
    2. Choose the entity you want to analyze  
    3. Set your forecast horizon
    4. Click "Generate Prediction"
    """)
    
    # Demo metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📦 Products Tracked", "5", delta="Active")
    
    with col2:
        st.metric("💰 Budget Categories", "4", delta="Monitored")
        
    with col3:
        st.metric("👥 Departments", "4", delta="Analyzed")
        
    with col4:
        st.metric("🎯 Predictions Made", "Today", delta="Real-time")
    
    # Feature highlights
    st.markdown("### ⚡ **Key Features**")
    
    feature_col1, feature_col2 = st.columns(2)
    
    with feature_col1:
        st.markdown("""
        - **Sub-2 second response times** ⚡
        - **Confidence intervals** for all predictions 📊
        - **Interactive visualizations** 📈
        """)
    
    with feature_col2:
        st.markdown("""
        - **Actionable business insights** 💡
        - **Risk indicators and alerts** ⚠️
        - **Export capabilities** 📥
        """)

def handle_session_state():
    """Initialize session state variables"""
    if 'advanced_options' not in st.session_state:
        st.session_state.advanced_options = {}
    
    if 'show_demo' not in st.session_state:
        st.session_state.show_demo = False
    
    if 'show_export' not in st.session_state:
        st.session_state.show_export = False

# Footer
def display_footer():
    """Display footer information"""
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            🤖 Powered by AI • Built for ERP Systems • Enhanced Dashboard v2.0
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    handle_session_state()
    main()
    display_footer()