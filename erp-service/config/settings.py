"""
Configuration settings for ERP Service
"""
import os

class Config:
    """Base configuration"""
    # For Docker/PostgreSQL deployment
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'erp_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    DB_PORT = os.getenv('DB_PORT', '5432')
    
    # For local SQLite deployment
    DATABASE_PATH = os.getenv('DATABASE_PATH', os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'erp_demo.db'))
    
    # Use PostgreSQL if DB_HOST is set (Docker environment)
    USE_POSTGRES = bool(os.getenv('DB_HOST'))
    
    DEBUG = True
    HOST = 'localhost'
    PORT = 3001
    
    # Database settings
    DB_CONNECTION_TIMEOUT = 30
    
    # API settings
    API_VERSION = 'v1'
    API_PREFIX = f'/api/{API_VERSION}'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    HOST = os.getenv('ERP_HOST', '0.0.0.0')
    PORT = int(os.getenv('ERP_PORT', 3001))

# Default configuration
config = DevelopmentConfig()