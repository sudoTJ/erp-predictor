"""
Service for fetching data from ERP systems
"""
import httpx
from typing import Dict, Any, Optional
import logging
from config.settings import config

logger = logging.getLogger(__name__)

class ERPDataFetcher:
    """Service to fetch historical data from ERP service"""
    
    def __init__(self):
        self.erp_url = config.ERP_SERVICE_URL
        self.timeout = config.REQUEST_TIMEOUT
    
    async def fetch_historical_data(self, prediction_type: str, entity_id: str) -> Dict[str, Any]:
        """Fetch relevant historical data based on prediction type"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = self._build_url(prediction_type, entity_id)
                logger.info(f"Fetching data from: {url}")
                
                response = await client.get(url)
                
                if response.status_code != 200:
                    logger.error(f"ERP service error: {response.status_code} - {response.text}")
                    raise ValueError(f"Failed to fetch ERP data: {response.status_code}")
                
                data = response.json()
                logger.info(f"Successfully fetched data for {prediction_type}:{entity_id}")
                return data
                
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise ConnectionError("Failed to connect to ERP service")
        except Exception as e:
            logger.error(f"Unexpected error fetching data: {e}")
            raise
    
    def _build_url(self, prediction_type: str, entity_id: str) -> str:
        """Build appropriate URL based on prediction type"""
        base_url = self.erp_url
        
        if prediction_type == "inventory":
            return f"{base_url}/inventory/{entity_id}/history?days=180"
        elif prediction_type == "budget":
            return f"{base_url}/finance/expenses?category={entity_id}&days=180"
        elif prediction_type == "resource":
            # This would need to be implemented in ERP service
            return f"{base_url}/hr/utilization?department={entity_id}&days=180"
        elif prediction_type == "sales":
            return f"{base_url}/sales/orders?days=180"
        else:
            raise ValueError(f"Unknown prediction type: {prediction_type}")
    
    async def health_check(self) -> Dict[str, str]:
        """Check if ERP service is healthy"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.erp_url.replace('/api/v1', '')}/health")
                
                if response.status_code == 200:
                    return {"erp_service": "healthy"}
                else:
                    return {"erp_service": f"unhealthy ({response.status_code})"}
                    
        except Exception as e:
            logger.error(f"ERP health check failed: {e}")
            return {"erp_service": "unhealthy (connection_failed)"}

# Global instance
data_fetcher = ERPDataFetcher()