"""Time series analysis functions."""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from src.utils import safe_divide

def extract_time_features(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """Extract time-based features from a datetime column."""
    df = df.copy()
    dates = pd.to_datetime(df[date_col])
    df['Year'] = dates.dt.year
    df['Quarter'] = dates.dt.quarter
    df['Month'] = dates.dt.month
    df['Week'] = dates.dt.isocalendar().week.astype(int)
    df['Day'] = dates.dt.day
    df['Day of Week'] = dates.dt.dayofweek
    df['Day Name'] = dates.dt.day_name()
    df['Hour'] = dates.dt.hour
    return df

def aggregate_time_series(df: pd.DataFrame, date_col: str, value_col: str, freq: str = 'M') -> pd.DataFrame:
    """Aggregate a value column by time frequency."""
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col)
    resampled = df[value_col].resample(freq).sum()
    return resampled.reset_index()

def compute_growth(series: pd.Series, periods: int = 1) -> pd.Series:
    """Compute percentage growth over periods."""
    return series.pct_change(periods=periods) * 100

def compare_periods(df: pd.DataFrame, date_col: str, value_col: str, current_start, current_end, previous_start, previous_end) -> Dict[str, Any]:
    """Compare two time periods."""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    current = df[(df[date_col] >= current_start) & (df[date_col] <= current_end)]
    previous = df[(df[date_col] >= previous_start) & (df[date_col] <= previous_end)]
    current_sum = current[value_col].sum()
    previous_sum = previous[value_col].sum()
    change = current_sum - previous_sum
    pct_change = safe_divide(change, previous_sum, default=np.nan) * 100
    return {
        'current_period': (current_start, current_end),
        'previous_period': (previous_start, previous_end),
        'current_total': current_sum,
        'previous_total': previous_sum,
        'change': change,
        'pct_change': pct_change,
    }

def compute_seasonal_stats(df: pd.DataFrame, date_col: str, value_col: str, period_col: str = 'Month') -> pd.DataFrame:
    """Compute average and total for a given period (e.g., Month, Day of Week)."""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    if period_col == 'Month':
        df['period'] = df[date_col].dt.month
    elif period_col == 'Day of Week':
        df['period'] = df[date_col].dt.day_name()
    elif period_col == 'Hour':
        df['period'] = df[date_col].dt.hour
    elif period_col == 'Quarter':
        df['period'] = df[date_col].dt.quarter
    else:
        df['period'] = df[date_col].dt.year
    grouped = df.groupby('period')[value_col].agg(['mean', 'sum', 'count']).reset_index()
    return grouped
