"""
Utility functions and decorators
"""
from functools import wraps
from flask import jsonify
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_api_error(f):
    """Decorator to handle API errors gracefully"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"API Error in {f.__name__}: {str(e)}")
            return jsonify({"error": str(e)}), 500
    return decorated_function

def validate_sku(sku: str) -> bool:
    """Validate SKU format"""
    return sku and len(sku.strip()) > 0 and sku.strip().startswith('SKU')

def validate_category(category: str) -> bool:
    """Validate category name"""
    valid_categories = ['Marketing', 'Engineering', 'Operations', 'HR']
    return category in valid_categories