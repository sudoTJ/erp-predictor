"""
Configuration settings for Prediction Service
"""
import os

class Config:
    """Base configuration"""
    ERP_SERVICE_URL = "http://localhost:3001/api/v1"
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 3003
    
    # ML Settings
    ML_MODEL_TYPE = "linear_regression"
    DEFAULT_TIME_HORIZON = 30
    MAX_TIME_HORIZON = 90
    MIN_DATA_POINTS = 5
    
    # API Settings
    API_VERSION = 'v1'
    API_PREFIX = f'/api/{API_VERSION}'
    REQUEST_TIMEOUT = 30.0
    
    # Confidence Settings
    BASE_CONFIDENCE = 0.8
    CONFIDENCE_DECAY = 0.01

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ERP_SERVICE_URL = os.getenv('ERP_SERVICE_URL', 'http://localhost:3001/api/v1')

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    HOST = os.getenv('PREDICTION_HOST', '0.0.0.0')
    PORT = int(os.getenv('PREDICTION_PORT', 3003))
    ERP_SERVICE_URL = os.getenv('ERP_SERVICE_URL', 'http://erp-service:3001/api/v1')

# Default configuration
config = DevelopmentConfig()