"""
Prediction routes
"""
from fastapi import APIRouter, HTTPException
from models.schemas import PredictionRequest, PredictionResponse
from services.prediction_engine import prediction_engine
import logging

logger = logging.getLogger(__name__)
predictions_router = APIRouter(prefix="/api/v1", tags=["Predictions"])

@predictions_router.post("/predict", response_model=PredictionResponse)
async def create_prediction(request: PredictionRequest):
    """Generate predictions based on historical ERP data"""
    try:
        logger.info(f"Received prediction request: {request.prediction_type} for {request.entity_id}")
        
        result = await prediction_engine.generate_predictions(
            prediction_type=request.prediction_type,
            entity_id=request.entity_id,
            time_horizon=request.time_horizon,
            context=request.context
        )
        
        return PredictionResponse(**result)
        
    except Exception as e:
        logger.error(f"Prediction endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@predictions_router.get("/predict/types")
async def get_prediction_types():
    """Get available prediction types"""
    return {
        "prediction_types": [
            {
                "type": "inventory",
                "name": "Inventory Forecasting",
                "description": "Predict product demand and inventory needs",
                "entities": ["SKU001", "SKU002", "SKU003", "SKU004", "SKU005"]
            },
            {
                "type": "budget", 
                "name": "Budget Analysis",
                "description": "Forecast department spending and budget variance",
                "entities": ["Marketing", "Engineering", "Operations", "HR"]
            },
            {
                "type": "resource",
                "name": "Resource Planning", 
                "description": "Predict team utilization and capacity needs",
                "entities": ["Engineering", "Sales", "Marketing", "Operations"]
            },
            {
                "type": "sales",
                "name": "Sales Forecasting",
                "description": "Forecast revenue and sales trends", 
                "entities": ["overall"]
            }
        ]
    }