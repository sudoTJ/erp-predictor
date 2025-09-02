"""
Database connection and models for ERP Service
Supports both SQLite (local) and PostgreSQL (Docker)
"""
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
from config.settings import config

# Import PostgreSQL adapter only if needed
if config.USE_POSTGRES:
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
    except ImportError:
        print("Warning: psycopg2 not available for PostgreSQL connection")
        psycopg2 = None

class DatabaseManager:
    """Database connection and query manager"""
    
    def __init__(self):
        self.use_postgres = config.USE_POSTGRES
        
    def get_connection(self):
        """Get database connection with row factory"""
        if self.use_postgres and psycopg2:
            # PostgreSQL connection for Docker
            conn = psycopg2.connect(
                host=config.DB_HOST,
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                port=config.DB_PORT
            )
            return conn
        else:
            # SQLite connection for local development
            conn = sqlite3.connect(config.DATABASE_PATH, timeout=config.DB_CONNECTION_TIMEOUT)
            conn.row_factory = sqlite3.Row
            return conn
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute a SELECT query and return results"""
        with self.get_connection() as conn:
            if self.use_postgres and psycopg2:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute(query, params)
                return cursor.fetchall()
            else:
                rows = conn.execute(query, params).fetchall()
                return [dict(row) for row in rows]
    
    def execute_single(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Execute a SELECT query and return single result"""
        with self.get_connection() as conn:
            if self.use_postgres and psycopg2:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute(query, params)
                result = cursor.fetchone()
                return dict(result) if result else None
            else:
                row = conn.execute(query, params).fetchone()
                return dict(row) if row else None

class InventoryModel:
    """Data model for inventory operations"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def get_all_items(self) -> List[Dict[str, Any]]:
        """Get all inventory items"""
        query = """
            SELECT sku, name, current_stock, category, unit_cost 
            FROM inventory_items 
            ORDER BY sku
        """
        rows = self.db.execute_query(query)
        return [
            {
                "sku": row["sku"],
                "name": row["name"], 
                "current_stock": row["current_stock"],
                "category": row["category"],
                "unit_cost": float(row["unit_cost"]) if row["unit_cost"] else 0
            } 
            for row in rows
        ]
    
    def get_item_history(self, sku: str, start_date: str) -> List[Dict[str, Any]]:
        """Get transaction history for a specific SKU"""
        query = """
            SELECT transaction_date, quantity, unit_price
            FROM inventory_transactions 
            WHERE sku = ? AND transaction_date >= ?
            ORDER BY transaction_date
        """
        rows = self.db.execute_query(query, (sku, start_date))
        return [
            {
                "date": row["transaction_date"],
                "quantity": abs(row["quantity"]),  # Make positive for demand
                "unit_price": float(row["unit_price"]) if row["unit_price"] else 0
            }
            for row in rows
        ]

class FinanceModel:
    """Data model for finance operations"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def get_expenses_by_category(self, category: str, start_date: str) -> Dict[str, Any]:
        """Get expenses for a specific category"""
        query = """
            SELECT bc.category_name, bc.annual_budget, 
                   er.expense_date, er.amount, er.description
            FROM budget_categories bc
            LEFT JOIN expense_records er ON bc.id = er.category_id
            WHERE bc.category_name = ? AND (er.expense_date >= ? OR er.expense_date IS NULL)
            ORDER BY er.expense_date DESC
        """
        rows = self.db.execute_query(query, (category, start_date))
        
        if not rows:
            return {}
        
        # Group data
        first_row = rows[0]
        result = {
            "category": first_row["category_name"],
            "total_budget": float(first_row["annual_budget"]) if first_row["annual_budget"] else 0,
            "expenses": []
        }
        
        for row in rows:
            if row["expense_date"]:
                result["expenses"].append({
                    "date": row["expense_date"],
                    "amount": float(row["amount"]) if row["amount"] else 0,
                    "description": row["description"] or ""
                })
        
        return result
    
    def get_all_expenses(self, start_date: str) -> Dict[str, Any]:
        """Get all expenses grouped by category"""
        query = """
            SELECT bc.category_name, bc.annual_budget,
                   er.expense_date, er.amount, er.description
            FROM budget_categories bc
            LEFT JOIN expense_records er ON bc.id = er.category_id
            WHERE er.expense_date >= ? OR er.expense_date IS NULL
            ORDER BY bc.category_name, er.expense_date DESC
        """
        rows = self.db.execute_query(query, (start_date,))
        
        # Group by category
        categories = {}
        for row in rows:
            cat_name = row["category_name"]
            if cat_name not in categories:
                categories[cat_name] = {
                    "category": cat_name,
                    "total_budget": float(row["annual_budget"]) if row["annual_budget"] else 0,
                    "expenses": []
                }
            
            if row["expense_date"]:
                categories[cat_name]["expenses"].append({
                    "date": row["expense_date"],
                    "amount": float(row["amount"]) if row["amount"] else 0,
                    "description": row["description"] or ""
                })
        
        return {"categories": list(categories.values())}

# Global database instance
db_manager = DatabaseManager()
inventory_model = InventoryModel(db_manager)
finance_model = FinanceModel(db_manager)