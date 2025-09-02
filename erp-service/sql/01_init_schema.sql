-- ERP Database Schema
-- Inventory Data
CREATE TABLE inventory_items (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    current_stock INTEGER DEFAULT 0,
    reorder_point INTEGER DEFAULT 0,
    unit_cost DECIMAL(10,2),
    supplier VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE inventory_transactions (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(50) REFERENCES inventory_items(sku),
    transaction_date DATE NOT NULL,
    transaction_type VARCHAR(20), -- 'sale', 'purchase', 'adjustment'
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2),
    total_amount DECIMAL(10,2)
);

-- Financial Data
CREATE TABLE budget_categories (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(100),
    annual_budget DECIMAL(12,2),
    current_spent DECIMAL(12,2) DEFAULT 0
);

CREATE TABLE expense_records (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES budget_categories(id),
    expense_date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    approved_by VARCHAR(100)
);

-- HR Data
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    head_count INTEGER DEFAULT 0,
    budget_allocated DECIMAL(12,2)
);

CREATE TABLE employee_utilization (
    id SERIAL PRIMARY KEY,
    department_id INTEGER REFERENCES departments(id),
    record_date DATE NOT NULL,
    available_hours INTEGER,
    utilized_hours INTEGER,
    efficiency_rate DECIMAL(5,2)
);

-- Sales Data
CREATE TABLE sales_orders (
    id SERIAL PRIMARY KEY,
    order_date DATE NOT NULL,
    customer_name VARCHAR(200),
    total_amount DECIMAL(12,2),
    status VARCHAR(50),
    sales_rep VARCHAR(100)
);