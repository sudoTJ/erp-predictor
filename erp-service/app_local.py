
from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)
DATABASE = "../erp_demo.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/v1/inventory/items')
def get_inventory_items():
    try:
        conn = get_db_connection()
        items = conn.execute("""
            SELECT sku, name, current_stock, category, unit_cost 
            FROM inventory_items 
            ORDER BY sku
        """).fetchall()
        
        result = {
            "items": [
                {
                    "sku": item["sku"],
                    "name": item["name"], 
                    "current_stock": item["current_stock"],
                    "category": item["category"],
                    "unit_cost": float(item["unit_cost"]) if item["unit_cost"] else 0
                } for item in items
            ]
        }
        
        conn.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/inventory/<sku>/history')
def get_inventory_history(sku):
    try:
        days = request.args.get('days', 90, type=int)
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        conn = get_db_connection()
        history = conn.execute("""
            SELECT transaction_date, quantity, unit_price
            FROM inventory_transactions 
            WHERE sku = ? AND transaction_date >= ?
            ORDER BY transaction_date
        """, (sku, start_date)).fetchall()
        
        result = {
            "sku": sku,
            "history": [
                {
                    "date": item["transaction_date"],
                    "quantity": abs(item["quantity"]),  # Make positive for demand
                    "unit_price": float(item["unit_price"]) if item["unit_price"] else 0
                } for item in history
            ]
        }
        
        conn.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/finance/expenses')
def get_expenses():
    try:
        category = request.args.get('category', '')
        days = request.args.get('days', 90, type=int)
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        conn = get_db_connection()
        
        if category:
            query = """
                SELECT bc.category_name, bc.annual_budget, 
                       er.expense_date, er.amount, er.description
                FROM budget_categories bc
                LEFT JOIN expense_records er ON bc.id = er.category_id
                WHERE bc.category_name = ? AND (er.expense_date >= ? OR er.expense_date IS NULL)
                ORDER BY er.expense_date DESC
            """
            expenses = conn.execute(query, (category, start_date)).fetchall()
        else:
            query = """
                SELECT bc.category_name, bc.annual_budget,
                       er.expense_date, er.amount, er.description
                FROM budget_categories bc
                LEFT JOIN expense_records er ON bc.id = er.category_id
                WHERE er.expense_date >= ? OR er.expense_date IS NULL
                ORDER BY bc.category_name, er.expense_date DESC
            """
            expenses = conn.execute(query, (start_date,)).fetchall()
        
        # Group by category
        categories = {}
        for expense in expenses:
            cat_name = expense["category_name"]
            if cat_name not in categories:
                categories[cat_name] = {
                    "category": cat_name,
                    "total_budget": float(expense["annual_budget"]) if expense["annual_budget"] else 0,
                    "expenses": []
                }
            
            if expense["expense_date"]:
                categories[cat_name]["expenses"].append({
                    "date": expense["expense_date"],
                    "amount": float(expense["amount"]) if expense["amount"] else 0,
                    "description": expense["description"] or ""
                })
        
        if category and category in categories:
            result = categories[category]
        else:
            result = {"categories": list(categories.values())}
        
        conn.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting ERP Service on http://localhost:3001")
    app.run(host='localhost', port=3001, debug=True)
