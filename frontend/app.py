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
    
    # Header - Business-focused title
    st.title("📊 Smart Business Forecasting")
    st.markdown("**Get instant predictions to prevent stockouts, budget overruns, and resource shortages**")
    
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
            with st.spinner("🤖 Generating AI-powered business insights... Please wait for DGPT analysis"):
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
    """Display prediction results with business insights prioritized first"""
    predictions = result.get('predictions', [])
    insights = result.get('insights', [])
    metadata = result.get('metadata', {})
    prediction_type = result.get('prediction_type', '')
    entity_id = result.get('entity_id', '')
    
    # === BUSINESS INSIGHTS FIRST (Most Important) ===
    st.markdown("## 🎯 **What This Means for Your Business**")
    
    # Create prominent insights display
    insight_col1, insight_col2 = st.columns([2, 1])
    
    with insight_col1:
        # Primary business insights - highly visible
        if insights:
            st.markdown("### 💡 **Key Insights & Recommendations**")
            for i, insight in enumerate(insights, 1):
                insight_lower = insight.lower()
                
                # URGENT ACTION - Only for critical problems
                if any(phrase in insight_lower for phrase in [
                    'reorder recommended', 'will run out', 'stockout', 'running low', 
                    'urgent reorder', 'immediate action', 'critical stock level'
                ]):
                    st.error(f"🚨 **URGENT ACTION:** {insight}")
                
                # BUDGET ALERT - Only for spending issues
                elif any(phrase in insight_lower for phrase in [
                    'over budget', 'exceed budget', 'budget exceeded', 'overspending',
                    'budget variance', 'spending too much', 'budget alert'
                ]):
                    st.warning(f"⚠️ **BUDGET ALERT:** {insight}")
                
                # GOOD NEWS - Positive situations
                elif any(phrase in insight_lower for phrase in [
                    'adequate', 'stable', 'good', 'healthy', 'sufficient', 
                    'on track', 'within budget', 'performing well'
                ]):
                    st.success(f"✅ **GOOD NEWS:** {insight}")
                
                # WARNING - Moderate concerns
                elif any(phrase in insight_lower for phrase in [
                    'monitor closely', 'watch', 'attention needed', 'declining',
                    'trending down', 'consider', 'may need'
                ]):
                    st.warning(f"⚠️ **MONITOR:** {insight}")
                
                # DEFAULT - General insights
                else:
                    st.info(f"📋 **INSIGHT {i}:** {insight}")
        else:
            st.info("🔍 Analyzing patterns... insights will appear here")
    
    with insight_col2:
        # Quick action summary
        display_action_recommendations(predictions, prediction_type, insights)
    
    st.markdown("---")  # Visual separator
    
    # === MAIN PREDICTION CHART (Right after insights) ===
    st.markdown("## 📈 **Prediction Forecast**")
    
    chart_col, info_col = st.columns([3, 1])
    
    with chart_col:
        if predictions:
            fig = create_prediction_chart(predictions, prediction_type)
            st.plotly_chart(fig, use_container_width=True)
            st.caption("💡 *Hover over the chart for detailed values and dates*")
        else:
            st.error("No prediction data available")
    
    with info_col:
        # Display model info
        display_model_info(metadata)
        
        # Risk indicators
        display_risk_indicators(predictions, prediction_type)
    
    # === DETAILED ANALYSIS (EXPANDABLE SECTIONS) ===
    st.markdown("---")
    st.markdown("## 📊 **Additional Analysis** *(Click sections below to explore)*")
    
    # Key metrics - now in expandable section
    with st.expander("📊 **Key Summary Metrics**", expanded=False):
        display_key_metrics(predictions, prediction_type, metadata)
    
    # Secondary analysis charts
    with st.expander("📊 **Advanced Analytics & Confidence Analysis**", expanded=False):
        if predictions:
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.markdown("**Confidence Over Time**")
                confidence_fig = create_confidence_chart(predictions)
                st.plotly_chart(confidence_fig, use_container_width=True)
            
            with chart_col2:
                if len(predictions) > 7:
                    st.markdown("**Trend Analysis**")
                    trend_fig = create_trend_analysis_chart(predictions)
                    st.plotly_chart(trend_fig, use_container_width=True)
                else:
                    st.markdown("**Summary Metrics**")
                    summary_fig = create_summary_metrics_chart(predictions, prediction_type)
                    st.plotly_chart(summary_fig, use_container_width=True)
        else:
            st.info("Generate a prediction to see advanced analytics")
    
    # Raw data table - least priority
    with st.expander("📋 **Raw Data & Export** *(For detailed analysis)*", expanded=False):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if predictions:
                st.markdown("**Daily Predictions Table**")
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
            else:
                st.info("No data to display")
        
        with col2:
            st.markdown("**Prediction Summary**")
            display_prediction_summary(predictions, prediction_type)

def display_welcome_content():
    """Display welcome content when no predictions are shown"""
    st.markdown("## 🎯 **Turn Your Business Data Into Smart Decisions**")
    
    # Prominent call-to-action box
    st.info("👈 **Select a prediction type from the sidebar to get started** - Get actionable insights in under 2 seconds!")
    
    st.markdown("---")
    
    # Business value proposition first
    st.markdown("### 💼 **Stop Guessing, Start Predicting**")
    
    value_col1, value_col2 = st.columns(2)
    
    with value_col1:
        st.markdown("""
        **🚨 Problems This Solves:**
        - Running out of popular products
        - Budget overruns discovered too late  
        - Teams overworked or underutilized
        - Missing revenue opportunities
        """)
    
    with value_col2:
        st.markdown("""
        **✅ Business Benefits:**
        - Prevent costly stockouts & overstock
        - Control spending before budget deadlines
        - Plan workforce needs in advance
        - Make data-driven strategic decisions
        """)
    
    st.markdown("---")
    
    # What we predict - business focused
    st.markdown("### 🎯 **What We Predict For You**")
    
    pred_col1, pred_col2 = st.columns(2)
    
    with pred_col1:
        st.markdown("""
        **📦 Inventory Intelligence**
        - *"Will I run out of laptops next week?"*
        - Get reorder alerts before stockouts
        
        **💰 Budget Control**
        - *"Is Marketing about to exceed budget?"*
        - Early warning for overspending
        """)
    
    with pred_col2:
        st.markdown("""
        **👥 Workforce Planning** 
        - *"Do I need to hire more engineers?"*
        - Optimize team capacity & costs
        
        **📈 Revenue Forecasting**
        - *"What's our sales trajectory?"*
        - Spot growth opportunities early
        """)
    
    st.markdown("---")
    
    # Quick start - action oriented
    st.markdown("### 🚀 **3 Simple Steps to Smart Insights**")
    
    step_col1, step_col2, step_col3 = st.columns(3)
    
    with step_col1:
        st.markdown("""
        **1️⃣ Choose What to Predict**
        Select inventory, budget, workforce, or sales from the sidebar
        """)
    
    with step_col2:
        st.markdown("""
        **2️⃣ Pick Your Focus**
        Choose the product, department, or team you want to analyze
        """)
    
    with step_col3:
        st.markdown("""
        **3️⃣ Get Instant Insights**
        Click "Generate Prediction" for actionable recommendations
        """)
    
    st.markdown("---")
    
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