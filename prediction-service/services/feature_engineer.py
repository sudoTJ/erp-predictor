"""
Feature engineering service for ML models
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class FeatureEngineer:
    """Service for converting raw ERP data into ML features"""
    
    def prepare_features(self, data: Dict[str, Any], prediction_type: str) -> pd.DataFrame:
        """Convert ERP data to ML features based on prediction type"""
        try:
            if prediction_type == "inventory":
                return self._prepare_inventory_features(data)
            elif prediction_type == "budget":
                return self._prepare_budget_features(data)
            elif prediction_type == "resource":
                return self._prepare_resource_features(data)
            elif prediction_type == "sales":
                return self._prepare_sales_features(data)
            else:
                raise ValueError(f"Unknown prediction type: {prediction_type}")
                
        except Exception as e:
            logger.error(f"Feature preparation error: {e}")
            return pd.DataFrame()
    
    def _prepare_inventory_features(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Prepare features for inventory prediction"""
        history = data.get("history", [])
        if not history:
            return pd.DataFrame()
        
        try:
            df = pd.DataFrame(history)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Create time-based features
            df['day_of_year'] = df['date'].dt.dayofyear
            df['month'] = df['date'].dt.month
            df['week_of_year'] = df['date'].dt.isocalendar().week
            df['day_of_week'] = df['date'].dt.dayofweek
            
            # Create lag features
            df['quantity_lag_1'] = df['quantity'].shift(1)
            df['quantity_lag_7'] = df['quantity'].shift(7)
            
            # Rolling statistics
            df['quantity_ma_7'] = df['quantity'].rolling(window=7, min_periods=1).mean()
            df['quantity_ma_30'] = df['quantity'].rolling(window=30, min_periods=1).mean()
            df['quantity_std_7'] = df['quantity'].rolling(window=7, min_periods=1).std().fillna(0)
            
            # Trend features
            df['quantity_trend'] = df['quantity'].diff()
            
            return df.dropna()
            
        except Exception as e:
            logger.error(f"Inventory feature preparation error: {e}")
            return pd.DataFrame()
    
    def _prepare_budget_features(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Prepare features for budget prediction"""
        expenses = data.get("expenses", [])
        if not expenses:
            return pd.DataFrame()
        
        try:
            df = pd.DataFrame(expenses)
            df['date'] = pd.to_datetime(df['date'])
            
            # Group by date and sum amounts (multiple expenses per day)
            daily_expenses = df.groupby('date')['amount'].sum().reset_index()
            daily_expenses = daily_expenses.sort_values('date')
            
            # Create time features
            daily_expenses['day_of_month'] = daily_expenses['date'].dt.day
            daily_expenses['month'] = daily_expenses['date'].dt.month
            daily_expenses['quarter'] = daily_expenses['date'].dt.quarter
            daily_expenses['day_of_week'] = daily_expenses['date'].dt.dayofweek
            
            # Rolling statistics
            daily_expenses['amount_ma_7'] = daily_expenses['amount'].rolling(window=7, min_periods=1).mean()
            daily_expenses['amount_ma_30'] = daily_expenses['amount'].rolling(window=30, min_periods=1).mean()
            
            # Lag features
            daily_expenses['amount_lag_1'] = daily_expenses['amount'].shift(1)
            daily_expenses['amount_lag_7'] = daily_expenses['amount'].shift(7)
            
            return daily_expenses.fillna(0)
            
        except Exception as e:
            logger.error(f"Budget feature preparation error: {e}")
            return pd.DataFrame()
    
    def _prepare_resource_features(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Prepare features for resource prediction"""
        utilization_data = data.get("utilization_data", [])
        if not utilization_data:
            return pd.DataFrame()
        
        try:
            df = pd.DataFrame(utilization_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Calculate utilization rate
            df['utilization_rate'] = df['utilized_hours'] / df['available_hours'].replace(0, 1)
            df['utilization_rate'] = df['utilization_rate'].fillna(0).clip(0, 1)
            
            # Time features
            df['day_of_week'] = df['date'].dt.dayofweek
            df['month'] = df['date'].dt.month
            df['quarter'] = df['date'].dt.quarter
            
            # Rolling statistics
            df['util_ma_7'] = df['utilization_rate'].rolling(window=7, min_periods=1).mean()
            df['util_ma_30'] = df['utilization_rate'].rolling(window=30, min_periods=1).mean()
            
            return df.fillna(0)
            
        except Exception as e:
            logger.error(f"Resource feature preparation error: {e}")
            return pd.DataFrame()
    
    def _prepare_sales_features(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Prepare features for sales prediction"""
        orders = data.get("orders", [])
        if not orders:
            return pd.DataFrame()
        
        try:
            df = pd.DataFrame(orders)
            df['date'] = pd.to_datetime(df['date'])
            
            # Group by date and sum amounts
            daily_sales = df.groupby('date')['total_amount'].sum().reset_index()
            daily_sales = daily_sales.sort_values('date')
            
            # Time features
            daily_sales['day_of_week'] = daily_sales['date'].dt.dayofweek
            daily_sales['month'] = daily_sales['date'].dt.month
            daily_sales['quarter'] = daily_sales['date'].dt.quarter
            daily_sales['day_of_month'] = daily_sales['date'].dt.day
            
            # Rolling statistics
            daily_sales['sales_ma_7'] = daily_sales['total_amount'].rolling(window=7, min_periods=1).mean()
            daily_sales['sales_ma_30'] = daily_sales['total_amount'].rolling(window=30, min_periods=1).mean()
            
            # Lag features
            daily_sales['sales_lag_1'] = daily_sales['total_amount'].shift(1)
            daily_sales['sales_lag_7'] = daily_sales['total_amount'].shift(7)
            
            return daily_sales.fillna(0)
            
        except Exception as e:
            logger.error(f"Sales feature preparation error: {e}")
            return pd.DataFrame()
    
    def create_future_features(self, df: pd.DataFrame, future_dates: List[datetime], 
                             feature_cols: List[str]) -> np.ndarray:
        """Create features for future dates"""
        try:
            if df.empty or not future_dates:
                return np.array([])
            
            future_features = []
            
            for future_date in future_dates:
                features = []
                
                # Time-based features
                if 'day_of_year' in feature_cols:
                    features.append(future_date.timetuple().tm_yday)
                if 'month' in feature_cols:
                    features.append(future_date.month)
                if 'week_of_year' in feature_cols:
                    features.append(future_date.isocalendar()[1])
                if 'day_of_week' in feature_cols:
                    features.append(future_date.weekday())
                if 'day_of_month' in feature_cols:
                    features.append(future_date.day)
                if 'quarter' in feature_cols:
                    features.append((future_date.month - 1) // 3 + 1)
                
                # For other features, use last known values or statistical measures
                for col in feature_cols:
                    if col not in ['day_of_year', 'month', 'week_of_year', 'day_of_week', 
                                 'day_of_month', 'quarter']:
                        if col in df.columns:
                            # Use last known value for lag and moving average features
                            if any(keyword in col for keyword in ['lag', 'ma', 'std', 'trend']):
                                features.append(df[col].iloc[-1] if not df[col].empty else 0)
                            else:
                                # Use mean for other features
                                features.append(df[col].mean() if not df[col].empty else 0)
                        else:
                            features.append(0)
                
                future_features.append(features)
            
            return np.array(future_features)
            
        except Exception as e:
            logger.error(f"Future feature creation error: {e}")
            return np.array([])

# Global instance
feature_engineer = FeatureEngineer()