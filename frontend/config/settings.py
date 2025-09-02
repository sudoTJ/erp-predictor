"""
Configuration settings for Frontend Dashboard
"""
import os

class Config:
    """Base configuration"""
    PREDICTION_API_URL = "http://localhost:3003/api/v1"
    ERP_API_URL = "http://localhost:3001/api/v1"
    
    # Streamlit settings
    PAGE_TITLE = "ERP Prediction Dashboard"
    PAGE_ICON = ":bar_chart:"
    LAYOUT = "wide"
    
    # UI settings
    SIDEBAR_STATE = "expanded"
    THEME = "light"

class DevelopmentConfig(Config):
    """Development configuration"""
    PREDICTION_API_URL = os.getenv('PREDICTION_API_URL', 'http://localhost:3003/api/v1')
    ERP_API_URL = os.getenv('ERP_API_URL', 'http://localhost:3001/api/v1')

class ProductionConfig(Config):
    """Production configuration for Docker"""
    PREDICTION_API_URL = os.getenv('PREDICTION_API_URL', 'http://prediction-service:3002/api/v1')
    ERP_API_URL = os.getenv('ERP_API_URL', 'http://erp-service:3001/api/v1')

# Default to development config
config = DevelopmentConfig()