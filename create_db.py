import sqlite3
from datetime import datetime, timedelta
import random
import os

# Create database
db_path = "erp_demo.db"
if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create tables
print("Creating tables...")

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

print("Inserting sample data...")

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
            ''', (sku, current_date.strftime('%Y-%m-%d'), 'sale', quantity, cost * 1.2))
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
print(f"Database created successfully: {db_path}")
print("Tables and sample data ready!")