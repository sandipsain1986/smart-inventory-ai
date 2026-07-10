# Smart Inventory Forecast AI

## Professional Retail Inventory Management & AI-Powered Demand Forecasting System

### 🎯 Overview

Smart Inventory Forecast AI is a comprehensive inventory management and demand forecasting dashboard built with Python and Streamlit. It helps retail businesses:

- 📊 Track inventory in real-time
- 📈 Analyze sales trends
- 🤖 Predict future demand using machine learning
- 💡 Get smart reorder recommendations
- ⚠️ Receive intelligent alerts
- 📋 Generate detailed reports

### 🚀 Features

#### 1. **Professional Dashboard**
- Modern, responsive UI with sidebar navigation
- 8 Key Performance Indicators (KPIs):
  - Total Products
  - Total Inventory Value
  - Total Units in Stock
  - Total Sales
  - Monthly Revenue
  - Low Stock Products
  - Predicted Stockouts
  - Inventory Health Score
- Interactive visualizations
- Sales trends and distributions
- Category-wise analysis

#### 2. **Inventory Management**
- Add, update, and delete products
- Search and filter by category
- Real-time stock status (In Stock, Low Stock, Out of Stock)
- Expiry date tracking
- Product details management

#### 3. **Sales Tracking**
- Record daily sales transactions
- Calculate revenue
- Track product demand
- Historical sales analysis

#### 4. **AI Demand Forecasting**
- Linear Regression forecasting
- Moving Average analysis
- Time series predictions
- 7, 30, and 90-day forecasts
- Actual vs Predicted comparison
- Stock-out predictions

#### 5. **Smart Reorder System**
- Automatic reorder quantity calculation
- Lead time consideration
- Safety stock calculation
- Priority-based recommendations

#### 6. **Alert System**
- Low stock warnings
- Overstock alerts
- Expiring product notifications
- Predicted stockout warnings

#### 7. **Analytics & Reports**
- Interactive Plotly charts
- Sales performance analysis
- Inventory distribution
- Category analysis
- CSV report exports

#### 8. **Excel Import**
- Import products from Excel
- Import sales data from Excel
- Data preview before import

### 📋 Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python 3
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: Scikit-learn
- **Visualizations**: Plotly
- **Database**: SQLite
- **Excel Support**: OpenPyXL

### 📁 Project Structure

```
smart-inventory-ai/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── database/
│   └── db.py                       # Database operations
│
├── pages/
│   ├── dashboard.py                # Dashboard page
│   ├── inventory.py                # Inventory management
│   ├── sales.py                    # Sales tracking
│   ├── forecast.py                 # AI forecasting
│   └── reports.py                  # Report generation
│
├── models/
│   └── forecasting_model.py        # ML forecasting models
│
├── utils/
│   ├── calculations.py             # Business logic
│   ├── alerts.py                   # Alert system
│   └── theme.py                    # UI theming
│
└── data/
    ├── products.csv                # Sample product data
    └── sales.csv                   # Sample sales data
```

### 🔧 Installation & Setup

#### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

#### Step 1: Clone the Repository
```bash
git clone https://github.com/sandipsain1986/smart-inventory-ai.git
cd smart-inventory-ai
```

#### Step 2: Create Virtual Environment (Optional but Recommended)
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Run the Application
```bash
streamlit run app.py
```

The application will open at `http://localhost:8501`

### 🎮 How to Use

#### Dashboard
1. View real-time KPIs
2. Monitor inventory health
3. Check sales trends
4. Identify low stock items

#### Inventory Management
1. **Add Product**: Click "Add New Product" and fill in details
2. **Update Product**: Select product and modify fields
3. **Delete Product**: Remove products from inventory
4. **Search/Filter**: Find products by name or category

#### Sales Tracking
1. **Record Sale**: Enter product ID, quantity, and date
2. **View History**: See all sales transactions
3. **Analyze Trends**: Check demand patterns

#### Forecasting
1. **Select Product**: Choose item to forecast
2. **Choose Period**: 7, 30, or 90 days
3. **View Predictions**: See forecast graphs and metrics
4. **Export Report**: Download forecast results

#### Reorder Recommendations
1. System automatically calculates optimal reorder points
2. Considers current stock, demand, and lead time
3. Prioritizes urgent orders

#### Reports
1. **Inventory Report**: Current stock levels
2. **Sales Report**: Historical transactions
3. **Forecast Report**: Predictions and recommendations
4. Download as CSV for further analysis

### 📊 Sample Data

The system comes pre-loaded with realistic sample data:

**Products**: Electronics, Grocery, Fashion, Home Appliances  
**Sales Data**: 6+ months of historical transactions  
**Categories**: Diverse product mix for demo purposes

### 🤖 Machine Learning Models

#### Linear Regression
- Predicts demand based on historical trends
- Best for stable, linear growth patterns

#### Moving Average
- Smooths out seasonal variations
- Considers recent sales patterns
- 7-day and 30-day windows

#### Time Series Analysis
- Captures temporal patterns
- Identifies seasonality
- Accounts for trend components

### 📈 Dashboard KPIs Explained

| KPI | Description |
|-----|-------------|
| **Total Products** | Count of unique items in inventory |
| **Total Inventory Value** | Sum of (quantity × price) for all products |
| **Total Units in Stock** | Total quantity across all products |
| **Total Sales** | Revenue from all transactions |
| **Monthly Revenue** | Current month sales total |
| **Low Stock Products** | Items below minimum threshold |
| **Predicted Stockouts** | Items likely to run out soon |
| **Inventory Health Score** | 0-100 rating of inventory efficiency |

### 🎨 Color Scheme

- **Primary**: Dark Blue (#1f77b4)
- **Secondary**: Green (#2ca02c)
- **Warning**: Orange (#ff7f0e)
- **Danger**: Red (#d62728)

### ⚠️ Alert Types

1. **Low Stock Warning** (Yellow): Product below minimum level
2. **Overstock Warning** (Orange): Excess inventory detected
3. **Expiry Alert** (Red): Product expiring soon
4. **Stockout Prediction** (Red): AI predicts stock-out

### 📧 Excel Import Format

#### Products CSV/Excel
```
Product ID | Name | Category | Supplier | Price | Quantity | Min Stock | Mfg Date | Expiry Date
001 | Laptop | Electronics | TechCorp | 999.99 | 50 | 10 | 2023-01-01 | 2025-01-01
```

#### Sales CSV/Excel
```
Sale ID | Product ID | Date | Quantity Sold | Revenue
001 | 001 | 2024-01-15 | 5 | 4999.95
```

### 🔐 Database

- **Type**: SQLite (lightweight, no server needed)
- **Location**: `data/inventory.db`
- **Auto-backup**: Available through reports

### 📱 Responsive Design

- ✅ Works on desktop
- ✅ Responsive layout
- ✅ Mobile-friendly
- ✅ Touch-optimized buttons

### 🚀 Deployment

#### Deploy to Streamlit Cloud
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Deploy!

#### Deploy to Heroku
```bash
heroku create your-app-name
git push heroku main
heroku ps:scale web=1
```

### 💻 API & Functions

#### Database Operations
```python
from database.db import init_db, add_product, get_products

# Initialize database
init_db()

# Add product
add_product(name, category, supplier, price, quantity, min_stock, mfg_date, exp_date)

# Get all products
products = get_products()
```

#### Forecasting
```python
from models.forecasting_model import forecast_demand

# Predict next 30 days
predictions = forecast_demand(product_id, days=30)
```

#### Calculations
```python
from utils.calculations import calculate_reorder_quantity, inventory_health_score

# Get reorder recommendation
reorder_qty = calculate_reorder_quantity(product_id)

# Get health score
score = inventory_health_score()
```

### 🐛 Troubleshooting

#### Issue: "Database locked" error
**Solution**: Close other instances of the app and restart

#### Issue: Forecast shows no data
**Solution**: Ensure product has at least 20 days of sales history

#### Issue: Excel import fails
**Solution**: Check file format (xlsx or csv) and column names

#### Issue: Charts not displaying
**Solution**: Clear browser cache and refresh

### 📊 Sample Output

After running the app, you'll see:
- Real-time dashboard with KPI cards
- Interactive sales trend charts
- Inventory distribution visualizations
- Demand forecast graphs
- Reorder recommendations table
- System alerts and notifications

### 🎯 Use Cases

1. **Small Retail Stores**: Manage inventory efficiently
2. **E-commerce Businesses**: Optimize stock levels
3. **Warehouses**: Track and forecast demand
4. **Supply Chain**: Coordinate reorders
5. **Hackathon Projects**: Showcase AI/ML applications

### 📚 Learning Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [Scikit-learn Guide](https://scikit-learn.org)
- [Pandas Tutorial](https://pandas.pydata.org)
- [Time Series Forecasting](https://en.wikipedia.org/wiki/Time_series)

### 👨‍💻 Author

Developed by: sandipsain1986  
Version: 1.0.0  
Last Updated: 2024

### 📄 License

MIT License - feel free to use for personal and commercial projects

### 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

### 💬 Support

For issues, questions, or suggestions, please open a GitHub issue.

### 🎉 Features Coming Soon

- [ ] Multi-warehouse support
- [ ] REST API
- [ ] Mobile app
- [ ] Advanced ML models (LSTM, Prophet)
- [ ] Supplier integration
- [ ] Real-time notifications
- [ ] Advanced analytics
- [ ] User authentication

---

**Happy Forecasting! 🚀**
