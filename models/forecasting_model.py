import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from database.db import get_sales_history, get_product_by_id
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# FORECASTING MODELS
# ============================================================================

class DemandForecaster:
    """AI-powered demand forecasting engine."""
    
    def __init__(self, product_id):
        self.product_id = product_id
        self.sales_data = self._get_sales_data()
    
    def _get_sales_data(self):
        """Retrieve sales data for the product."""
        try:
            sales_df = get_sales_history(product_id=self.product_id, days=180)
            if not sales_df.empty:
                sales_df['date'] = pd.to_datetime(sales_df['date'])
                sales_df = sales_df.sort_values('date')
            return sales_df
        except Exception as e:
            print(f"Error retrieving sales data: {str(e)}")
            return pd.DataFrame()
    
    def linear_regression_forecast(self, days=30):
        """Forecast demand using Linear Regression."""
        try:
            if len(self.sales_data) < 7:
                return None
            
            # Aggregate daily sales
            daily_sales = self.sales_data.groupby('date')['quantity'].sum().reset_index()
            daily_sales['date'] = pd.to_datetime(daily_sales['date'])
            daily_sales = daily_sales.sort_values('date')
            
            # Create feature: days since start
            daily_sales['day_num'] = (daily_sales['date'] - daily_sales['date'].min()).dt.days.values
            
            X = daily_sales['day_num'].values.reshape(-1, 1)
            y = daily_sales['quantity'].values
            
            # Train model
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict future days
            last_day = X[-1][0]
            future_days = np.array([last_day + i for i in range(1, days + 1)]).reshape(-1, 1)
            predictions = model.predict(future_days)
            predictions = np.maximum(predictions, 0)  # No negative predictions
            
            # Create forecast dataframe
            forecast_dates = [daily_sales['date'].max() + timedelta(days=i) for i in range(1, days + 1)]
            forecast_df = pd.DataFrame({
                'date': forecast_dates,
                'predicted_quantity': predictions.round(2)
            })
            
            return forecast_df
        
        except Exception as e:
            print(f"Error in linear regression forecast: {str(e)}")
            return None
    
    def moving_average_forecast(self, days=30, window=7):
        """Forecast demand using Moving Average."""
        try:
            if len(self.sales_data) < window:
                return None
            
            # Aggregate daily sales
            daily_sales = self.sales_data.groupby('date')['quantity'].sum().reset_index()
            daily_sales['date'] = pd.to_datetime(daily_sales['date'])
            daily_sales = daily_sales.sort_values('date')
            
            # Calculate moving average
            moving_avg = daily_sales['quantity'].rolling(window=window).mean().iloc[-1]
            
            if pd.isna(moving_avg):
                moving_avg = daily_sales['quantity'].mean()
            
            # Create forecast
            forecast_dates = [daily_sales['date'].max() + timedelta(days=i) for i in range(1, days + 1)]
            forecast_df = pd.DataFrame({
                'date': forecast_dates,
                'predicted_quantity': [moving_avg] * days
            })
            
            return forecast_df
        
        except Exception as e:
            print(f"Error in moving average forecast: {str(e)}")
            return None
    
    def exponential_smoothing_forecast(self, days=30, alpha=0.3):
        """Forecast demand using Exponential Smoothing."""
        try:
            if len(self.sales_data) < 3:
                return None
            
            # Aggregate daily sales
            daily_sales = self.sales_data.groupby('date')['quantity'].sum().reset_index()
            daily_sales['date'] = pd.to_datetime(daily_sales['date'])
            daily_sales = daily_sales.sort_values('date')
            
            quantities = daily_sales['quantity'].values
            
            # Exponential smoothing
            smoothed = [quantities[0]]
            for i in range(1, len(quantities)):
                smoothed.append(alpha * quantities[i] + (1 - alpha) * smoothed[i-1])
            
            last_smoothed = smoothed[-1]
            
            # Forecast
            forecast_dates = [daily_sales['date'].max() + timedelta(days=i) for i in range(1, days + 1)]
            forecast_df = pd.DataFrame({
                'date': forecast_dates,
                'predicted_quantity': [last_smoothed] * days
            })
            
            return forecast_df
        
        except Exception as e:
            print(f"Error in exponential smoothing forecast: {str(e)}")
            return None
    
    def ensemble_forecast(self, days=30):
        """Combine multiple forecasting methods for better accuracy."""
        try:
            lr_forecast = self.linear_regression_forecast(days)
            ma_forecast = self.moving_average_forecast(days)
            es_forecast = self.exponential_smoothing_forecast(days)
            
            if lr_forecast is not None and ma_forecast is not None and es_forecast is not None:
                # Average the predictions
                ensemble_predictions = (
                    lr_forecast['predicted_quantity'].values +
                    ma_forecast['predicted_quantity'].values +
                    es_forecast['predicted_quantity'].values
                ) / 3
                
                ensemble_df = pd.DataFrame({
                    'date': lr_forecast['date'],
                    'predicted_quantity': ensemble_predictions.round(2)
                })
                
                return ensemble_df
            elif lr_forecast is not None:
                return lr_forecast
            elif ma_forecast is not None:
                return ma_forecast
            else:
                return es_forecast
        
        except Exception as e:
            print(f"Error in ensemble forecast: {str(e)}")
            return None

# ============================================================================
# FORECASTING FUNCTIONS
# ============================================================================

def forecast_demand(product_id, days=30, method='ensemble'):
    """Forecast demand for a product.
    
    Args:
        product_id: Product ID to forecast
        days: Number of days to forecast (7, 30, or 90)
        method: Forecasting method ('linear', 'moving_average', 'exponential', or 'ensemble')
    
    Returns:
        DataFrame with forecast data or None
    """
    try:
        forecaster = DemandForecaster(product_id)
        
        if forecaster.sales_data.empty:
            return None
        
        if method == 'linear':
            return forecaster.linear_regression_forecast(days)
        elif method == 'moving_average':
            return forecaster.moving_average_forecast(days)
        elif method == 'exponential':
            return forecaster.exponential_smoothing_forecast(days)
        else:  # ensemble
            return forecaster.ensemble_forecast(days)
    
    except Exception as e:
        print(f"Error forecasting demand: {str(e)}")
        return None

def get_actual_vs_predicted(product_id, forecast_days=30):
    """Get actual sales vs predicted sales for comparison."""
    try:
        # Get forecast
        forecast_df = forecast_demand(product_id, days=forecast_days)
        
        if forecast_df is None:
            return None
        
        # Get actual sales for comparison period
        sales_df = get_sales_history(product_id=product_id, days=forecast_days)
        
        if sales_df.empty:
            return forecast_df.assign(actual_quantity=0)
        
        sales_df['date'] = pd.to_datetime(sales_df['date'])
        actual_by_date = sales_df.groupby('date')['quantity'].sum().reset_index()
        actual_by_date.columns = ['date', 'actual_quantity']
        
        # Merge
        comparison = forecast_df.merge(actual_by_date, on='date', how='left')
        comparison['actual_quantity'] = comparison['actual_quantity'].fillna(0)
        
        return comparison
    
    except Exception as e:
        print(f"Error getting actual vs predicted: {str(e)}")
        return None

def predict_stockout(product_id, days=7):
    """Predict if a product will go out of stock."""
    try:
        product = get_product_by_id(product_id)
        if not product:
            return False
        
        current_stock = product[5]
        
        # Get forecast
        forecast_df = forecast_demand(product_id, days=days)
        
        if forecast_df is None or forecast_df.empty:
            return False
        
        # Sum predicted demand
        predicted_demand = forecast_df['predicted_quantity'].sum()
        
        # Check if stock will run out
        return current_stock < predicted_demand
    
    except Exception as e:
        print(f"Error predicting stockout: {str(e)}")
        return False

def forecast_inventory_requirement(product_id, days=30):
    """Calculate inventory requirement based on forecast."""
    try:
        forecast_df = forecast_demand(product_id, days=days)
        
        if forecast_df is None or forecast_df.empty:
            return 0
        
        return forecast_df['predicted_quantity'].sum()
    
    except Exception as e:
        print(f"Error forecasting inventory requirement: {str(e)}")
        return 0

def calculate_forecast_accuracy(product_id, days=30):
    """Calculate forecast accuracy by comparing with actual sales."""
    try:
        # Get comparison data (from at least 30 days ago)
        sales_df = get_sales_history(product_id=product_id, days=60)
        
        if len(sales_df) < 14:
            return None
        
        # Split data
        train_data = sales_df.iloc[:len(sales_df)//2]
        test_data = sales_df.iloc[len(sales_df)//2:]
        
        if test_data.empty:
            return None
        
        # Simple accuracy metric: Mean Absolute Percentage Error (MAPE)
        actual_avg = test_data['quantity'].mean()
        predicted_avg = train_data['quantity'].mean()
        
        if actual_avg == 0:
            return 0
        
        mape = abs((actual_avg - predicted_avg) / actual_avg) * 100
        accuracy = max(0, 100 - mape)
        
        return round(accuracy, 2)
    
    except Exception as e:
        print(f"Error calculating accuracy: {str(e)}")
        return None

def get_top_selling_products(limit=5):
    """Get top selling products by quantity."""
    try:
        sales_df = get_sales_history(days=90)
        
        if sales_df.empty:
            return pd.DataFrame()
        
        top_products = sales_df.groupby('product_id')['quantity'].sum().nlargest(limit).reset_index()
        top_products.columns = ['product_id', 'total_quantity']
        
        # Add product names
        product_names = []
        for pid in top_products['product_id']:
            product = get_product_by_id(pid)
            if product:
                product_names.append(product[1])
            else:
                product_names.append(pid)
        
        top_products['product_name'] = product_names
        
        return top_products
    
    except Exception as e:
        print(f"Error getting top selling products: {str(e)}")
        return pd.DataFrame()
