"""
Pydantic models for API request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Any, Optional
from datetime import datetime

class PredictionRequest(BaseModel):
    """Request model for predictions"""
    prediction_type: str = Field(..., description="Type of prediction: inventory, budget, resource, sales")
    entity_id: str = Field(..., description="Entity identifier (SKU, department, etc.)")
    time_horizon: int = Field(30, ge=1, le=90, description="Number of days to predict")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context parameters")
    
    @validator('prediction_type')
    def validate_prediction_type(cls, v):
        valid_types = ['inventory', 'budget', 'resource', 'sales']
        if v not in valid_types:
            raise ValueError(f'prediction_type must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('entity_id')
    def validate_entity_id(cls, v):
        if not v or not v.strip():
            raise ValueError('entity_id cannot be empty')
        return v.strip()

class PredictionPoint(BaseModel):
    """Individual prediction data point"""
    date: str = Field(..., description="Date in ISO format")
    predicted_value: float = Field(..., description="Predicted value")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score between 0 and 1")

class PredictionMetadata(BaseModel):
    """Metadata about the prediction"""
    model_used: str = Field(..., description="ML model type used")
    data_points: int = Field(..., description="Number of historical data points used")
    last_updated: str = Field(..., description="When the prediction was generated")
    confidence_avg: float = Field(..., description="Average confidence score")

class PredictionResponse(BaseModel):
    """Complete prediction response"""
    prediction_type: str = Field(..., description="Type of prediction made")
    entity_id: str = Field(..., description="Entity identifier")
    time_horizon: int = Field(..., description="Number of days predicted")
    predictions: List[PredictionPoint] = Field(..., description="List of prediction points")
    insights: List[str] = Field(..., description="Business insights and recommendations")
    metadata: PredictionMetadata = Field(..., description="Prediction metadata")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    timestamp: str = Field(..., description="Current timestamp")
    dependencies: Optional[Dict[str, str]] = Field(default_factory=dict, description="Dependency status")