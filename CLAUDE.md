# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Claude Context: ERP Prediction Microservice

## Project Mission
Build a **plug-and-play prediction microservice** for ERP systems that demonstrates AI-powered business intelligence in 2-3 days. Focus: **working demo over perfect code**.

## Reference Documents
- **HLD (High Level Design)**: System architecture, technology decisions, timeline
- **LLD (Low Level Design)**: Implementation details, code templates, database schemas

## What We're Building

### Core Value Proposition
```
ERP Data → AI Predictions → Business Insights
```

**One sentence goal**: Create a service that takes any ERP data and returns smart predictions that save businesses money.

### Success Metrics
- ✅ **Demo works end-to-end** - Priority #1
- ✅ **Sub-2 second API responses** - Fast enough to impress
- ✅ **3+ prediction types working** - Inventory, budget, resources
- ✅ **Realistic sample data** - Looks like real business

## 80-20 Rule Implementation

### Focus 80% Effort On (Must-Have):
1. **Core API working** - Prediction service responds correctly
2. **Sample data realistic** - 6 months of believable ERP data  
3. **One prediction type perfect** - Inventory forecasting works flawlessly
4. **Docker setup works** - One command deployment
5. **Basic error handling** - Service doesn't crash during demo

### Spend 20% Effort On (Nice-to-Have):
1. **Perfect ML accuracy** - Simple models are fine if they work
2. **Complex UI** - Basic dashboard or even just API responses
3. **Extensive testing** - Manual testing during development
4. **Production features** - Authentication, logging, monitoring
5. **Code optimization** - Working code first, clean code second

## Development Philosophy

### Pragmatic Over Perfect
```python
# GOOD - Works reliably
def predict_inventory(data):
    if len(data) < 5:
        return simple_trend(data)
    return ml_prediction(data)

# AVOID - Over-engineered for hackathon
class AbstractPredictionFactory:
    def create_predictor(self):
        # Complex factory pattern...
```

### Working Over Elegant
- **Hardcode constants** instead of complex config systems
- **Copy-paste similar functions** instead of perfect abstractions  
- **Use simple if-else** instead of complex design patterns
- **Inline SQL queries** instead of ORM complexity
- **Direct API calls** instead of service layer abstractions

### Fast Development Priorities
1. **Get something running first** - Even if it's ugly
2. **Add features incrementally** - One prediction type at a time
3. **Test as you go** - Manual testing, not unit tests initially
4. **Refactor only if broken** - Don't optimize working code during hackathon

## Clean Code Guidelines (Hackathon Edition)

### Code Structure - Keep It Simple
```python
# File organization
app.py              # All main logic here (200-300 lines OK)
utils.py            # Helper functions only
data_generator.py   # Sample data creation
requirements.txt    # Dependencies

# Avoid creating
models/predictor.py        # Don't split too early
services/data_service.py   # Keep logic together
config/settings.py         # Use environment variables
```

### Naming Convention - Clear Over Clever
```python
# GOOD - Immediately clear
def get_inventory_history(sku, days):
    pass

def predict_demand_next_30_days(historical_data):
    pass

# AVOID - Requires thinking
def fetch_temporal_entity_data(identifier, period):
    pass

def execute_forecasting_algorithm(dataset):
    pass
```

### Function Design - Small and Focused
```python
# GOOD - Single responsibility
def fetch_erp_data(entity_id):
    """Get data from ERP service"""
    return requests.get(f"{ERP_URL}/{entity_id}").json()

def prepare_ml_features(raw_data):
    """Convert ERP data to ML format"""
    return pd.DataFrame(raw_data).fillna(0)

def generate_predictions(features, days):
    """Run ML model and return predictions"""
    return model.predict(features)

# AVOID - Doing too much
def predict_everything(entity_id, days):
    # Fetching data, processing, ML, formatting - too much
    pass
```

### Error Handling - Fail Gracefully
```python
# GOOD - Simple fallbacks
def predict_with_fallback(data):
    try:
        return ml_model.predict(data)
    except Exception as e:
        print(f"ML failed: {e}, using simple trend")
        return simple_trend_prediction(data)

# AVOID - Complex error hierarchy during hackathon
class PredictionError(Exception):
    class MLModelError(Exception):
        class FeaturePreparationError(Exception):
            # Too complex for 3-day project
```

## Implementation Strategy

### Day 1: Foundation (Must Work)
```bash
# End of day 1 checklist:
✅ docker-compose up works
✅ PostgreSQL has sample data
✅ ERP service returns JSON
✅ Basic prediction endpoint responds
✅ One inventory prediction works end-to-end
```

### Day 2: Features (Add Value)
```bash
# End of day 2 checklist:
✅ 3+ prediction types working
✅ Insights generation works
✅ API documentation ready
✅ Error handling prevents crashes
✅ Performance meets <2sec requirement
```

### Day 3: Polish (Demo Ready)
```bash
# End of day 3 checklist:
✅ Demo scenarios prepared
✅ Sample data looks realistic
✅ Basic UI or good API docs
✅ System stable under demo conditions
✅ Clear business value demonstrated
```

## Code Quality Standards (Minimal Viable)

### Required Quality Measures
```python
# 1. Basic validation
def predict(request):
    if not request.entity_id:
        return {"error": "Missing entity_id"}
    
# 2. Simple logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Processing prediction for {entity_id}")

# 3. Basic documentation
def fetch_inventory_data(sku: str, days: int = 90) -> dict:
    """
    Get inventory history for a product
    Args: sku - product code, days - history period
    Returns: dict with sales history
    """
```

### Skip During Hackathon
- ❌ Comprehensive unit tests
- ❌ Complex logging frameworks  
- ❌ Detailed API documentation
- ❌ Performance profiling
- ❌ Security implementations
- ❌ Database migrations
- ❌ Configuration management systems

## Technical Constraints & Shortcuts

### Database - Keep It Simple
```sql
-- GOOD - Simple schema
CREATE TABLE inventory_history (
    sku TEXT,
    date DATE, 
    quantity INTEGER,
    amount DECIMAL
);

-- AVOID - Over-normalized during hackathon
CREATE TABLE products (...);
CREATE TABLE categories (...);
CREATE TABLE suppliers (...);
-- Complex joins slow down development
```

### ML Models - Start Simple
```python
# GOOD - Works reliably
from sklearn.linear_model import LinearRegression
model = LinearRegression()

# AVOID - Complex models that might fail
from tensorflow import keras
# Neural networks can be unpredictable in hackathon timeline
```

### API Design - Consistent and Simple  
```python
# GOOD - One pattern for everything
@app.post("/predict")
def predict(request: PredictionRequest):
    return {
        "predictions": [...],
        "insights": [...],
        "metadata": {...}
    }

# AVOID - Different patterns per endpoint
@app.post("/inventory/forecast")
@app.post("/budget/analyze")  
@app.post("/resources/plan")
# Consistency > custom endpoints
```

## Demo Preparation Strategy

### Prepare 3 Demo Scenarios
1. **Inventory Crisis**: "Product X will run out in 8 days without reorder"
2. **Budget Alert**: "Marketing will exceed budget by 15% this quarter"  
3. **Resource Gap**: "Engineering needs 3 more developers for Q2 projects"

### Demo Data Requirements
```python
# Inventory demo data
SKU001: 6 months declining stock, clear reorder pattern
SKU002: Seasonal product with holiday spike
SKU003: Stable product with steady consumption

# Budget demo data  
Marketing: Overspending trend, clear budget risk
Engineering: Under budget, reallocation opportunity

# Resource demo data
Engineering: 85% utilization, hiring trigger point
Sales: 60% utilization, potential downsizing
```

### Demo Script Template
```markdown
1. Show current state: "Here's our ERP data"
2. Make prediction: "AI predicts this will happen"
3. Show insight: "Business recommendation is..."
4. Quantify impact: "This saves $X or prevents Y loss"
```

## Critical Success Factors

### Technical Must-Haves
- **Service starts reliably** - No dependency issues
- **API responds consistently** - No random failures during demo
- **Predictions look reasonable** - Numbers make business sense
- **Performance acceptable** - Fast enough for live demo

### Business Must-Haves  
- **Clear value proposition** - Obvious why businesses need this
- **Realistic scenarios** - Problems real businesses face
- **Actionable insights** - Not just predictions, but recommendations
- **Quantified benefits** - Dollar savings or risk prevention

## Project Architecture Overview

This is a hackathon-style ERP prediction microservice with three main components:
1. **Mock ERP Service** (port 3001): Simulates ERP system with PostgreSQL backend
2. **Prediction Service** (port 3002): FastAPI service with universal ML predictor using scikit-learn
3. **Frontend Dashboard** (port 3000): Optional Streamlit/React interface

### Expected Project Structure
```
erp-prediction-system/
├── docker-compose.yml
├── erp-service/          # Flask app + PostgreSQL data
├── prediction-service/   # FastAPI + ML models  
└── frontend/            # Streamlit dashboard
```

## Common Development Commands

### Initial Setup
```bash
# Create and start all services
docker-compose up --build

# Generate sample ERP data (6 months)
docker-compose exec erp-service python data/generate_sample_data.py
```

### Development Workflow
```bash
# Test ERP service
curl http://localhost:3001/api/v1/inventory/items

# Test prediction endpoint
curl -X POST http://localhost:3002/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"prediction_type": "inventory", "entity_id": "SKU001", "time_horizon": 30}'

# Check service health
curl http://localhost:3002/api/v1/health
```

### Quick Testing
```bash
# Restart specific service
docker-compose restart prediction-service

# View service logs
docker-compose logs -f prediction-service

# Clean rebuild
docker-compose down && docker-compose up --build
```

## Final Reminders

### Hackathon Mindset
- **Working > Perfect**: Ship working code, not perfect code
- **Demo > Features**: Prioritize what judges will see  
- **Simple > Complex**: Choose the simplest solution that works
- **Fast > Scalable**: Optimize for 3-day delivery, not 3-year maintenance

### When You're Stuck
1. **Check if it's demo-critical** - If not, skip for now
2. **Look for simpler alternative** - Can you hardcode/fake it?
3. **Ask "minimum viable"** - What's the simplest version that works?
4. **Time-box problems** - Don't spend >2 hours on any single issue

### Success Definition
You succeed if:
- Demo works reliably during presentation
- Business value is clear and quantified  
- System shows intelligent predictions
- Judges understand the ERP integration value

**Remember: The goal is winning the hackathon, not building production software. Everything else is secondary.**