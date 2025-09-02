# 🚀 ERP Prediction Microservice

A modular, machine learning prediction microservice for ERP systems that demonstrates intelligent business forecasting with sub-2 second response times.

## ✨ Features

- **🤖 ML-Powered Predictions**: Linear regression models with confidence intervals and intelligent insights
- **📦 Multi-Domain Support**: Inventory, Budget, Resource, and Sales forecasting  
- **⚡ High Performance**: Sub-2 second API response times
- **🎯 Business Insights**: Actionable recommendations beyond raw predictions
- **📊 Interactive Dashboard**: Rich Streamlit frontend with charts and metrics
- **🏗️ Modular Architecture**: Clean separation of concerns across all services
- **🐳 Docker Support**: One-command deployment with Docker Compose
- **💻 Local Development**: Easy setup for development and testing

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │───▶│ Prediction API  │───▶│   ERP Service   │
│   Dashboard     │    │   (FastAPI)     │    │    (Flask)      │
│   Port 8000     │    │   Port 3003     │    │   Port 3001     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
       │                         │                       │
       ▼                         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │  ML Models      │    │   SQLite DB     │
│   Components    │    │  Scikit-learn   │    │  Sample Data    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Service Architecture

**🏪 ERP Service (Flask)**
- **Models**: Database connections and data models
- **Services**: Business logic layer 
- **Routes**: API endpoints with validation
- **Utils**: Helper functions and decorators

**🔮 Prediction Service (FastAPI)**
- **Models**: ML models and Pydantic schemas
- **Services**: ML pipeline orchestration
- **Routes**: Prediction endpoints
- **Utils**: Insights generation and utilities

**📊 Frontend Dashboard (Streamlit)**
- **Components**: Reusable UI components
- **Utils**: API clients and formatters
- **Config**: Environment configurations

## 🧠 How It Works (Simple Explanation)

### The Big Picture
Imagine you run a business and want to know:
- "Will I run out of laptops next month?"
- "Am I spending too much on marketing?" 
- "Do I need to hire more engineers?"

This system looks at your past business data and uses machine learning algorithms to predict what will happen in the future, just like a weather forecast but for your business!

### Step-by-Step Process

**1. 📊 Data Collection**
- The system reads your business history (past 6 months)
- Examples: How many laptops were sold each day, how much was spent on marketing, how busy your teams were
- This data comes from your ERP system (business software that tracks everything)

**2. 🤖 ML Analysis** 
- The machine learning model looks for patterns in your data
- "Every Monday we sell 5 laptops, every Friday we sell 12"
- "Marketing spends more in December, less in January"
- "Engineering team gets busier before product launches"

**3. 🔮 Making Predictions**
- Based on these patterns, the ML model predicts the future
- "Next Tuesday, you'll probably sell 7 laptops"
- "Your marketing budget will be 15% over by month-end"
- "You'll need 2 more developers by next quarter"

**4. 📈 Confidence Levels**
- The ML model also tells you how confident it is in each prediction
- 90% confidence = Very sure this will happen
- 50% confidence = Could go either way, monitor closely
- Predictions get less confident the further into the future they go

**5. 💡 AI-Powered Smart Recommendations**
- The system uses DGPT AI to generate contextual business advice:
- "Order 50 more laptops by Friday to avoid stockout"
- "Reduce marketing spend by $10K this month to stay on budget" 
- "Start interviewing developers now for Q2 hiring"
- Enhanced with real-time AI analysis for nuanced, actionable insights

### Real Example in Action

**You ask**: "Will SKU001 (Laptop) run out of stock?"

**The system**:
1. **Looks at history**: "You sold 150 laptops in the last 30 days, averaging 5 per day"
2. **Finds patterns**: "Sales spike on weekends, drop on holidays"
3. **Makes prediction**: "You'll sell 7 laptops tomorrow, 5 the day after..."
4. **Calculates stock**: "At this rate, you'll run out in 12 days"
5. **Gives advice**: "Reorder 100 units by Wednesday to be safe"
6. **Shows confidence**: "85% confident in this prediction"

### Why This Matters for Business

**Before this system:**
- ❌ "I think we might need more inventory... maybe?"
- ❌ Gut feelings and Excel spreadsheets
- ❌ Reactive: Problems discovered after they happen

**With this system:**
- ✅ "ML model predicts 87% chance of stockout in 8 days"
- ✅ Data-driven decisions with confidence levels
- ✅ Proactive: Prevent problems before they happen

**Business Impact:**
- 💰 Save money by avoiding overstocking
- 📉 Reduce waste from expired inventory
- 😊 Keep customers happy with products in stock
- ⏰ Make decisions faster with AI insights

### Technical Deep-Dive (For Developers)

**🔬 How the Machine Learning Prediction Actually Works:**

**1. Data Pipeline**
```
ERP Database → Feature Engineering → ML Model → Confidence Calculation → Business Insights
```

**2. Feature Engineering Process**
- **Time Series Features**: Rolling averages, trends, seasonality patterns
- **Statistical Features**: Mean, standard deviation, variance over different time windows
- **Business Context**: Category, cost, seasonal factors, business rules

**3. Machine Learning Model**
- **Algorithm**: Linear Regression (chosen for speed and interpretability)
- **Training Data**: 6 months of historical transactions (100+ data points per entity)
- **Feature Matrix**: 10+ engineered features per prediction
- **Model Selection**: Optimized for <2 second response times

**4. Prediction Generation**
- **Time Horizon**: 1-90 days into the future
- **Daily Predictions**: Each day gets individual prediction + confidence
- **Confidence Scoring**: Based on data quality, volatility, and prediction distance

**5. Insights Engine**
- **Rule-Based System**: Business logic for actionable recommendations
- **Threshold Detection**: Automatic alerts for stockouts, budget overruns, etc.
- **Context Awareness**: Different insights for different business domains

**6. API Response Structure**
```json
{
  "predictions": [{"date": "2025-09-03", "predicted_value": 7.0, "confidence": 0.8}],
  "insights": ["Demand expected to remain stable", "Reorder recommended"],
  "metadata": {"model_used": "linear_regression", "data_points": 113}
}
```

**Performance Characteristics:**
- **Response Time**: <2 seconds for 90-day predictions
- **Memory Usage**: <512MB per service
- **Accuracy**: 70-85% for 30-day predictions (varies by domain)
- **Scalability**: Handles 10+ concurrent prediction requests

## 🤖 **DGPT AI Integration**

### **Enhanced Business Insights with AI**

The system now features **DGPT AI integration** for generating sophisticated, contextual business insights that go far beyond static rule-based recommendations.

**🎯 How It Works:**
1. **ML Predictions Generated** - Linear regression creates numerical forecasts
2. **AI Analysis** - DGPT analyzes predictions with business context 
3. **Smart Insights** - AI generates actionable, domain-specific recommendations
4. **Fallback Protection** - Static insights used if AI unavailable

**💡 AI-Powered vs Static Insights:**

| **Static (Old)** | **AI-Powered (New)** |
|------------------|----------------------|
| "Demand expected to remain stable" | "Based on seasonal patterns and current inventory turnover, maintain current stock levels but prepare for 15% demand increase in Q2 due to product lifecycle trends" |
| "Budget spending on track" | "Marketing spend is tracking 8% below budget with strong ROI on digital channels - consider reallocating $15K from traditional to digital marketing for optimal performance" |
| "Resource utilization stable" | "Engineering team operating at 78% capacity with upcoming project deadlines - recommend hiring 2 senior developers by month-end to maintain delivery commitments and prevent burnout" |

### **🔧 DGPT Configuration**

**Environment Variables:**
```bash
# Required for DGPT integration
DELA_API_KEY=your_api_key_here
DGPT_CUSTOMER_ID=your_customer_id  
DGPT_USER_ID=your_user_id

# Optional configuration
DGPT_ENABLED=true  # Set to false to disable AI insights
DGPT_REQUEST_TIMEOUT=30.0  # API timeout in seconds
```

**Setup Steps:**
1. Copy `.env.dgpt.example` to `.env`
2. Configure your DGPT API credentials
3. Set `DGPT_ENABLED=true` to activate AI insights
4. System automatically falls back to static insights if AI fails

**🛡️ Fallback Strategy:**
- **Primary:** DGPT AI-generated insights (contextual, sophisticated)
- **Fallback:** Static rule-based insights (reliable, fast)
- **Graceful degradation:** No system failures if AI unavailable

## 🚀 Quick Start Guide

### 📋 **Prerequisites**
- **Python 3.9+** installed on your system
- **Git** (optional, for cloning)
- **Web Browser** (Chrome, Firefox, Safari, etc.)

### 🛠️ **Complete Setup Instructions**

#### **Step 1: Get the Code**
```bash
# Option A: If you have git
git clone <repository-url>
cd ai-predictor

# Option B: Download and extract ZIP file to ai-predictor folder
```

#### **Step 2: Install Dependencies**
```bash
# Install all required packages
pip install flask fastapi uvicorn streamlit pandas scikit-learn plotly httpx requests pydantic
```

#### **Step 3: Create Sample Database**
```bash
# Generate 6 months of sample business data
python create_db.py
```
**Expected Output:**
```
Creating tables...
Inserting sample data...
Database created successfully: erp_demo.db
Tables and sample data ready!
```

#### **Step 4: Start All Services**

**🏪 Terminal 1 - ERP Service:**
```bash
cd erp-service
python app.py
```
**Expected Output:**
```
Starting ERP Service on http://localhost:3001
Health Check: http://localhost:3001/health
* Running on http://localhost:3001
```

**🔮 Terminal 2 - Prediction Service:**
```bash
cd prediction-service
python app.py
```
**Expected Output:**
```
Prediction Service starting up...
API Documentation available at: http://0.0.0.0:3003/docs
Uvicorn running on http://0.0.0.0:3003
```

**📊 Terminal 3 - Frontend Dashboard:**
```bash
cd frontend
streamlit run app.py
```
**When Streamlit asks for email:** Just press **Enter** (leave blank)

**Expected Output:**
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
Network URL: http://192.168.1.100:8501
```
**Note:** Streamlit typically runs on port 8501, but may use 8000 or other ports if 8501 is busy.

#### **Step 5: Access the Dashboard**
1. **Open your browser** to: **http://localhost:8501** (or the URL shown in Terminal 3)
2. **You should see**: ERP Prediction Dashboard with sidebar controls
3. **Test the system**: Try the demo scenarios below!

### 🎯 **Quick Test Scenarios**

Once the dashboard is running, try these:

**📦 Inventory Prediction:**
1. Select **"Inventory"** from prediction type
2. Choose **"SKU001"** (Laptop Dell Inspiron)
3. Set time horizon to **30 days**
4. Click **"Generate Prediction"**
5. **Expected**: Chart showing declining inventory with reorder recommendation

**💰 Budget Analysis:**
1. Select **"Budget"** from prediction type
2. Choose **"Marketing"** department
3. Set time horizon to **60 days**
4. Click **"Generate Prediction"**
5. **Expected**: Spending trend analysis with budget alerts

**👥 Resource Planning:**
1. Select **"Resource"** from prediction type
2. Choose **"Engineering"** team
3. Set time horizon to **45 days**
4. Click **"Generate Prediction"**
5. **Expected**: Team utilization forecast with hiring insights

### 🔧 **Troubleshooting**

**🚨 Common Issues:**

**"Port already in use" Error:**
```bash
# Find what's using the port
netstat -ano | findstr :3001
# Kill the process or restart your terminal
```

**"Module not found" Error:**
```bash
# Install missing dependency
pip install <missing-module-name>
```

**"Database not found" Error:**
```bash
# Recreate the database
python create_db.py
```

**Frontend not loading:**
- Check all 3 services are running in separate terminals
- Ensure ports 8501 (or 8000), 3001, 3003 are available
- Try refreshing browser or opening in incognito mode

**Services running but no data:**
- Verify database was created successfully
- Check service logs for errors
- Test API endpoints manually:
  - http://localhost:3001/health
  - http://localhost:3003/health

### 📊 **System Status Check**

**Verify everything is working:**
```bash
# Test ERP Service
curl http://localhost:3001/health

# Test Prediction Service  
curl http://localhost:3003/health

# Test prediction endpoint
curl -X POST http://localhost:3003/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"prediction_type": "inventory", "entity_id": "SKU001", "time_horizon": 30}'
```

**All working?** ✅ Your system is ready for demo!

## 🖥️ **Complete UI Guide - Dashboard Walkthrough**

### 📱 **Dashboard Layout Overview**

When you open **http://localhost:8501** (or 8000), you'll see:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  🏢 ERP Prediction Dashboard                                     [Settings] [❓] │
├─────────────────┬───────────────────────────────────────────────────────────────┤
│     SIDEBAR     │                    MAIN CONTENT AREA                          │
│                 │                                                               │
│ 🎯 Controls     │  📊 Charts & Visualizations                                  │
│ 📋 Options      │  📈 Prediction Results                                       │
│ ⚙️ Settings      │  💡 Business Insights                                        │
│ 🔄 Actions      │  📋 Data Tables                                              │
│                 │                                                               │
└─────────────────┴───────────────────────────────────────────────────────────────┘
```

### 🎯 **Left Sidebar - Control Panel**

**🔧 Main Controls (Always Visible):**

1. **📊 Prediction Type Selector**
   - **Purpose**: Choose what you want to predict
   - **Options**: 
     - 📦 **Inventory** - Product stock levels and demand
     - 💰 **Budget** - Department spending and financial trends  
     - 👥 **Resource** - Team utilization and workforce planning
     - 📈 **Sales** - Revenue forecasting and performance metrics
   - **What it does**: Changes the entire dashboard to focus on that business area

2. **🎯 Entity Selector** (Changes based on prediction type)
   - **For Inventory**: Dropdown with products
     - SKU001 (Laptop Dell Inspiron)
     - SKU002 (Office Chair Premium)
     - SKU003 (Wireless Mouse)
     - SKU004 (Standing Desk)
     - SKU005 (USB Cable)
   - **For Budget**: Dropdown with departments
     - Marketing, Engineering, Operations, HR
   - **For Resource**: Dropdown with teams
     - Engineering, Sales, Marketing, Operations
   - **For Sales**: Overall or category-based options

3. **📅 Time Horizon Slider**
   - **Range**: 7 to 90 days
   - **Default**: 30 days
   - **Purpose**: How far into the future to predict
   - **Impact**: Longer periods = less confidence but more strategic planning

4. **⚙️ Advanced Options** (Collapsible Section)
   - **Confidence Threshold**: Minimum confidence level to show
   - **Include Weekends**: Whether to include weekend predictions
   - **Seasonal Adjustment**: Account for seasonal patterns
   - **Data Quality Filter**: Only use high-quality historical data

**🚀 Action Buttons:**

5. **🔮 Generate Prediction** (Large, Primary Button)
   - **Purpose**: Main action button - starts the ML prediction
   - **What happens**: 
     - Sends request to prediction service
     - Shows loading spinner
     - Updates main content area with results
   - **Time**: Takes 1-2 seconds to complete

6. **🔄 Refresh Data** (Secondary Button)
   - **Purpose**: Reload fresh data from ERP system
   - **When to use**: If you suspect data has changed recently

7. **📋 Export Results** (Secondary Button)
   - **Purpose**: Download predictions as CSV/Excel
   - **Available after**: Successful prediction generation

**📊 Service Status Indicators:**

8. **🟢 ERP Service Status**
   - **Green**: Connected and healthy
   - **Red**: Connection error or service down
   - **Shows**: Last update time and response time

9. **🟢 Prediction Service Status**
   - **Green**: ML models ready
   - **Yellow**: Loading or updating models
   - **Red**: Service unavailable

### 🖥️ **Main Content Area - Results Display**

**📈 Section 1: Key Metrics Cards (Top Row)**

- **📊 Current Value**: Shows current inventory/budget/utilization level
- **🎯 Predicted Change**: Percentage increase/decrease expected
- **⚡ Confidence Score**: Overall prediction reliability (0-100%)
- **⚠️ Alert Status**: Risk level (Low/Medium/High) with color coding

**📊 Section 2: Interactive Charts (Center)**

1. **📈 Main Prediction Chart**
   - **X-Axis**: Time (days into the future)
   - **Y-Axis**: Predicted values (inventory levels, spending, utilization)
   - **Blue Line**: Historical data (dotted)
   - **Green Line**: Predictions (solid)
   - **Gray Shaded Area**: Confidence intervals
   - **Interactive**: Hover for exact values, zoom, pan

2. **📊 Confidence Chart** (Below main chart)
   - **Shows**: How confidence decreases over time
   - **Color coding**: Green (high), Yellow (medium), Red (low)

**💡 Section 3: Business Insights (Right Side)**

- **🎯 Key Insights**: 3-5 bullet points with actionable recommendations
- **⚠️ Alerts**: Automatic warnings about risks
- **📋 Action Items**: Suggested next steps
- **📊 Impact Analysis**: Potential cost savings or revenue impact

**📋 Section 4: Detailed Data Table (Bottom)**

- **📅 Date Column**: Each day in the prediction horizon
- **📊 Predicted Value**: Numeric prediction for that day
- **🎯 Confidence**: Confidence level (0-100%)
- **📈 Change**: Day-over-day change
- **💡 Notes**: Any special considerations for that day

### 🎨 **Visual Design Elements**

**🎨 Color Coding System:**
- **🟢 Green**: Good performance, low risk, high confidence
- **🟡 Yellow**: Moderate risk, medium confidence, attention needed
- **🟠 Orange**: Warning, declining performance, action recommended
- **🔴 Red**: High risk, low confidence, immediate action required
- **🔵 Blue**: Neutral information, historical data

**📊 Chart Types You'll See:**
- **Line Charts**: Trends over time
- **Area Charts**: Confidence intervals
- **Bar Charts**: Comparative data
- **Gauge Charts**: Performance meters
- **Heatmaps**: Risk assessment matrices

### 🎯 **Interactive Features**

**🖱️ What You Can Click/Interact With:**

1. **Chart Interactions**:
   - **Hover**: See exact values and dates
   - **Zoom**: Click and drag to zoom into time periods
   - **Legend**: Click to show/hide data series
   - **Reset**: Double-click to reset zoom

2. **Sidebar Interactions**:
   - **All dropdowns**: Click to expand options
   - **Sliders**: Drag to adjust values
   - **Checkboxes**: Enable/disable features
   - **Collapsible sections**: Click headers to expand/collapse

3. **Data Table Interactions**:
   - **Sort**: Click column headers to sort data
   - **Filter**: Search within table data
   - **Export**: Download filtered results

### 📱 **Responsive Design**

**💻 Desktop (Recommended)**: Full layout with sidebar and charts
**📱 Tablet**: Sidebar becomes collapsible, charts stack vertically
**📱 Mobile**: Single column layout, simplified charts

### 🚀 **Demo Flow Walkthrough**

**Perfect Demo Sequence:**

1. **Start**: Open dashboard, point out clean layout
2. **Select**: Choose "Inventory" → "SKU001" → "30 days"
3. **Predict**: Click "Generate Prediction", watch loading
4. **Explain Chart**: Point to declining trend, confidence bands
5. **Show Insights**: Read key recommendations aloud
6. **Change Scenario**: Switch to "Budget" → "Marketing" → "60 days"
7. **Compare**: Show different chart types and insights
8. **Interact**: Hover over charts, zoom in/out
9. **Wrap up**: Export results, show data table

This UI is designed for **business users** who need quick insights without technical complexity!

### Option 2: Docker Deployment

**Prerequisites:**
- Docker & Docker Compose

**Setup:**
```bash
# 1. Start all services
docker-compose up --build

# 2. Generate sample data
docker-compose exec erp-service python create_db.py

# 3. Access dashboard
open http://localhost:3000
```

## 📋 Usage Guide

### 1. Dashboard Navigation

**Main Interface:**
- **Sidebar**: Select prediction type, entity, and time horizon
- **Service Status**: Monitor backend service health
- **Quick Actions**: Demo data and export functions

**Prediction Types:**
- 📦 **Inventory**: Forecast product demand (SKU001-SKU005)
- 💰 **Budget**: Analyze department spending (Marketing, Engineering, Operations, HR)
- 👥 **Resources**: Plan team utilization (Engineering, Sales, Marketing, Operations)
- 📈 **Sales**: Revenue forecasting (overall trends)

### 2. Generating Predictions

1. **Select Parameters** in sidebar:
   - Choose prediction type
   - Select entity (product, department, etc.)
   - Set forecast horizon (7-90 days)
   - Configure advanced options if needed

2. **Click "Generate Prediction"** button

3. **Review Results**:
   - Key metrics and trends
   - Interactive charts with confidence bands
   - Business insights and recommendations
   - Detailed data tables

### 3. API Usage

**Prediction Endpoint:**
```bash
curl -X POST http://localhost:3002/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "prediction_type": "inventory",
    "entity_id": "SKU001",
    "time_horizon": 30
  }'
```

**Health Check:**
```bash
curl http://localhost:3002/health
```

**Available Prediction Types:**
```bash
curl http://localhost:3002/api/v1/predict/types
```

## 🛠️ Development Guide

### Project Structure

```
ai-predictor/
├── erp-service/                 # Mock ERP backend
│   ├── app.py                  # Main Flask application
│   ├── config/settings.py      # Configuration
│   ├── models/database.py      # Data models
│   ├── routes/                 # API endpoints
│   ├── services/               # Business logic
│   └── utils/helpers.py        # Utilities
├── prediction-service/         # ML prediction service
│   ├── app.py                  # Main FastAPI application
│   ├── config/settings.py      # Configuration  
│   ├── models/                 # ML models & schemas
│   ├── routes/                 # API endpoints
│   ├── services/               # ML pipeline
│   └── utils/insights.py       # Business insights
├── frontend/                   # Streamlit dashboard
│   ├── app.py                  # Main application
│   ├── config/settings.py      # Configuration
│   ├── components/             # UI components
│   └── utils/                  # API clients & formatters
├── docker-compose.yml          # Container orchestration
├── create_db.py               # Database setup script
└── README.md                  # This file
```

### Local Development Setup

**1. Environment Setup:**
```bash
# Install Python dependencies for each service
pip install flask fastapi uvicorn streamlit requests pandas scikit-learn plotly httpx
```

**2. Database Setup:**
```bash
# Create SQLite database with sample data
python create_db.py
```

**3. Service Configuration:**
Each service has its own `config/settings.py` for environment-specific settings.

**4. Running Individual Services:**
```bash
# ERP Service (port 3001)
cd erp-service && python app.py

# Prediction Service (port 3002)  
cd prediction-service && python app.py

# Frontend (port 3000)
cd frontend && streamlit run app.py
```

### Adding New Prediction Types

**1. Update ERP Service:**
- Add new routes in `routes/` directory
- Implement business logic in `services/`
- Update data models if needed

**2. Update Prediction Service:**
- Add feature engineering in `services/feature_engineer.py`
- Update prediction logic in `services/prediction_engine.py`
- Add insights generation in `utils/insights.py`

**3. Update Frontend:**
- Add UI components in `components/`
- Update entity mappings in `components/sidebar.py`

## 🧪 Demo Scenarios

### Inventory Crisis Prediction
```json
{
  "prediction_type": "inventory",
  "entity_id": "SKU001", 
  "time_horizon": 30
}
```
**Expected Output:**
- Laptop demand trending analysis
- Stock-out risk warnings
- Reorder recommendations

### Budget Variance Alert
```json
{
  "prediction_type": "budget",
  "entity_id": "Marketing",
  "time_horizon": 60  
}
```
**Expected Output:**
- Spending pattern analysis
- Budget variance warnings
- Cost control recommendations

### Resource Planning
```json
{
  "prediction_type": "resource",
  "entity_id": "Engineering", 
  "time_horizon": 45
}
```
**Expected Output:**
- Team utilization forecasts
- Capacity planning insights
- Hiring recommendations

## 🔧 Configuration

### Environment Variables

**ERP Service:**
- `DB_PATH`: Database file location
- `ERP_HOST`: Service host (default: localhost)
- `ERP_PORT`: Service port (default: 3001)

**Prediction Service:**
- `ERP_SERVICE_URL`: ERP service URL
- `PREDICTION_HOST`: Service host (default: 0.0.0.0)
- `PREDICTION_PORT`: Service port (default: 3002)

**Frontend:**
- `PREDICTION_API_URL`: Prediction service URL
- `ERP_API_URL`: ERP service URL (for direct calls)

### Docker Configuration

**For Docker Deployment:**
Services automatically discover each other using Docker networking.

**For Local Development:**
Services connect via localhost URLs.

## 📊 Performance Metrics

**Response Times:**
- ERP Service: < 100ms (SQLite queries)
- Prediction Service: < 2 seconds (ML processing)
- Frontend: Interactive (client-side rendering)

**Data Processing:**
- Handles 180 days of historical data
- Supports 50+ data points per prediction
- Real-time feature engineering

**Scalability:**
- 10+ concurrent prediction requests
- Memory usage: < 512MB per service
- Horizontal scaling with load balancers

## 🚨 Troubleshooting

### Common Issues

**1. "Connection Error" in Frontend:**
```bash
# Check if services are running
curl http://localhost:3001/health
curl http://localhost:3002/health

# Verify service URLs in frontend/config/settings.py
```

**2. "Database Error" in ERP Service:**
```bash
# Recreate database
python create_db.py

# Check database permissions
ls -la erp_demo.db
```

**3. "Module Import Error":**
```bash
# Install missing dependencies
pip install -r erp-service/requirements.txt
pip install -r prediction-service/requirements.txt
pip install -r frontend/requirements.txt
```

**4. "Port Already in Use":**
```bash
# Find and kill processes
lsof -i :3001
lsof -i :3002
lsof -i :3000

# Or change ports in config/settings.py
```

### Debug Mode

**Enable Detailed Logging:**
```python
# In any service's config/settings.py
DEBUG = True
```

**View Service Logs:**
```bash
# Docker logs
docker-compose logs -f prediction-service

# Local development - logs appear in terminal
```

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-prediction-type`
3. **Make changes** following the modular architecture
4. **Test thoroughly** with all services running
5. **Submit pull request** with detailed description

### Code Style

- **Python**: Follow PEP 8
- **Documentation**: Docstrings for all functions
- **Error Handling**: Graceful fallbacks
- **Logging**: Structured logging with context

### Testing

**Manual Testing:**
```bash
# Test all endpoints
curl http://localhost:3001/api/v1/inventory/items
curl -X POST http://localhost:3002/api/v1/predict -d '{"prediction_type":"inventory","entity_id":"SKU001","time_horizon":30}' -H "Content-Type: application/json"
```

## 📄 License

Built for educational and demonstration purposes. 

## 🎯 Roadmap

- [ ] **Advanced ML Models**: LSTM, Prophet for time series
- [ ] **Real-time Data**: WebSocket connections for live updates  
- [ ] **Authentication**: User management and API keys
- [ ] **Monitoring**: Metrics, alerts, and dashboards
- [ ] **Multi-tenancy**: Support for multiple organizations
- [ ] **Export Features**: PDF reports, Excel dashboards

---

**🚀 Ready to predict the future of your ERP data!**

For questions or issues, please create a GitHub issue or contact the development team.