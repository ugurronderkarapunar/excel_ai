"""Derived metric engine with safe expression evaluation."""
import pandas as pd
import numpy as np
import re
from typing import List, Dict, Any, Optional
from src.utils import safe_divide

def safe_eval_expression(df: pd.DataFrame, expression: str) -> pd.Series:
    """Safely evaluate a mathematical expression on dataframe columns using pandas.eval."""
    sanitized = re.sub(r'[^A-Za-z0-9_\s\+\-\*\/\(\)\.\,\:\%\<\>\=]', '', expression)
    if not sanitized:
        raise ValueError("Expression is empty or invalid.")
    cols_used = re.findall(r'[A-Za-z_][A-Za-z0-9_]*', sanitized)
    for col in cols_used:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in dataframe.")
    try:
        result = df.eval(sanitized)
        return result
    except Exception as e:
        raise ValueError(f"Error evaluating expression: {e}")

def auto_generate_derived_metrics(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Generate common derived metrics based on column names."""
    metrics = []
    cols_lower = {col.lower(): col for col in df.columns}

    def get_col(name: str) -> Optional[str]:
        if name in df.columns:
            return name
        if name.lower() in cols_lower:
            return cols_lower[name.lower()]
        return None

    revenue = get_col('revenue') or get_col('sales') or get_col('total_revenue')
    cost = get_col('cost') or get_col('total_cost')
    quantity = get_col('quantity') or get_col('qty')
    visitors = get_col('visitors') or get_col('traffic')
    conversions = get_col('conversions') or get_col('conversion')
    customers = get_col('customers') or get_col('customer_id')

    if revenue and cost:
        metrics.append({
            'name': 'Profit',
            'formula': f"{revenue} - {cost}",
            'description': 'Revenue minus Cost',
            'apply': lambda df: df[revenue] - df[cost]
        })
        metrics.append({
            'name': 'Profit Margin',
            'formula': f"({revenue} - {cost}) / {revenue} * 100",
            'description': 'Profit divided by Revenue times 100',
            'apply': lambda df: safe_divide(df[revenue] - df[cost], df[revenue]) * 100
        })
    if revenue and quantity:
        metrics.append({
            'name': 'Average Price',
            'formula': f"{revenue} / {quantity}",
            'description': 'Revenue per Quantity',
            'apply': lambda df: safe_divide(df[revenue], df[quantity])
        })
    if conversions and visitors:
        metrics.append({
            'name': 'Conversion Rate',
            'formula': f"{conversions} / {visitors} * 100",
            'description': 'Conversions divided by Visitors times 100',
            'apply': lambda df: safe_divide(df[conversions], df[visitors]) * 100
        })
    if revenue and customers:
        metrics.append({
            'name': 'Average Order Value',
            'formula': f"{revenue} / {customers}",
            'description': 'Revenue per Customer',
            'apply': lambda df: safe_divide(df[revenue], df[customers])
        })
    return metrics
