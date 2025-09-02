"""
Business logic for inventory operations
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from models.database import inventory_model

class InventoryService:
    """Service class for inventory business logic"""
    
    def __init__(self):
        self.inventory_model = inventory_model
    
    def get_all_inventory_items(self) -> Dict[str, Any]:
        """Get all inventory items with business logic"""
        items = self.inventory_model.get_all_items()
        
        # Add business logic here if needed
        # e.g., calculate reorder alerts, stock status, etc.
        for item in items:
            item['stock_status'] = self._get_stock_status(item['current_stock'])
            item['needs_reorder'] = item['current_stock'] < 50  # Simple reorder logic
        
        return {"items": items}
    
    def get_item_transaction_history(self, sku: str, days: int = 90) -> Dict[str, Any]:
        """Get transaction history for a specific item"""
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        history = self.inventory_model.get_item_history(sku, start_date)
        
        # Add business insights
        total_demand = sum(item['quantity'] for item in history)
        avg_daily_demand = total_demand / max(days, 1)
        
        return {
            "sku": sku,
            "history": history,
            "summary": {
                "total_demand": total_demand,
                "avg_daily_demand": round(avg_daily_demand, 2),
                "data_points": len(history)
            }
        }
    
    def _get_stock_status(self, current_stock: int) -> str:
        """Determine stock status based on current stock level"""
        if current_stock < 25:
            return "critical"
        elif current_stock < 50:
            return "low"
        elif current_stock < 100:
            return "normal"
        else:
            return "high"

# Global service instance
inventory_service = InventoryService()