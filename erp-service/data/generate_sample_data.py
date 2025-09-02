import psycopg2
import random
from datetime import datetime, timedelta
import os

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'erp_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'password')
    )

def generate_inventory_data():
    """Generate realistic inventory data for demo"""
    products = [
        ("SKU001", "Laptop Dell Inspiron", "Electronics", 2500),
        ("SKU002", "Office Chair Premium", "Furniture", 150),
        ("SKU003", "Wireless Mouse", "Electronics", 25),
        ("SKU004", "Standing Desk", "Furniture", 300),
        ("SKU005", "USB Cable", "Electronics", 5)
    ]
    
    # Generate 6 months of transaction history
    start_date = datetime.now() - timedelta(days=180)
    
    transactions = []
    for sku, name, category, unit_cost in products:
        current_date = start_date
        stock_level = random.randint(200, 500)
        
        while current_date <= datetime.now():
            # Generate sales (daily) - different patterns per product
            if sku == "SKU001":  # Laptop - steady high-value sales
                if random.random() > 0.4:  # 60% chance of sales
                    daily_sales = random.randint(1, 5)
                    transactions.append((
                        sku, current_date.date(), 'sale', 
                        -daily_sales, unit_cost * 1.2, 
                        -daily_sales * unit_cost * 1.2
                    ))
                    stock_level -= daily_sales
            
            elif sku == "SKU002":  # Chair - seasonal pattern
                seasonal_factor = 1.5 if current_date.month in [9, 10, 1] else 1.0  # Back-to-office seasons
                if random.random() > 0.3:  # 70% chance of sales
                    daily_sales = int(random.randint(2, 8) * seasonal_factor)
                    transactions.append((
                        sku, current_date.date(), 'sale', 
                        -daily_sales, unit_cost * 1.3, 
                        -daily_sales * unit_cost * 1.3
                    ))
                    stock_level -= daily_sales
            
            elif sku == "SKU003":  # Mouse - high volume, steady
                if random.random() > 0.2:  # 80% chance of sales
                    daily_sales = random.randint(5, 20)
                    transactions.append((
                        sku, current_date.date(), 'sale', 
                        -daily_sales, unit_cost * 1.4, 
                        -daily_sales * unit_cost * 1.4
                    ))
                    stock_level -= daily_sales
            
            else:  # Other products - normal distribution
                if random.random() > 0.3:  # 70% chance of sales
                    daily_sales = random.randint(1, 15)
                    transactions.append((
                        sku, current_date.date(), 'sale', 
                        -daily_sales, unit_cost * 1.25, 
                        -daily_sales * unit_cost * 1.25
                    ))
                    stock_level -= daily_sales
            
            # Generate restocking (weekly)
            if current_date.weekday() == 0 and stock_level < 50:
                restock_qty = random.randint(100, 300)
                transactions.append((
                    sku, current_date.date(), 'purchase',
                    restock_qty, unit_cost,
                    restock_qty * unit_cost
                ))
                stock_level += restock_qty
            
            current_date += timedelta(days=1)
    
    return products, transactions

def generate_budget_data():
    """Generate realistic budget and expense data"""
    categories = [
        ("Marketing", "Sales", 120000),
        ("Engineering", "Technology", 800000),
        ("Operations", "Operations", 200000),
        ("HR", "Human Resources", 150000)
    ]
    
    expenses = []
    start_date = datetime.now() - timedelta(days=180)
    
    for cat_name, department, annual_budget in categories:
        current_date = start_date
        monthly_budget = annual_budget / 12
        
        # Generate different spending patterns per category
        if cat_name == "Marketing":
            # Marketing - higher variability, campaign-based
            while current_date <= datetime.now():
                if current_date.day <= 28:
                    # Campaign months vs regular months
                    is_campaign_month = random.random() > 0.7
                    expense_multiplier = 1.5 if is_campaign_month else 0.8
                    
                    num_expenses = random.randint(8, 15) if is_campaign_month else random.randint(3, 8)
                    for _ in range(num_expenses):
                        expense_date = current_date + timedelta(days=random.randint(0, 27))
                        if expense_date <= datetime.now():
                            base_amount = monthly_budget * random.uniform(0.05, 0.25)
                            amount = base_amount * expense_multiplier
                            description = f"Marketing campaign expense" if is_campaign_month else f"Regular marketing expense"
                            expenses.append((
                                cat_name, expense_date.date(), amount,
                                description, "Marketing Manager"
                            ))
                current_date += timedelta(days=30)
        
        elif cat_name == "Engineering":
            # Engineering - steady, predictable spending
            while current_date <= datetime.now():
                if current_date.day <= 28:
                    num_expenses = random.randint(5, 10)  # Consistent spending
                    for _ in range(num_expenses):
                        expense_date = current_date + timedelta(days=random.randint(0, 27))
                        if expense_date <= datetime.now():
                            amount = monthly_budget * random.uniform(0.08, 0.15)  # Steady amounts
                            expenses.append((
                                cat_name, expense_date.date(), amount,
                                f"Engineering tools and infrastructure", "Engineering Lead"
                            ))
                current_date += timedelta(days=30)
        
        else:
            # Other departments - normal pattern
            while current_date <= datetime.now():
                if current_date.day <= 28:
                    num_expenses = random.randint(3, 8)
                    for _ in range(num_expenses):
                        expense_date = current_date + timedelta(days=random.randint(0, 27))
                        if expense_date <= datetime.now():
                            amount = monthly_budget * random.uniform(0.05, 0.25)
                            expenses.append((
                                cat_name, expense_date.date(), amount,
                                f"Monthly {cat_name.lower()} expense", "Department Head"
                            ))
                current_date += timedelta(days=30)
    
    return categories, expenses

def generate_hr_data():
    """Generate HR utilization data"""
    departments = [
        ("Engineering", 25, 500000),
        ("Sales", 15, 300000),
        ("Marketing", 8, 200000),
        ("Operations", 12, 180000)
    ]
    
    utilization_records = []
    start_date = datetime.now() - timedelta(days=180)
    
    for dept_name, headcount, budget in departments:
        current_date = start_date
        
        while current_date <= datetime.now():
            # Skip weekends
            if current_date.weekday() < 5:
                available_hours = headcount * 8  # 8 hours per person per day
                
                # Different utilization patterns per department
                if dept_name == "Engineering":
                    # High utilization, trending up (hiring signal)
                    base_utilization = 0.85
                    days_from_start = (current_date - start_date).days
                    trend_factor = min(0.95, base_utilization + (days_from_start / 180) * 0.1)
                    utilization = random.uniform(trend_factor - 0.1, trend_factor + 0.05)
                
                elif dept_name == "Sales":
                    # Moderate utilization with seasonal variations
                    base_utilization = 0.65
                    seasonal_factor = 1.2 if current_date.month in [11, 12, 3] else 1.0  # End of quarters
                    utilization = random.uniform(0.5, 0.8) * seasonal_factor
                    utilization = min(0.95, utilization)
                
                else:
                    # Normal utilization
                    utilization = random.uniform(0.6, 0.85)
                
                utilized_hours = int(available_hours * utilization)
                efficiency = random.uniform(0.8, 0.95)
                
                utilization_records.append((
                    dept_name, current_date.date(), available_hours, 
                    utilized_hours, efficiency
                ))
            
            current_date += timedelta(days=1)
    
    return departments, utilization_records

def generate_sales_data():
    """Generate sales order data"""
    customers = ["ABC Corp", "XYZ Ltd", "Tech Solutions Inc", "Global Systems", "Enterprise Co"]
    sales_reps = ["Alice Johnson", "Bob Smith", "Carol Davis", "David Wilson", "Eva Brown"]
    
    orders = []
    start_date = datetime.now() - timedelta(days=180)
    current_date = start_date
    
    while current_date <= datetime.now():
        # Skip weekends
        if current_date.weekday() < 5:
            # Different probability of orders based on day and season
            order_probability = 0.6
            
            # Quarter-end rush
            if current_date.month in [3, 6, 9, 12] and current_date.day > 25:
                order_probability = 0.8
            
            # Generate 0-5 orders per day
            if random.random() < order_probability:
                num_orders = random.randint(1, 5)
                for _ in range(num_orders):
                    order_amount = random.uniform(1000, 50000)
                    orders.append((
                        current_date.date(),
                        random.choice(customers),
                        order_amount,
                        "Completed",
                        random.choice(sales_reps)
                    ))
        
        current_date += timedelta(days=1)
    
    return orders

def insert_sample_data():
    """Insert all generated sample data into database"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        print("Generating and inserting sample data...")
        
        # Clear existing data
        cur.execute("TRUNCATE TABLE inventory_transactions, inventory_items, expense_records, budget_categories, employee_utilization, departments, sales_orders RESTART IDENTITY CASCADE")
        
        # Insert inventory data
        print("Inserting inventory data...")
        products, transactions = generate_inventory_data()
        for sku, name, category, unit_cost in products:
            cur.execute("""
                INSERT INTO inventory_items (sku, name, category, unit_cost, current_stock, reorder_point)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (sku, name, category, unit_cost, random.randint(50, 200), 30))
        
        for sku, date, trans_type, quantity, unit_price, total in transactions:
            cur.execute("""
                INSERT INTO inventory_transactions (sku, transaction_date, transaction_type, quantity, unit_price, total_amount)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (sku, date, trans_type, quantity, unit_price, total))
        
        # Insert budget data
        print("Inserting budget data...")
        categories, expenses = generate_budget_data()
        category_ids = {}
        for cat_name, department, annual_budget in categories:
            cur.execute("""
                INSERT INTO budget_categories (category_name, department, annual_budget)
                VALUES (%s, %s, %s) RETURNING id
            """, (cat_name, department, annual_budget))
            category_ids[cat_name] = cur.fetchone()[0]
        
        for cat_name, date, amount, description, approved_by in expenses:
            cur.execute("""
                INSERT INTO expense_records (category_id, expense_date, amount, description, approved_by)
                VALUES (%s, %s, %s, %s, %s)
            """, (category_ids[cat_name], date, amount, description, approved_by))
        
        # Insert HR data
        print("Inserting HR data...")
        departments, utilization_records = generate_hr_data()
        dept_ids = {}
        for dept_name, headcount, budget in departments:
            cur.execute("""
                INSERT INTO departments (name, head_count, budget_allocated)
                VALUES (%s, %s, %s) RETURNING id
            """, (dept_name, headcount, budget))
            dept_ids[dept_name] = cur.fetchone()[0]
        
        for dept_name, date, available_hours, utilized_hours, efficiency in utilization_records:
            cur.execute("""
                INSERT INTO employee_utilization (department_id, record_date, available_hours, utilized_hours, efficiency_rate)
                VALUES (%s, %s, %s, %s, %s)
            """, (dept_ids[dept_name], date, available_hours, utilized_hours, efficiency))
        
        # Insert sales data
        print("Inserting sales data...")
        orders = generate_sales_data()
        for order_date, customer, amount, status, sales_rep in orders:
            cur.execute("""
                INSERT INTO sales_orders (order_date, customer_name, total_amount, status, sales_rep)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_date, customer, amount, status, sales_rep))
        
        conn.commit()
        conn.close()
        print("Sample data generated successfully!")
        print(f"- {len(products)} inventory items with {len(transactions)} transactions")
        print(f"- {len(categories)} budget categories with {len(expenses)} expense records")
        print(f"- {len(departments)} departments with {len(utilization_records)} utilization records")
        print(f"- {len(orders)} sales orders")
        
    except Exception as e:
        print(f"Error inserting sample data: {e}")
        raise

if __name__ == "__main__":
    insert_sample_data()