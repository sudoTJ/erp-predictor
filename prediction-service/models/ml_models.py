"""
Machine Learning models and related functionality
"""
from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class UniversalMLModel:
    """Universal ML model that handles multiple prediction types"""
    
    def __init__(self, model_type: str = "linear_regression"):
        self.model_type = model_type
        self.model = LinearRegression()
        self.is_trained = False
        
    def train(self, X: np.ndarray, y: np.ndarray) -> float:
        """Train the model and return score"""
        try:
            if len(X) < 2:
                logger.warning("Insufficient data for training")
                return 0.0
                
            self.model.fit(X, y)
            self.is_trained = True
            
            # Calculate R² score
            score = self.model.score(X, y)
            return max(0.0, min(1.0, score))  # Clamp between 0 and 1
            
        except Exception as e:
            logger.error(f"Model training error: {e}")
            self.is_trained = False
            return 0.0
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        if not self.is_trained:
            logger.warning("Model not trained, returning zeros")
            return np.zeros(len(X))
            
        try:
            predictions = self.model.predict(X)
            # Ensure non-negative predictions for most business metrics
            return np.maximum(predictions, 0)
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return np.zeros(len(X))
    
    def get_feature_importance(self) -> Optional[np.ndarray]:
        """Get feature importance (coefficients for linear models)"""
        if not self.is_trained:
            return None
        
        try:
            if hasattr(self.model, 'coef_'):
                return np.abs(self.model.coef_)
            return None
        except Exception as e:
            logger.error(f"Error getting feature importance: {e}")
            return None

class SimpleMovingAverage:
    """Simple moving average model as fallback"""
    
    def __init__(self, window: int = 7):
        self.window = window
        
    def predict(self, data: List[float], steps: int) -> List[float]:
        """Predict using simple moving average"""
        if len(data) < self.window:
            # Use overall mean if insufficient data
            avg = np.mean(data) if data else 0.0
            return [avg] * steps
        
        # Calculate moving average from last window
        recent_avg = np.mean(data[-self.window:])
        return [recent_avg] * steps

class TrendModel:
    """Simple linear trend model as fallback"""
    
    def predict(self, data: List[float], steps: int) -> List[float]:
        """Predict using linear trend"""
        if len(data) < 2:
            return [data[0] if data else 0.0] * steps
        
        # Calculate trend
        x = np.arange(len(data))
        y = np.array(data)
        
        try:
            # Simple linear regression
            slope = np.sum((x - np.mean(x)) * (y - np.mean(y))) / np.sum((x - np.mean(x)) ** 2)
            intercept = np.mean(y) - slope * np.mean(x)
            
            # Generate predictions
            future_x = np.arange(len(data), len(data) + steps)
            predictions = slope * future_x + intercept
            
            return np.maximum(predictions, 0).tolist()  # Ensure non-negative
            
        except Exception as e:
            logger.error(f"Trend calculation error: {e}")
            # Fallback to last value
            return [data[-1]] * steps