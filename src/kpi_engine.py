"""KPI calculation and discovery."""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from src.utils import safe_divide

def calculate_kpis(df: pd.DataFrame, numeric_columns: List[str]) -> pd.DataFrame:
    """Calculate summary KPIs for numeric columns."""
    kpi_rows = []
    for col in numeric_columns:
        series = df[col]
        kpi_rows.append({
            'Column': col,
            'SUM': series.sum(),
            'AVERAGE': series.mean(),
            'MEDIAN': series.median(),
            'MIN': series.min(),
            'MAX': series.max(),
            'COUNT': series.count(),
            'COUNT DISTINCT': series.nunique(),
            'STD': series.std(),
        })
    return pd.DataFrame(kpi_rows)

def discover_kpis(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Automatically discover meaningful KPIs based on column names and relationships."""
    kpis = []
    numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col]) and not pd.api.types.is_bool_dtype(df[col])]
    lower_cols = {col.lower(): col for col in df.columns}

    def get_col(name: str) -> Optional[str]:
        if name in df.columns:
            return name
        if name.lower() in lower_cols:
            return lower_cols[name.lower()]
        return None

    revenue_col = get_col('revenue') or get_col('sales') or get_col('total_revenue') or get_col('total_sales')
    if revenue_col:
        total_revenue = df[revenue_col].sum()
        kpis.append({'Name': f'Total {revenue_col}', 'Value': total_revenue, 'Formula': f'SUM({revenue_col})'})
        kpis.append({'Name': f'Average {revenue_col}', 'Value': df[revenue_col].mean(), 'Formula': f'AVG({revenue_col})'})
        date_col = next((c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])), None)
        if date_col:
            df_sorted = df.sort_values(date_col)
            mid = len(df_sorted) // 2
            if mid > 1:
                prev_period = df_sorted[revenue_col].iloc[:mid].sum()
                curr_period = df_sorted[revenue_col].iloc[mid:].sum()
                growth = safe_divide(curr_period - prev_period, prev_period, default=np.nan)
                if pd.notna(growth):
                    kpis.append({'Name': f'{revenue_col} Growth', 'Value': growth, 'Formula': '(Current - Previous)/Previous'})

    cost_col = get_col('cost') or get_col('total_cost')
    if cost_col:
        total_cost = df[cost_col].sum()
        kpis.append({'Name': f'Total {cost_col}', 'Value': total_cost, 'Formula': f'SUM({cost_col})'})
        if revenue_col:
            profit = df[revenue_col].sum() - total_cost
            kpis.append({'Name': 'Profit', 'Value': profit, 'Formula': f'SUM({revenue_col}) - SUM({cost_col})'})
            margin = safe_divide(profit, df[revenue_col].sum(), default=np.nan)
            if pd.notna(margin):
                kpis.append({'Name': 'Profit Margin', 'Value': margin, 'Formula': 'Profit / Revenue'})

    quantity_col = get_col('quantity') or get_col('qty') or get_col('units')
    if quantity_col:
        total_qty = df[quantity_col].sum()
        kpis.append({'Name': f'Total {quantity_col}', 'Value': total_qty, 'Formula': f'SUM({quantity_col})'})
        if revenue_col:
            avg_price = safe_divide(df[revenue_col].sum(), total_qty)
            kpis.append({'Name': 'Average Price', 'Value': avg_price, 'Formula': f'SUM({revenue_col}) / SUM({quantity_col})'})

    customer_col = get_col('customer_id') or get_col('customer') or get_col('client_id')
    if customer_col:
        unique_customers = df[customer_col].nunique()
        kpis.append({'Name': 'Customer Count', 'Value': unique_customers, 'Formula': f'COUNT DISTINCT({customer_col})'})
        if revenue_col:
            avg_rev_per_cust = safe_divide(df[revenue_col].sum(), unique_customers)
            kpis.append({'Name': 'Revenue per Customer', 'Value': avg_rev_per_cust, 'Formula': f'SUM({revenue_col}) / Customer Count'})

    for col in numeric_cols:
        if col not in [revenue_col, cost_col, quantity_col, customer_col]:
            kpis.append({'Name': f'Total {col}', 'Value': df[col].sum(), 'Formula': f'SUM({col})'})
            kpis.append({'Name': f'Average {col}', 'Value': df[col].mean(), 'Formula': f'AVG({col})'})
    return kpis
