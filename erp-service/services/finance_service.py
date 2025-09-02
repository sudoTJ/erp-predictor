"""
Business logic for finance operations
"""
from typing import Dict, Any
from datetime import datetime, timedelta
from models.database import finance_model

class FinanceService:
    """Service class for finance business logic"""
    
    def __init__(self):
        self.finance_model = finance_model
    
    def get_expense_analysis(self, category: str = None, days: int = 90) -> Dict[str, Any]:
        """Get expense analysis with business insights"""
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        if category:
            data = self.finance_model.get_expenses_by_category(category, start_date)
            if data:
                data.update(self._calculate_budget_metrics(data, days))
            return data
        else:
            data = self.finance_model.get_all_expenses(start_date)
            # Add metrics for each category
            for cat_data in data['categories']:
                cat_data.update(self._calculate_budget_metrics(cat_data, days))
            return data
    
    def _calculate_budget_metrics(self, category_data: Dict[str, Any], days: int) -> Dict[str, Any]:
        """Calculate budget-related metrics for a category"""
        expenses = category_data.get('expenses', [])
        total_budget = category_data.get('total_budget', 0)
        
        # Calculate totals
        total_spent = sum(expense['amount'] for expense in expenses)
        daily_average = total_spent / max(days, 1)
        
        # Calculate projections
        monthly_projection = daily_average * 30
        annual_projection = daily_average * 365
        
        # Budget utilization
        budget_utilization = (total_spent / total_budget * 100) if total_budget > 0 else 0
        
        # Variance analysis
        monthly_budget = total_budget / 12
        variance = monthly_projection - monthly_budget
        variance_percentage = (variance / monthly_budget * 100) if monthly_budget > 0 else 0
        
        return {
            "metrics": {
                "total_spent_period": round(total_spent, 2),
                "daily_average": round(daily_average, 2),
                "monthly_projection": round(monthly_projection, 2),
                "annual_projection": round(annual_projection, 2),
                "budget_utilization_percent": round(budget_utilization, 1),
                "monthly_variance": round(variance, 2),
                "variance_percentage": round(variance_percentage, 1),
                "expense_count": len(expenses)
            },
            "status": self._get_budget_status(budget_utilization, variance_percentage)
        }
    
    def _get_budget_status(self, utilization: float, variance_pct: float) -> str:
        """Determine budget status based on utilization and variance"""
        if variance_pct > 20:
            return "over_budget"
        elif variance_pct > 10:
            return "at_risk"
        elif utilization < 50:
            return "under_utilized"
        else:
            return "on_track"

# Global service instance
finance_service = FinanceService()