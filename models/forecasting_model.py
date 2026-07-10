import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

def forecast_demand(product_id, days=30, method='ensemble'):
    """
    Forecast demand for a product using specified method.
    Methods: 'linear', 'moving_average', 'exponential', 'ensemble'
    """
    try:
        from database.db import get_sales_history, get_product_by_id
        
        # Get historical sales data
        sales_df = get_sales_history(days=90)
        
        if sales_df.empty:
            return None
        
        # Filter for this product
        product_sales = sales_df[sales_df['product_id'] == product_id]
        
        if product_sales.empty or len(product_sales) < 7:
            return None
        
        product_sales = product_sales.sort_values('date')
        product_sales['date'] = pd.to_datetime(product_sales['date'])
        
        # Group by date and sum quantities
        daily_sales = product_sales.groupby('date')['quantity'].sum().reset_index()
        daily_sales = daily_sales.sort_values('date')
        
        if len(daily_sales) < 7:
            return None
        
        quantities = daily_sales['quantity'].values
        
        # Generate forecast
        if method == 'linear':
            forecast_values = _linear_forecast(quantities, days)
        elif method == 'moving_average':
            forecast_values = _moving_average_forecast(quantities, days)
        elif method == 'exponential':
            forecast_values = _exponential_smoothing_forecast(quantities, days)
        else:  # ensemble
            forecast_values = _ensemble_forecast(quantities, days)
        
        # Create forecast dataframe
        last_date = daily_sales['date'].max()
        forecast_dates = [last_date + timedelta(days=i+1) for i in range(days)]
        
        forecast_df = pd.DataFrame({
            'date': forecast_dates,
            'predicted_quantity': forecast_values
        })
        
        return forecast_df
    
    except Exception as e:
        print(f"Error in forecast_demand: {str(e)}")
        return None

def _linear_forecast(quantities, days):
    """Linear regression forecast."""
    try:
        X = np.arange(len(quantities)).reshape(-1, 1)
        y = quantities
        
        model = LinearRegression()
        model.fit(X, y)
        
        future_X = np.arange(len(quantities), len(quantities) + days).reshape(-1, 1)
        forecast = model.predict(future_X)
        
        return np.maximum(forecast, 0)  # Ensure non-negative values
    except:
        return np.full(days, np.mean(quantities))

def _moving_average_forecast(quantities, days, window=7):
    """Moving average forecast."""
    try:
        avg = np.mean(quantities[-window:])
        return np.full(days, avg)
    except:
        return np.full(days, np.mean(quantities))

def _exponential_smoothing_forecast(quantities, days, alpha=0.3):
    """Exponential smoothing forecast."""
    try:
        result = [quantities[0]]
        
        for i in range(1, len(quantities)):
            result.append(alpha * quantities[i-1] + (1 - alpha) * result[-1])
        
        last_forecast = result[-1]
        return np.full(days, last_forecast)
    except:
        return np.full(days, np.mean(quantities))

def _ensemble_forecast(quantities, days):
    """Ensemble forecast combining multiple methods."""
    try:
        linear = _linear_forecast(quantities, days)
        ma = _moving_average_forecast(quantities, days)
        exp = _exponential_smoothing_forecast(quantities, days)
        
        # Average of all methods
        ensemble = (linear + ma + exp) / 3
        
        return np.maximum(ensemble, 0)
    except:
        return np.full(days, np.mean(quantities))

def get_actual_vs_predicted(product_id, forecast_days=30):
    """Get comparison of actual vs predicted values."""
    try:
        from database.db import get_sales_history
        
        sales_df = get_sales_history(days=forecast_days)
        
        if sales_df.empty:
            return None
        
        product_sales = sales_df[sales_df['product_id'] == product_id]
        product_sales['date'] = pd.to_datetime(product_sales['date'])
        
        daily_sales = product_sales.groupby('date')['quantity'].sum().reset_index()
        daily_sales.columns = ['date', 'actual_quantity']
        
        # Get forecast
        forecast_df = forecast_demand(product_id, days=forecast_days, method='ensemble')
        
        if forecast_df is None or forecast_df.empty:
            return None
        
        forecast_df['date'] = pd.to_datetime(forecast_df['date'])
        
        # Merge on date
        comparison = daily_sales.merge(forecast_df, on='date', how='outer')
        comparison = comparison.sort_values('date')
        comparison['predicted_quantity'] = comparison['predicted_quantity'].fillna(0)
        
        return comparison
    except:
        return None

def predict_stockout(product_id, days=30):
    """Predict if product will stockout."""
    try:
        from database.db import get_product_by_id
        
        product = get_product_by_id(product_id)
        if not product:
            return False
        
        current_stock = product[5]
        
        forecast_df = forecast_demand(product_id, days=days, method='ensemble')
        
        if forecast_df is None or forecast_df.empty:
            return False
        
        total_predicted_demand = forecast_df['predicted_quantity'].sum()
        
        return current_stock < total_predicted_demand
    except:
        return False

def forecast_inventory_requirement(product_id, days=30):
    """Calculate required inventory level."""
    try:
        forecast_df = forecast_demand(product_id, days=days, method='ensemble')
        
        if forecast_df is None or forecast_df.empty:
            return 0
        
        return forecast_df['predicted_quantity'].sum()
    except:
        return 0

def calculate_forecast_accuracy(product_id, days=30):
    """Calculate forecast accuracy based on historical data."""
    try:
        from sklearn.metrics import mean_absolute_percentage_error
        
        comparison = get_actual_vs_predicted(product_id, forecast_days=days)
        
        if comparison is None or comparison.empty:
            return None
        
        # Only use rows where we have both actual and predicted
        comparison = comparison.dropna()
        
        if comparison.empty or len(comparison) < 2:
            return None
        
        actual = comparison['actual_quantity'].values
        predicted = comparison['predicted_quantity'].values
        
        # Handle edge cases
        if np.sum(actual) == 0:
            return None
        
        mape = mean_absolute_percentage_error(actual, predicted)
        accuracy = max(0, 100 * (1 - mape))
        
        return round(accuracy, 2)
    except:
        return None
