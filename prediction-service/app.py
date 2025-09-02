"""
Main FastAPI application for Prediction Service
Modular architecture with clean separation of concerns
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn

from config.settings import config
from routes.health import health_router
from routes.predictions import predictions_router

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Application factory"""
    app = FastAPI(
        title="ERP Prediction Service",
        description="AI-powered prediction service for ERP systems",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS middleware for frontend integration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify exact origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register routers
    app.include_router(health_router)
    app.include_router(predictions_router)
    
    # Startup logging
    logger.info("Prediction Service starting up...")
    logger.info(f"API Documentation available at: http://{config.HOST}:{config.PORT}/docs")
    logger.info(f"Health Check: http://{config.HOST}:{config.PORT}/health")
    logger.info(f"ERP Service URL: {config.ERP_SERVICE_URL}")
    
    return app

def main():
    """Main entry point"""
    app = create_app()
    
    uvicorn.run(
        app,
        host=config.HOST,
        port=config.PORT,
        log_level="info" if config.DEBUG else "warning"
    )

if __name__ == "__main__":
    main()