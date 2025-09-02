"""
Main Flask application for ERP Service
Modular architecture with clean separation of concerns
"""
from flask import Flask
from config.settings import config
from routes.health import health_bp
from routes.inventory import inventory_bp
from routes.finance import finance_bp

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object(config)
    
    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(finance_bp)
    
    return app

def main():
    """Main entry point"""
    app = create_app()
    
    print(f"Starting ERP Service on http://{config.HOST}:{config.PORT}")
    print(f"API Documentation: http://{config.HOST}:{config.PORT}{config.API_PREFIX}")
    print(f"Health Check: http://{config.HOST}:{config.PORT}/health")
    
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )

if __name__ == '__main__':
    main()