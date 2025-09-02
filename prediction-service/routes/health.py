"""
Health check routes
"""
from fastapi import APIRouter
from models.schemas import HealthResponse
from services.data_fetcher import data_fetcher
from datetime import datetime

health_router = APIRouter(tags=["Health"])

@health_router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with dependency status"""
    
    # Check ERP service dependency
    erp_status = await data_fetcher.health_check()
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat(),
        dependencies=erp_status
    )