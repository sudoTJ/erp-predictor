"""
DGPT Client Service for AI-powered business insights generation
"""
import httpx
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
from config.settings import config

logger = logging.getLogger(__name__)

class DGPTClient:
    """Client for DGPT API integration"""
    
    def __init__(self):
        self.auth_base_url = "https://sst-services.engdeltek.com/auth/v1"
        self.dgpt_base_url = "https://sst-services.engdeltek.com/dgpt/v1"
        self.api_key = config.DELA_API_KEY
        self.customer_id = config.DGPT_CUSTOMER_ID
        self.user_id = config.DGPT_USER_ID
        self._token = None
        self._token_expires = None
    
    async def _authenticate(self) -> str:
        """Get authentication token from auth service"""
        try:
            auth_url = f"{self.auth_base_url}/user_token/{self.customer_id}/{self.user_id}"
            logger.info(f"Authenticating with DGPT auth service at: {auth_url}")
            logger.debug(f"Customer ID: {self.customer_id}, User ID: {self.user_id}")
            
            async with httpx.AsyncClient(timeout=config.DGPT_REQUEST_TIMEOUT) as client:
                response = await client.post(
                    auth_url,
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                
                logger.debug(f"Auth response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    logger.debug(f"Auth response keys: {list(data.keys())}")
                    token = data.get("token")
                    if token:
                        self._token = token
                        logger.info("Successfully authenticated with DGPT auth service")
                        logger.debug(f"Received token (first 20 chars): {token[:20]}...")
                        return token
                    else:
                        logger.error("No token in auth response")
                        logger.error(f"Auth response data: {data}")
                        raise Exception("Authentication failed: no token received")
                else:
                    logger.error(f"Auth failed with status {response.status_code}")
                    logger.error(f"Auth response headers: {dict(response.headers)}")
                    logger.error(f"Auth response text: {response.text}")
                    raise Exception(f"Authentication failed: {response.status_code}")
                    
        except httpx.TimeoutException as e:
            logger.error(f"DGPT authentication timeout: {e}")
            raise Exception("Authentication timeout - check network connectivity")
        except httpx.RequestError as e:
            logger.error(f"DGPT authentication request error: {e}")
            raise Exception(f"Authentication request failed: {e}")
        except Exception as e:
            logger.error(f"DGPT authentication error: {e}")
            logger.error(f"Error type: {type(e)}")
            raise
    
    async def _get_token(self) -> str:
        """Get valid authentication token, refreshing if needed"""
        if self._token is None:
            return await self._authenticate()
        return self._token
    
    async def generate_insights(self, 
                              prediction_data: Dict[str, Any], 
                              prediction_type: str,
                              historical_context: Dict[str, Any] = None) -> List[str]:
        """Generate business insights using DGPT"""
        try:
            if not config.DGPT_ENABLED:
                logger.info("DGPT integration disabled, skipping AI insights")
                return []
                
            token = await self._get_token()
            
            # Create business-focused prompt
            prompt = self._create_business_prompt(prediction_data, prediction_type, historical_context)
            
            # Prepare DGPT request payload
            dgpt_payload = {
                "gpt_completion_payload": {
                    "messages": [
                        {
                            "content": prompt,
                            "role": "user"
                        }
                    ]
                },
                "session_uuid": f"erp-prediction-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "completion_index": 0,
            }
            
            # Make DGPT API call
            completion_url = f"{self.dgpt_base_url}/completion"
            
            async with httpx.AsyncClient(timeout=config.DGPT_REQUEST_TIMEOUT) as client:
                response = await client.post(
                    completion_url,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    },
                    json=dgpt_payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    completion = data.get("completion", {})
                    choices = completion.get("choices", [])
                    
                    if choices and len(choices) > 0:
                        message_content = choices[0].get("message", {}).get("content", "")
                        if message_content:
                            # Parse insights from AI response
                            insights = self._parse_ai_insights(message_content)
                            logger.info(f"Generated {len(insights)} AI-powered insights")
                            return insights
                        else:
                            logger.warning("Empty content in DGPT response")
                    else:
                        logger.warning("No choices in DGPT response")
                else:
                    error_text = response.text
                    try:
                        error_data = response.json()
                        if "detail" in error_data:
                            error_msg = error_data["detail"]
                            if isinstance(error_msg, list) and len(error_msg) > 0:
                                error_msg = error_msg[0].get("msg", str(error_msg))
                            logger.error(f"DGPT completion failed: {response.status_code} - {error_msg}")
                        else:
                            logger.error(f"DGPT completion failed: {response.status_code} - {error_text}")
                    except:
                        logger.error(f"DGPT completion failed: {response.status_code} - {error_text}")
            
            return []
            
        except Exception as e:
            logger.error(f"DGPT insights generation error: {e}")
            return []
    
    def _create_business_prompt(self, 
                              prediction_data: Dict[str, Any], 
                              prediction_type: str,
                              historical_context: Dict[str, Any] = None) -> str:
        """Create business-focused prompt for DGPT"""
        
        # Extract key data points
        predictions = prediction_data.get('predictions', [])
        metadata = prediction_data.get('metadata', {})
        entity_id = prediction_data.get('entity_id', 'Unknown')
        time_horizon = len(predictions)
        
        if not predictions:
            return "No prediction data available for analysis."
        
        # Calculate trend and statistics
        values = [p.get('predicted_value', 0) for p in predictions]
        confidences = [p.get('confidence', 0) for p in predictions]
        
        first_value = values[0] if values else 0
        last_value = values[-1] if values else 0
        avg_value = sum(values) / len(values) if values else 0
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        trend_pct = ((last_value - first_value) / first_value * 100) if first_value != 0 else 0
        
        # Build context-aware prompt based on prediction type
        base_prompt = f"""You are a senior business analyst providing strategic insights for {prediction_type} management.

PREDICTION DATA:
- Entity: {entity_id}
- Forecast Period: {time_horizon} days
- Trend: {trend_pct:+.1f}% change expected
- Average Predicted Value: {avg_value:.2f}
- Confidence Level: {avg_confidence:.1%}
- Values Range: {min(values):.2f} to {max(values):.2f}

"""
        
        # Add prediction type specific context
        if prediction_type == "inventory":
            specific_prompt = """INVENTORY CONTEXT:
You're analyzing product demand forecasting for inventory management. Consider:
- Stock-out risks and customer impact
- Carrying costs and storage constraints  
- Seasonal patterns and market trends
- Supplier lead times and reorder points

Provide 3-4 concise, actionable business insights focusing on:
1. Immediate actions needed (reorder, adjust stock levels)
2. Risk assessment (stock-out probability, overstock risk)
3. Strategic recommendations (inventory optimization, supplier strategy)
4. Financial impact (cost savings, revenue protection)

Format each insight as a clear, actionable business recommendation."""

        elif prediction_type == "budget":
            specific_prompt = """BUDGET CONTEXT:
You're analyzing departmental spending patterns for financial planning. Consider:
- Budget variance and spending velocity
- Departmental priorities and business impact
- Cost control opportunities and efficiency gains
- Cash flow implications and seasonal factors

Provide 3-4 concise, actionable business insights focusing on:
1. Budget status and variance analysis
2. Spending trend implications and risks  
3. Cost control recommendations
4. Resource reallocation opportunities

Format each insight as a clear, actionable financial recommendation."""

        elif prediction_type == "resource":
            specific_prompt = """RESOURCE PLANNING CONTEXT:
You're analyzing team utilization and workforce planning. Consider:
- Capacity constraints and bottlenecks
- Employee burnout and productivity impacts
- Hiring lead times and onboarding costs
- Skills gaps and training needs

Provide 3-4 concise, actionable business insights focusing on:
1. Current utilization assessment and capacity gaps
2. Workforce planning recommendations (hiring, redistribution)
3. Productivity optimization opportunities
4. Risk mitigation for resource shortages

Format each insight as a clear, actionable HR/operations recommendation."""

        elif prediction_type == "sales":
            specific_prompt = """SALES FORECASTING CONTEXT:
You're analyzing revenue trends and sales performance. Consider:
- Market conditions and competitive landscape
- Pipeline health and conversion rates
- Seasonal factors and customer behavior
- Sales team performance and territory management

Provide 3-4 concise, actionable business insights focusing on:
1. Revenue trajectory and growth opportunities
2. Sales strategy optimization recommendations
3. Market risk assessment and mitigation
4. Resource allocation for sales acceleration

Format each insight as a clear, actionable sales/revenue recommendation."""
        
        else:
            specific_prompt = """Provide 3-4 concise, actionable business insights based on the prediction data."""
        
        return base_prompt + specific_prompt
    
    def _parse_ai_insights(self, ai_response: str) -> List[str]:
        """Parse AI response into structured insights"""
        try:
            # Split response into individual insights
            lines = ai_response.strip().split('\n')
            insights = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Remove numbering, bullets, and formatting
                cleaned_line = line
                for prefix in ['1. ', '2. ', '3. ', '4. ', '5. ', '- ', '• ', '* ']:
                    if cleaned_line.startswith(prefix):
                        cleaned_line = cleaned_line[len(prefix):].strip()
                        break
                
                # Only include substantial insights (not just headers)
                if len(cleaned_line) > 20 and not cleaned_line.endswith(':'):
                    insights.append(cleaned_line)
            
            # Limit to top 5 insights for UI clarity
            return insights[:5]
            
        except Exception as e:
            logger.error(f"Error parsing AI insights: {e}")
            # Fallback: return the raw response as a single insight
            return [ai_response.strip()] if ai_response.strip() else []

# Global instance
dgpt_client = DGPTClient()