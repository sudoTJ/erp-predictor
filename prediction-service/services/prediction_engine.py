"""
Core prediction engine that orchestrates ML models and feature engineering
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

from models.ml_models import UniversalMLModel, SimpleMovingAverage, TrendModel
from models.schemas import PredictionPoint
from services.data_fetcher import data_fetcher
from services.feature_engineer import feature_engineer
from utils.insights import insight_generator
from config.settings import config

logger = logging.getLogger(__name__)

class PredictionEngine:
    """Main prediction engine that orchestrates the entire ML pipeline"""
    
    def __init__(self):
        self.ml_model = UniversalMLModel()
        self.fallback_ma = SimpleMovingAverage()
        self.fallback_trend = TrendModel()
        self.feature_engineer = feature_engineer
        self.insight_generator = insight_generator
    
    async def generate_predictions(
        self, 
        prediction_type: str, 
        entity_id: str, 
        time_horizon: int,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate complete prediction with insights"""
        try:
            logger.info(f"Starting prediction for {prediction_type}:{entity_id} ({time_horizon} days)")
            
            # Fetch historical data
            historical_data = await data_fetcher.fetch_historical_data(prediction_type, entity_id)
            
            # Prepare features
            df = self.feature_engineer.prepare_features(historical_data, prediction_type)
            
            # Generate predictions
            predictions = self._create_predictions(df, prediction_type, time_horizon)
            
            # Create metadata first (needed for insights)
            metadata = self._create_metadata(df, predictions)
            
            # Prepare enhanced prediction data for AI insights
            prediction_data = {
                "prediction_type": prediction_type,
                "entity_id": entity_id,
                "time_horizon": time_horizon,
                "predictions": [p.dict() for p in predictions],
                "metadata": metadata
            }
            
            # Generate enhanced insights with DGPT + fallback
            insights = await self.insight_generator.generate_insights(
                predictions, 
                prediction_type, 
                historical_df=df,
                entity_id=entity_id,
                prediction_data=prediction_data
            )
            
            return {
                "prediction_type": prediction_type,
                "entity_id": entity_id,
                "time_horizon": time_horizon,
                "predictions": [p.dict() for p in predictions],
                "insights": insights,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Prediction generation error: {e}")
            # Return fallback predictions
            return self._generate_fallback_predictions(prediction_type, entity_id, time_horizon, str(e))
    
    def _create_predictions(self, df: pd.DataFrame, prediction_type: str, time_horizon: int) -> List[PredictionPoint]:
        """Create ML predictions from prepared features"""
        if len(df) < config.MIN_DATA_POINTS:
            logger.warning(f"Insufficient data points ({len(df)}), using fallback")
            return self._fallback_predictions(df, prediction_type, time_horizon)
        
        try:
            # Prepare features and target
            feature_cols = self._get_feature_columns(df, prediction_type)
            target_col = self._get_target_column(prediction_type)
            
            if not feature_cols or target_col not in df.columns:
                logger.warning("Missing features or target, using fallback")
                return self._fallback_predictions(df, prediction_type, time_horizon)
            
            X = df[feature_cols].fillna(0).values
            y = df[target_col].values
            
            # Train model
            score = self.ml_model.train(X, y)
            logger.info(f"Model trained with score: {score:.3f}")
            
            # Generate future features
            last_date = pd.to_datetime(df['date'].max())
            future_dates = [last_date + timedelta(days=i) for i in range(1, time_horizon + 1)]
            future_features = self.feature_engineer.create_future_features(df, future_dates, feature_cols)
            
            if len(future_features) == 0:
                return self._fallback_predictions(df, prediction_type, time_horizon)
            
            # Make predictions
            future_predictions = self.ml_model.predict(future_features)
            
            # Create prediction points with confidence
            predictions = []
            for i, (date, pred_value) in enumerate(zip(future_dates, future_predictions)):
                confidence = self._calculate_confidence(i, time_horizon, score)
                predictions.append(PredictionPoint(
                    date=date.isoformat(),
                    predicted_value=round(float(pred_value), 2),
                    confidence=round(confidence, 2)
                ))
            
            return predictions
            
        except Exception as e:
            logger.error(f"ML prediction error: {e}")
            return self._fallback_predictions(df, prediction_type, time_horizon)
    
    def _get_feature_columns(self, df: pd.DataFrame, prediction_type: str) -> List[str]:
        """Get appropriate feature columns for each prediction type"""
        exclude_cols = ['date']
        
        if prediction_type == "inventory":
            exclude_cols.extend(['quantity'])
        elif prediction_type == "budget":
            exclude_cols.extend(['amount'])
        elif prediction_type == "resource":
            exclude_cols.extend(['utilization_rate', 'available_hours', 'utilized_hours'])
        elif prediction_type == "sales":
            exclude_cols.extend(['total_amount'])
        
        return [col for col in df.columns if col not in exclude_cols]
    
    def _get_target_column(self, prediction_type: str) -> str:
        """Get target column for each prediction type"""
        target_mapping = {
            "inventory": "quantity",
            "budget": "amount", 
            "resource": "utilization_rate",
            "sales": "total_amount"
        }
        return target_mapping.get(prediction_type, "")
    
    def _calculate_confidence(self, step: int, time_horizon: int, model_score: float) -> float:
        """Calculate confidence score that decreases over time"""
        base_confidence = config.BASE_CONFIDENCE
        decay = config.CONFIDENCE_DECAY
        
        # Start with model score influence
        score_factor = max(0.5, model_score) if model_score > 0 else 0.6
        
        # Time decay
        time_factor = max(0.5, base_confidence - (step * decay))
        
        # Combined confidence
        confidence = score_factor * time_factor
        return max(0.5, min(0.95, confidence))
    
    def _fallback_predictions(self, df: pd.DataFrame, prediction_type: str, time_horizon: int) -> List[PredictionPoint]:
        """Generate fallback predictions using simple methods"""
        try:
            target_col = self._get_target_column(prediction_type)
            
            if target_col in df.columns and len(df) > 0:
                values = df[target_col].values
                trend_predictions = self.fallback_trend.predict(values.tolist(), time_horizon)
            else:
                # Ultimate fallback
                trend_predictions = [100.0] * time_horizon
            
            predictions = []
            base_date = datetime.now()
            
            for i, pred_value in enumerate(trend_predictions):
                future_date = base_date + timedelta(days=i + 1)
                predictions.append(PredictionPoint(
                    date=future_date.isoformat(),
                    predicted_value=round(float(pred_value), 2),
                    confidence=0.6
                ))
            
            logger.info(f"Generated {len(predictions)} fallback predictions")
            return predictions
            
        except Exception as e:
            logger.error(f"Fallback prediction error: {e}")
            # Ultimate fallback
            predictions = []
            base_date = datetime.now()
            
            for i in range(time_horizon):
                future_date = base_date + timedelta(days=i + 1)
                predictions.append(PredictionPoint(
                    date=future_date.isoformat(),
                    predicted_value=100.0,
                    confidence=0.5
                ))
            
            return predictions
    
    def _create_metadata(self, df: pd.DataFrame, predictions: List[PredictionPoint]) -> Dict[str, Any]:
        """Create prediction metadata"""
        avg_confidence = np.mean([p.confidence for p in predictions]) if predictions else 0
        
        return {
            "model_used": self.ml_model.model_type,
            "data_points": len(df),
            "last_updated": datetime.now().isoformat(),
            "confidence_avg": round(avg_confidence, 2)
        }
    
    def _generate_fallback_predictions(self, prediction_type: str, entity_id: str, 
                                     time_horizon: int, error_msg: str) -> Dict[str, Any]:
        """Generate fallback response when everything fails"""
        predictions = []
        base_date = datetime.now()
        
        for i in range(time_horizon):
            future_date = base_date + timedelta(days=i + 1)
            predictions.append({
                "date": future_date.isoformat(),
                "predicted_value": 100.0,
                "confidence": 0.5
            })
        
        return {
            "prediction_type": prediction_type,
            "entity_id": entity_id,
            "time_horizon": time_horizon,
            "predictions": predictions,
            "insights": [f"Unable to generate detailed insights: {error_msg}", "Using basic trend analysis"],
            "metadata": {
                "model_used": "fallback",
                "data_points": 0,
                "last_updated": datetime.now().isoformat(),
                "confidence_avg": 0.5
            }
        }

# Global instance
prediction_engine = PredictionEngine()