"""
API client for communicating with backend services
"""
import requests
import streamlit as st
from typing import Dict, Any, Optional
from config.settings import config
import logging

logger = logging.getLogger(__name__)

class APIClient:
    """Client for backend API communication"""
    
    def __init__(self):
        self.prediction_url = config.PREDICTION_API_URL
        self.erp_url = config.ERP_API_URL
        self.timeout = 60  # Increased for DGPT AI processing
    
    def make_prediction(self, prediction_type: str, entity_id: str, 
                       time_horizon: int, context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make prediction request"""
        try:
            payload = {
                "prediction_type": prediction_type,
                "entity_id": entity_id,
                "time_horizon": time_horizon,
                "context": context or {}
            }
            
            response = requests.post(
                f"{self.prediction_url}/predict",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Prediction API error: {response.status_code}")
                st.error(f"API Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            st.error("AI insights generation timed out. DGPT may be busy - please try again.")
            return None
        except requests.exceptions.ConnectionError:
            st.error("Unable to connect to prediction service. Please check if the service is running.")
            return None
        except Exception as e:
            logger.error(f"Prediction request error: {e}")
            st.error(f"Error: {str(e)}")
            return None
    
    def get_prediction_types(self) -> Optional[Dict[str, Any]]:
        """Get available prediction types"""
        try:
            response = requests.get(
                f"{self.prediction_url}/predict/types",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            logger.error(f"Get prediction types error: {e}")
            return None
    
    def check_health(self) -> Dict[str, str]:
        """Check health of backend services"""
        health_status = {}
        
        # Check prediction service
        try:
            response = requests.get(f"{self.prediction_url.replace('/api/v1', '')}/health", timeout=5)
            if response.status_code == 200:
                health_status["prediction_service"] = "✅ Healthy"
            else:
                health_status["prediction_service"] = f"❌ Error ({response.status_code})"
        except Exception:
            health_status["prediction_service"] = "❌ Offline"
        
        # Check ERP service
        try:
            response = requests.get(f"{self.erp_url.replace('/api/v1', '')}/health", timeout=5)
            if response.status_code == 200:
                health_status["erp_service"] = "✅ Healthy"
            else:
                health_status["erp_service"] = f"❌ Error ({response.status_code})"
        except Exception:
            health_status["erp_service"] = "❌ Offline"
        
        return health_status
    
    def get_inventory_items(self) -> Optional[Dict[str, Any]]:
        """Get available inventory items"""
        try:
            response = requests.get(f"{self.erp_url}/inventory/items", timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Get inventory items error: {e}")
            return None

# Global API client instance
api_client = APIClient()