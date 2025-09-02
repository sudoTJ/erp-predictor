"""
Inventory-related routes
"""
from flask import Blueprint, jsonify, request
from services.inventory_service import inventory_service
from utils.helpers import handle_api_error

inventory_bp = Blueprint('inventory', __name__, url_prefix='/api/v1/inventory')

@inventory_bp.route('/items')
@handle_api_error
def get_inventory_items():
    """Get all inventory items"""
    result = inventory_service.get_all_inventory_items()
    return jsonify(result)

@inventory_bp.route('/<sku>/history')
@handle_api_error
def get_inventory_history(sku):
    """Get transaction history for a specific SKU"""
    days = request.args.get('days', 90, type=int)
    
    # Validate days parameter
    if days < 1 or days > 365:
        return jsonify({"error": "Days parameter must be between 1 and 365"}), 400
    
    result = inventory_service.get_item_transaction_history(sku, days)
    
    if not result['history']:
        return jsonify({"error": f"No transaction history found for SKU: {sku}"}), 404
    
    return jsonify(result)