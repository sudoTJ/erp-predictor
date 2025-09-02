# Low Level Design: ERP Prediction Service Implementation

## Project Structure
```
erp-prediction-system/
├── docker-compose.yml
├── README.md
├── requirements.txt
├── .env
├── erp-service/
│   ├── app.py
│   ├── models/
│   ├── data/
│   └── requirements.txt
├── prediction-service/
│   ├── app.py
│   ├── ml_models/
│   ├── utils/
│   └── requirements.txt
└── frontend/
    ├── app.py (Streamlit)
    └── requirements.txt
```

## Database Schema

### PostgreSQL Tables

```sql
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
```

## API Specifications

### Mock ERP Service (Port 3001)

#### Base URL: `http://localhost:3001/api/v1`

```python
# Inventory Endpoints
GET /inventory/items
Response: {
    "items": [
        {
            "sku": "SKU001",
            "name": "Product A",
            "current_stock": 150,
            "category": "Electronics"
        }
    ]
}

GET /inventory/{sku}/history?days=90
Response: {
    "sku": "SKU001",
    "history": [
        {
            "date": "2024-01-01",
            "quantity_sold": 10,
            "stock_level": 140
        }
    ]
}

# Budget Endpoints  
GET /finance/expenses?category=marketing&days=90
Response: {
    "category": "marketing",
    "total_budget": 50000,
    "spent_to_date": 32000,
    "expenses": [
        {
            "date": "2024-01-15",
            "amount": 1500,
            "description": "Google Ads"
        }
    ]
}

# HR Endpoints
GET /hr/utilization?department=engineering&days=90
Response: {
    "department": "engineering",
    "current_headcount": 25,
    "utilization_data": [
        {
            "date": "2024-01-01",
            "available_hours": 200,
            "utilized_hours": 180
        }
    ]
}

# Sales Endpoints
GET /sales/orders?days=90
Response: {
    "orders": [
        {
            "date": "2024-01-01",
            "total_amount": 15000,
            "customer": "ABC Corp"
        }
    ]
}
```

### Prediction Service (Port 3002)

#### Base URL: `http://localhost:3002/api/v1`

```python
# Universal Prediction Endpoint
POST /predict
Request: {
    "prediction_type": "inventory",  # inventory, budget, resource, sales
    "entity_id": "SKU001",          # SKU, category, department, etc.
    "time_horizon": 30,             # days to predict
    "context": {                    # additional context
        "seasonal_factor": 1.2,
        "market_condition": "stable"
    }
}

Response: {
    "prediction_type": "inventory",
    "entity_id": "SKU001",
    "time_horizon": 30,
    "predictions": [
        {
            "date": "2024-02-01",
            "predicted_value": 120,
            "confidence": 0.85
        }
    ],
    "insights": [
        "Expected 15% increase in demand",
        "Recommend reordering in 10 days"
    ],
    "metadata": {
        "model_used": "linear_regression",
        "accuracy_score": 0.87,
        "last_updated": "2024-01-15T10:30:00Z"
    }
}

# Health Check
GET /health
Response: {
    "status": "healthy",
    "version": "1.0.0",
    "uptime": "2h 30m"
}
```

## Implementation Details

### Mock ERP Service (`erp-service/app.py`)

```python
from flask import Flask, jsonify, request
import psycopg2
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Database connection
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'erp_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'password')
    )

@app.route('/api/v1/inventory/items')
def get_inventory_items():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT sku, name, current_stock, category, unit_cost 
        FROM inventory_items 
        ORDER BY sku
    """)
    items = cur.fetchall()
    
    result = {
        "items": [
            {
                "sku": item[0],
                "name": item[1], 
                "current_stock": item[2],
                "category": item[3],
                "unit_cost": float(item[4])
            } for item in items
        ]
    }
    
    conn.close()
    return jsonify(result)

@app.route('/api/v1/inventory/<sku>/history')
def get_inventory_history(sku):
    days = request.args.get('days', 90, type=int)
    start_date = datetime.now() - timedelta(days=days)
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT transaction_date, quantity, unit_price
        FROM inventory_transactions 
        WHERE sku = %s AND transaction_date >= %s
        ORDER BY transaction_date
    """, (sku, start_date))
    
    history = cur.fetchall()
    
    result = {
        "sku": sku,
        "history": [
            {
                "date": item[0].isoformat(),
                "quantity": item[1],
                "unit_price": float(item[2])
            } for item in history
        ]
    }
    
    conn.close()
    return jsonify(result)

# Additional endpoints for budget, hr, sales...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001, debug=True)
```

### Prediction Service (`prediction-service/app.py`)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

app = FastAPI(title="ERP Prediction Service", version="1.0.0")

# Pydantic Models
class PredictionRequest(BaseModel):
    prediction_type: str
    entity_id: str
    time_horizon: int = 30
    context: Optional[Dict[str, Any]] = {}

class PredictionPoint(BaseModel):
    date: str
    predicted_value: float
    confidence: float

class PredictionResponse(BaseModel):
    prediction_type: str
    entity_id: str
    time_horizon: int
    predictions: List[PredictionPoint]
    insights: List[str]
    metadata: Dict[str, Any]

# Configuration
ERP_SERVICE_URL = "http://localhost:3001/api/v1"

class UniversalPredictor:
    def __init__(self):
        self.model = LinearRegression()
        
    async def fetch_historical_data(self, prediction_type: str, entity_id: str):
        """Fetch relevant historical data from ERP service"""
        async with httpx.AsyncClient() as client:
            if prediction_type == "inventory":
                response = await client.get(f"{ERP_SERVICE_URL}/inventory/{entity_id}/history?days=180")
            elif prediction_type == "budget":
                response = await client.get(f"{ERP_SERVICE_URL}/finance/expenses?category={entity_id}&days=180")
            elif prediction_type == "resource":
                response = await client.get(f"{ERP_SERVICE_URL}/hr/utilization?department={entity_id}&days=180")
            elif prediction_type == "sales":
                response = await client.get(f"{ERP_SERVICE_URL}/sales/orders?days=180")
            else:
                raise HTTPException(status_code=400, detail="Unknown prediction type")
                
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch ERP data")
                
            return response.json()
    
    def prepare_features(self, data: Dict, prediction_type: str) -> pd.DataFrame:
        """Convert ERP data to ML features"""
        if prediction_type == "inventory":
            history = data.get("history", [])
            df = pd.DataFrame(history)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Create time-based features
            df['day_of_year'] = df['date'].dt.dayofyear
            df['month'] = df['date'].dt.month
            df['week_of_year'] = df['date'].dt.isocalendar().week
            
            # Create lag features
            df['quantity_lag_1'] = df['quantity'].shift(1)
            df['quantity_lag_7'] = df['quantity'].shift(7)
            
            # Rolling averages
            df['quantity_ma_7'] = df['quantity'].rolling(window=7).mean()
            df['quantity_ma_30'] = df['quantity'].rolling(window=30).mean()
            
            return df.dropna()
            
        elif prediction_type == "budget":
            expenses = data.get("expenses", [])
            df = pd.DataFrame(expenses)
            df['date'] = pd.to_datetime(df['date'])
            
            # Group by date and sum amounts
            daily_expenses = df.groupby('date')['amount'].sum().reset_index()
            daily_expenses = daily_expenses.sort_values('date')
            
            # Create time features
            daily_expenses['day_of_month'] = daily_expenses['date'].dt.day
            daily_expenses['month'] = daily_expenses['date'].dt.month
            daily_expenses['quarter'] = daily_expenses['date'].dt.quarter
            
            return daily_expenses
            
        # Add similar logic for resource and sales prediction types
        return pd.DataFrame()
    
    def train_and_predict(self, df: pd.DataFrame, prediction_type: str, time_horizon: int) -> List[PredictionPoint]:
        """Train model and generate predictions"""
        if len(df) < 10:
            # Fallback to simple trend calculation
            return self._simple_trend_prediction(df, prediction_type, time_horizon)
        
        # Prepare features and target
        feature_cols = [col for col in df.columns if col not in ['date', 'quantity', 'amount']]
        X = df[feature_cols].fillna(0)
        
        if prediction_type == "inventory":
            y = df['quantity']
        elif prediction_type == "budget":
            y = df['amount']
        else:
            y = df.iloc[:, -1]  # Last column as target
        
        # Train model
        self.model.fit(X, y)
        
        # Generate future predictions
        predictions = []
        last_date = pd.to_datetime(df['date'].max())
        
        for i in range(1, time_horizon + 1):
            future_date = last_date + timedelta(days=i)
            
            # Create features for future date
            future_features = self._create_future_features(future_date, df, feature_cols)
            
            # Predict
            pred_value = self.model.predict([future_features])[0]
            confidence = max(0.5, min(0.95, 0.8 - (i * 0.01)))  # Decreasing confidence
            
            predictions.append(PredictionPoint(
                date=future_date.isoformat(),
                predicted_value=round(float(pred_value), 2),
                confidence=round(confidence, 2)
            ))
        
        return predictions
    
    def _create_future_features(self, future_date: datetime, df: pd.DataFrame, feature_cols: List[str]) -> List[float]:
        """Create features for future date prediction"""
        features = []
        
        # Time-based features
        if 'day_of_year' in feature_cols:
            features.append(future_date.timetuple().tm_yday)
        if 'month' in feature_cols:
            features.append(future_date.month)
        if 'week_of_year' in feature_cols:
            features.append(future_date.isocalendar()[1])
        
        # Lag and moving average features (use last known values)
        for col in feature_cols:
            if col.startswith(('quantity_lag', 'quantity_ma', 'amount_lag', 'amount_ma')):
                features.append(df[col].iloc[-1] if not df[col].empty else 0)
            elif col not in ['day_of_year', 'month', 'week_of_year']:
                features.append(df[col].mean() if not df[col].empty else 0)
        
        return features
    
    def _simple_trend_prediction(self, df: pd.DataFrame, prediction_type: str, time_horizon: int) -> List[PredictionPoint]:
        """Fallback prediction using simple trend analysis"""
        if prediction_type == "inventory":
            values = df['quantity'].values
        elif prediction_type == "budget":
            values = df['amount'].values
        else:
            values = df.iloc[:, -1].values
        
        # Simple linear trend
        if len(values) > 1:
            trend = (values[-1] - values[0]) / len(values)
        else:
            trend = 0
        
        predictions = []
        last_date = pd.to_datetime(df['date'].max()) if 'date' in df.columns else datetime.now()
        last_value = values[-1] if len(values) > 0 else 100
        
        for i in range(1, time_horizon + 1):
            future_date = last_date + timedelta(days=i)
            pred_value = last_value + (trend * i)
            
            predictions.append(PredictionPoint(
                date=future_date.isoformat(),
                predicted_value=round(float(max(0, pred_value)), 2),
                confidence=0.6
            ))
        
        return predictions
    
    def generate_insights(self, predictions: List[PredictionPoint], prediction_type: str) -> List[str]:
        """Generate business insights from predictions"""
        insights = []
        
        if not predictions:
            return ["Insufficient data for insights"]
        
        # Calculate trend
        first_pred = predictions[0].predicted_value
        last_pred = predictions[-1].predicted_value
        trend_pct = ((last_pred - first_pred) / first_pred * 100) if first_pred != 0 else 0
        
        if prediction_type == "inventory":
            if trend_pct > 10:
                insights.append(f"Expected {trend_pct:.1f}% increase in demand over forecast period")
                insights.append("Consider increasing inventory levels")
            elif trend_pct < -10:
                insights.append(f"Expected {abs(trend_pct):.1f}% decrease in demand")
                insights.append("Consider reducing inventory to avoid overstocking")
            else:
                insights.append("Demand expected to remain stable")
        
        elif prediction_type == "budget":
            if trend_pct > 15:
                insights.append(f"Budget spending trending {trend_pct:.1f}% higher")
                insights.append("Review spending controls and budget allocation")
            elif trend_pct < -15:
                insights.append(f"Budget spending trending {abs(trend_pct):.1f}% lower")
                insights.append("Potential for budget reallocation")
        
        # Add confidence-based insights
        avg_confidence = sum(p.confidence for p in predictions) / len(predictions)
        if avg_confidence < 0.7:
            insights.append("Prediction confidence is moderate - consider additional data collection")
        
        return insights

# Global predictor instance
predictor = UniversalPredictor()

@app.post("/api/v1/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    try:
        # Fetch historical data
        historical_data = await predictor.fetch_historical_data(
            request.prediction_type, 
            request.entity_id
        )
        
        # Prepare features
        df = predictor.prepare_features(historical_data, request.prediction_type)
        
        # Generate predictions
        predictions = predictor.train_and_predict(df, request.prediction_type, request.time_horizon)
        
        # Generate insights
        insights = predictor.generate_insights(predictions, request.prediction_type)
        
        return PredictionResponse(
            prediction_type=request.prediction_type,
            entity_id=request.entity_id,
            time_horizon=request.time_horizon,
            predictions=predictions,
            insights=insights,
            metadata={
                "model_used": "linear_regression",
                "data_points": len(df),
                "last_updated": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3002)
```

## Sample Data Generation Script

```python
# erp-service/data/generate_sample_data.py
import psycopg2
import random
from datetime import datetime, timedelta
import json

def generate_inventory_data():
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
            # Generate sales (daily)
            if random.random() > 0.3:  # 70% chance of sales
                daily_sales = random.randint(1, 15)
                transactions.append((
                    sku, current_date.date(), 'sale', 
                    -daily_sales, unit_cost * 1.2, 
                    -daily_sales * unit_cost * 1.2
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
        
        while current_date <= datetime.now():
            # Generate 3-8 expenses per month
            if current_date.day <= 28:
                num_expenses = random.randint(3, 8)
                for _ in range(num_expenses):
                    expense_date = current_date + timedelta(days=random.randint(0, 27))
                    if expense_date <= datetime.now():
                        amount = random.uniform(monthly_budget * 0.05, monthly_budget * 0.25)
                        expenses.append((
                            cat_name, expense_date.date(), amount,
                            f"Monthly {cat_name.lower()} expense", 
                            "System Generated"
                        ))
            
            current_date += timedelta(days=30)
    
    return categories, expenses

# Database insertion functions
def insert_sample_data():
    conn = psycopg2.connect(
        host='localhost',
        database='erp_db', 
        user='postgres',
        password='password'
    )
    cur = conn.cursor()
    
    # Insert inventory data
    products, transactions = generate_inventory_data()
    for sku, name, category, unit_cost in products:
        cur.execute("""
            INSERT INTO inventory_items (sku, name, category, unit_cost, current_stock, reorder_point)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (sku) DO NOTHING
        """, (sku, name, category, unit_cost, random.randint(50, 200), 30))
    
    for sku, date, trans_type, quantity, unit_price, total in transactions:
        cur.execute("""
            INSERT INTO inventory_transactions (sku, transaction_date, transaction_type, quantity, unit_price, total_amount)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (sku, date, trans_type, quantity, unit_price, total))
    
    # Insert budget data  
    categories, expenses = generate_budget_data()
    for cat_name, department, annual_budget in categories:
        cur.execute("""
            INSERT INTO budget_categories (category_name, department, annual_budget)
            VALUES (%s, %s, %s)
            ON CONFLICT (category_name) DO NOTHING
        """, (cat_name, department, annual_budget))
    
    conn.commit()
    conn.close()
    print("Sample data generated successfully!")

if __name__ == "__main__":
    insert_sample_data()
```

## Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: erp_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./erp-service/sql/:/docker-entrypoint-initdb.d/

  erp-service:
    build: ./erp-service
    ports:
      - "3001:3001"
    depends_on:
      - postgres
    environment:
      DB_HOST: postgres
      DB_NAME: erp_db
      DB_USER: postgres
      DB_PASSWORD: password

  prediction-service:
    build: ./prediction-service
    ports:
      - "3002:3002"
    environment:
      ERP_SERVICE_URL: http://erp-service:3001/api/v1

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      PREDICTION_API_URL: http://prediction-service:3002/api/v1

volumes:
  postgres_data:
```

## Testing Strategy

### Unit Tests
```python
# prediction-service/tests/test_predictor.py
import pytest
from app import UniversalPredictor

def test_simple_trend_prediction():
    predictor = UniversalPredictor()
    # Test with sample data
    # Assert predictions are reasonable
    pass

def test_inventory_prediction():
    # Test inventory-specific logic
    pass

def test_budget_prediction():
    # Test budget-specific logic
    pass
```

### Integration Tests
```bash
# Test ERP service endpoints
curl http://localhost:3001/api/v1/inventory/items

# Test prediction service
curl -X POST http://localhost:3002/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"prediction_type": "inventory", "entity_id": "SKU001", "time_horizon": 30}'
```

## Deployment Commands

```bash
# Setup and run
git clone <repository>
cd erp-prediction-system
docker-compose up --build

# Generate sample data
docker-compose exec erp-service python data/generate_sample_data.py

# Test endpoints
curl http://localhost:3001/api/v1/inventory/items
curl -X POST http://localhost:3002/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"prediction_type": "inventory", "entity_id": "SKU001", "time_horizon": 30}'
```

## Performance Requirements
- **API Response Time**: < 2 seconds
- **Data Processing**: Handle 1000+ historical records
- **Concurrent Requests**: Support 10+ simultaneous predictions
- **Memory Usage**: < 512MB per service

This LLD provides complete implementation details for a developer to build the system end-to-end within hackathon timeframes.