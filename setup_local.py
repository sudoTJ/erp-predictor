import subprocess
import sys
import os
import sqlite3
from datetime import datetime, timedelta
import random

def install_packages():
    """Install required Python packages"""
    packages = [
        "flask",
        "fastapi",
        "uvicorn",
        "requests",
        "pandas", 
        "scikit-learn",
        "httpx"
    ]
    
    print("Installing required packages...")
    for package in packages:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def create_sqlite_db():
    """Create SQLite database with sample data"""
    db_path = "erp_demo.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    print("Creating database tables...")
    
    # Inventory tables
    cursor.execute('''
    CREATE TABLE inventory_items (
        id INTEGER PRIMARY KEY,
        sku TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        category TEXT,
        current_stock INTEGER DEFAULT 0,
        unit_cost REAL
    )''')
    
    cursor.execute('''
    CREATE TABLE inventory_transactions (
        id INTEGER PRIMARY KEY,
        sku TEXT,
        transaction_date DATE,
        transaction_type TEXT,
        quantity INTEGER,
        unit_price REAL
    )''')
    
    # Budget tables
    cursor.execute('''
    CREATE TABLE budget_categories (
        id INTEGER PRIMARY KEY,
        category_name TEXT UNIQUE,
        annual_budget REAL
    )''')
    
    cursor.execute('''
    CREATE TABLE expense_records (
        id INTEGER PRIMARY KEY,
        category_id INTEGER,
        expense_date DATE,
        amount REAL,
        description TEXT
    )''')
    
    print("Generating sample data...")
    
    # Insert sample inventory items
    products = [
        ("SKU001", "Laptop Dell Inspiron", "Electronics", 150, 2500),
        ("SKU002", "Office Chair Premium", "Furniture", 75, 150),
        ("SKU003", "Wireless Mouse", "Electronics", 200, 25),
        ("SKU004", "Standing Desk", "Furniture", 45, 300),
        ("SKU005", "USB Cable", "Electronics", 300, 5)
    ]
    
    for sku, name, category, stock, cost in products:
        cursor.execute('''
        INSERT INTO inventory_items (sku, name, category, current_stock, unit_cost)
        VALUES (?, ?, ?, ?, ?)
        ''', (sku, name, category, stock, cost))
    
    # Generate inventory transactions (6 months)
    start_date = datetime.now() - timedelta(days=180)
    for sku, name, category, stock, cost in products:
        current_date = start_date
        while current_date <= datetime.now():
            if random.random() > 0.3:  # 70% chance of transaction
                quantity = random.randint(1, 15)
                cursor.execute('''
                INSERT INTO inventory_transactions (sku, transaction_date, transaction_type, quantity, unit_price)
                VALUES (?, ?, ?, ?, ?)
                ''', (sku, current_date.strftime('%Y-%m-%d'), 'sale', -quantity, cost * 1.2))
            current_date += timedelta(days=1)
    
    # Insert budget categories
    categories = [
        ("Marketing", 120000),
        ("Engineering", 800000),
        ("Operations", 200000),
        ("HR", 150000)
    ]
    
    category_ids = {}
    for cat_name, budget in categories:
        cursor.execute('''
        INSERT INTO budget_categories (category_name, annual_budget)
        VALUES (?, ?)
        ''', (cat_name, budget))
        category_ids[cat_name] = cursor.lastrowid
    
    # Generate expense records
    start_date = datetime.now() - timedelta(days=180)
    for cat_name, budget in categories:
        monthly_budget = budget / 12
        current_date = start_date
        while current_date <= datetime.now():
            if current_date.day <= 28:
                for _ in range(random.randint(3, 8)):
                    expense_date = current_date + timedelta(days=random.randint(0, 27))
                    if expense_date <= datetime.now():
                        amount = monthly_budget * random.uniform(0.05, 0.25)
                        cursor.execute('''
                        INSERT INTO expense_records (category_id, expense_date, amount, description)
                        VALUES (?, ?, ?, ?)
                        ''', (category_ids[cat_name], expense_date.strftime('%Y-%m-%d'), amount, f"{cat_name} expense"))
            current_date += timedelta(days=30)
    
    conn.commit()
    conn.close()
    print(f"Sample database created: {db_path}")

def update_erp_service():
    """Update ERP service to use SQLite"""
    erp_app_content = '''
from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)
DATABASE = "erp_demo.db"

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
'''
    
    with open('erp-service/app_local.py', 'w') as f:
        f.write(erp_app_content)
    print("Created erp-service/app_local.py for SQLite")

def update_prediction_service():
    """Update prediction service for local testing"""
    # The existing prediction service should work, just need to change ERP_SERVICE_URL
    pred_content = '''
import os
os.environ['ERP_SERVICE_URL'] = 'http://localhost:3001/api/v1'
'''
    with open('prediction-service/local_config.py', 'w') as f:
        f.write(pred_content)

if __name__ == "__main__":
    print("Setting up ERP Prediction System for local testing...")
    print("=" * 50)
    
    try:
        install_packages()
        create_sqlite_db()
        update_erp_service()
        update_prediction_service()
        
        print("\\n" + "=" * 50)
        print("Setup complete! 🚀")
        print("\\nTo start the system:")
        print("1. Terminal 1: cd erp-service && python app_local.py")
        print("2. Terminal 2: cd prediction-service && python app.py")
        print("\\nThen test with:")
        print("curl http://localhost:3001/api/v1/inventory/items")
        print("curl -X POST http://localhost:3002/api/v1/predict -H 'Content-Type: application/json' -d '{\"prediction_type\": \"inventory\", \"entity_id\": \"SKU001\", \"time_horizon\": 30}'")
        
    except Exception as e:
        print(f"Setup failed: {e}")
        sys.exit(1)