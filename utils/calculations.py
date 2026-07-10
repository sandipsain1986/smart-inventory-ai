import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from database.db import get_product_by_id, get_sales_history, get_all_products, get_inventory_value

# ============================================================================
# INVENTORY CALCULATIONS
# ============================================================================

def calculate_inventory_health_score():
    """Calculate overall inventory health score (0-100)."""
    try:
        products = get_all_products()
        
        if not products:
            return 0
        
        total_items = len(products)
        
        # Score factors
        in_stock_count = sum([1 for p in products if p[5] > p[6]])  # quantity > min_stock
        overstock_count = sum([1 for p in products if p[5] > (p[6] * 5)])  # overstock
        low_stock_count = sum([1 for p in products if 0 < p[5] <= p[6]])  # low stock
        out_of_stock_count = sum([1 for p in products if p[5] == 0])  # out of stock
        
        # Calculate score
        optimal_items_score = (in_stock_count / total_items) * 40
        overstock_penalty = (overstock_count / total_items) * 10
        low_stock_penalty = (low_stock_count / total_items) * 30
        out_of_stock_penalty = (out_of_stock_count / total_items) * 20
        
        health_score = optimal_items_score - overstock_penalty - low_stock_penalty - out_of_stock_penalty
        health_score = max(0, min(100, health_score))  # Clamp between 0-100
        
        return round(health_score, 1)
    
    except Exception as e:
        print(f"Error calculating health score: {str(e)}")
        return 0

def calculate_stock_status(quantity, minimum_stock):
    """Determine stock status: 'In Stock', 'Low Stock', or 'Out of Stock'."""
    if quantity == 0:
        return "Out of Stock"
    elif quantity <= minimum_stock:
        return "Low Stock"
    else:
        return "In Stock"

def calculate_reorder_quantity(product_id, lead_time_days=5, safety_stock_days=7):
    """Calculate optimal reorder quantity using EOQ model."""
    try:
        product = get_product_by_id(product_id)
        if not product:
            return 0
        
        sales_df = get_sales_history(product_id=product_id, days=90)
        
        if sales_df.empty or len(sales_df) < 7:
            return product[6] * 2  # Default: 2x minimum stock
        
        # Calculate average daily demand
        avg_daily_demand = sales_df['quantity'].sum() / 90
        
        # Calculate safety stock
        safety_stock = avg_daily_demand * safety_stock_days
        
        # Calculate reorder point (lead time demand + safety stock)
        reorder_point = (avg_daily_demand * lead_time_days) + safety_stock
        
        # Current stock
        current_stock = product[5]
        
        # Reorder quantity
        reorder_qty = max(0, reorder_point - current_stock)
        
        return round(reorder_qty)
    
    except Exception as e:
        print(f"Error calculating reorder quantity: {str(e)}")
        return 0

def calculate_reorder_date(product_id, lead_time_days=5):
    """Calculate when to place a reorder."""
    try:
        product = get_product_by_id(product_id)
        if not product:
            return None
        
        sales_df = get_sales_history(product_id=product_id, days=90)
        
        if sales_df.empty or len(sales_df) < 7:
            return datetime.now() + timedelta(days=3)
        
        # Calculate average daily demand
        avg_daily_demand = sales_df['quantity'].sum() / 90
        
        if avg_daily_demand == 0:
            return datetime.now() + timedelta(days=7)
        
        # Days of stock remaining
        current_stock = product[5]
        minimum_stock = product[6]
        stock_buffer = current_stock - minimum_stock
        
        if stock_buffer <= 0:
            return datetime.now()  # Order immediately
        
        days_until_reorder = stock_buffer / avg_daily_demand
        reorder_date = datetime.now() + timedelta(days=days_until_reorder - lead_time_days)
        
        return max(datetime.now(), reorder_date)
    
    except Exception as e:
        print(f"Error calculating reorder date: {str(e)}")
        return datetime.now()

def get_reorder_priority(product_id):
    """Determine reorder priority: 'Urgent', 'High', 'Medium', 'Low'."""
    try:
        product = get_product_by_id(product_id)
        if not product:
            return "Low"
        
        current_stock = product[5]
        minimum_stock = product[6]
        
        # Calculate urgency
        if current_stock == 0:
            return "Urgent"
        elif current_stock < minimum_stock:
            return "Urgent"
        elif current_stock <= minimum_stock * 1.5:
            return "High"
        elif current_stock <= minimum_stock * 3:
            return "Medium"
        else:
            return "Low"
    
    except Exception as e:
        print(f"Error determining reorder priority: {str(e)}")
        return "Low"

# ============================================================================
# SALES CALCULATIONS
# ============================================================================

def calculate_average_daily_sales(product_id, days=30):
    """Calculate average daily sales for a product."""
    try:
        sales_df = get_sales_history(product_id=product_id, days=days)
        
        if sales_df.empty:
            return 0
        
        return round(sales_df['quantity'].sum() / days, 2)
    
    except Exception as e:
        print(f"Error calculating average daily sales: {str(e)}")
        return 0

def calculate_revenue_metrics(product_id=None, days=30):
    """Calculate revenue metrics."""
    try:
        if product_id:
            sales_df = get_sales_history(product_id=product_id, days=days)
        else:
            sales_df = get_sales_history(days=days)
        
        if sales_df.empty:
            return {
                'total_revenue': 0,
                'average_revenue': 0,
                'max_revenue': 0,
                'min_revenue': 0
            }
        
        return {
            'total_revenue': round(sales_df['revenue'].sum(), 2),
            'average_revenue': round(sales_df['revenue'].mean(), 2),
            'max_revenue': round(sales_df['revenue'].max(), 2),
            'min_revenue': round(sales_df['revenue'].min(), 2),
            'transaction_count': len(sales_df)
        }
    
    except Exception as e:
        print(f"Error calculating revenue metrics: {str(e)}")
        return {}

def calculate_sales_trend(product_id=None, days=30):
    """Calculate sales trend (increasing, decreasing, stable)."""
    try:
        if product_id:
            sales_df = get_sales_history(product_id=product_id, days=days)
        else:
            sales_df = get_sales_history(days=days)
        
        if len(sales_df) < 2:
            return "insufficient_data"
        
        # Split into two halves
        mid_point = len(sales_df) // 2
        first_half = sales_df['quantity'].iloc[:mid_point].sum()
        second_half = sales_df['quantity'].iloc[mid_point:].sum()
        
        if second_half > first_half * 1.1:
            return "increasing"
        elif second_half < first_half * 0.9:
            return "decreasing"
        else:
            return "stable"
    
    except Exception as e:
        print(f"Error calculating sales trend: {str(e)}")
        return "error"

# ============================================================================
# INVENTORY VALUE CALCULATIONS
# ============================================================================

def calculate_product_value(product_id):
    """Calculate inventory value for a product."""
    try:
        product = get_product_by_id(product_id)
        if not product:
            return 0
        
        price = product[4]
        quantity = product[5]
        
        return round(price * quantity, 2)
    
    except Exception as e:
        print(f"Error calculating product value: {str(e)}")
        return 0

def calculate_category_value(category):
    """Calculate total inventory value for a category."""
    try:
        products = get_all_products()
        category_products = [p for p in products if p[2] == category]
        
        total_value = sum([p[4] * p[5] for p in category_products])
        
        return round(total_value, 2)
    
    except Exception as e:
        print(f"Error calculating category value: {str(e)}")
        return 0

# ============================================================================
# KPI CALCULATIONS
# ============================================================================

def get_dashboard_kpis():
    """Get all KPIs for dashboard."""
    try:
        products = get_all_products()
        sales_df = get_sales_history(days=30)
        
        total_products = len(products)
        total_units = sum([p[5] for p in products])
        total_value = get_inventory_value()
        total_sales = sales_df['revenue'].sum() if not sales_df.empty else 0
        
        # Monthly revenue
        monthly_sales_df = get_sales_history(days=30)
        monthly_revenue = monthly_sales_df['revenue'].sum() if not monthly_sales_df.empty else 0
        
        # Low stock count
        low_stock_count = sum([1 for p in products if p[5] <= p[6]])
        
        # Predicted stockouts (simplified)
        stockout_count = sum([1 for p in products if p[5] == 0])
        
        # Health score
        health_score = calculate_inventory_health_score()
        
        return {
            'total_products': total_products,
            'total_units': total_units,
            'total_value': round(total_value, 2),
            'total_sales': round(total_sales, 2),
            'monthly_revenue': round(monthly_revenue, 2),
            'low_stock_count': low_stock_count,
            'stockout_count': stockout_count,
            'health_score': health_score
        }
    
    except Exception as e:
        print(f"Error calculating KPIs: {str(e)}")
        return {}
