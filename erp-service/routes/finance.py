"""
Finance-related routes
"""
from flask import Blueprint, jsonify, request
from services.finance_service import finance_service
from utils.helpers import handle_api_error

finance_bp = Blueprint('finance', __name__, url_prefix='/api/v1/finance')

@finance_bp.route('/expenses')
@handle_api_error
def get_expenses():
    """Get expense analysis by category or all categories"""
    category = request.args.get('category', '').strip()
    days = request.args.get('days', 90, type=int)
    
    # Validate days parameter
    if days < 1 or days > 365:
        return jsonify({"error": "Days parameter must be between 1 and 365"}), 400
    
    result = finance_service.get_expense_analysis(category if category else None, days)
    
    if category and not result:
        return jsonify({"error": f"No data found for category: {category}"}), 404
    
    return jsonify(result)

@finance_bp.route('/categories')
@handle_api_error  
def get_budget_categories():
    """Get all available budget categories"""
    # This could be extended to return just category names
    result = finance_service.get_expense_analysis(days=1)  # Get recent data
    
    if 'categories' in result:
        categories = [{"name": cat["category"], "budget": cat["total_budget"]} 
                     for cat in result['categories']]
        return jsonify({"categories": categories})
    
    return jsonify({"categories": []})