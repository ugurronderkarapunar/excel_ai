"""Segmentation, Pareto and ABC analysis."""
import pandas as pd
import numpy as np
from typing import Optional

def quantile_segments(series: pd.Series) -> pd.Series:
    """Assign segments based on quantiles."""
    def segment(x):
        if x >= series.quantile(0.9):
            return 'Top 10%'
        elif x >= series.quantile(0.75):
            return 'Top 25%'
        elif x >= series.quantile(0.5):
            return 'Middle 50%'
        else:
            return 'Bottom 25%'
    return series.apply(segment)

def pareto_analysis(df: pd.DataFrame, category_col: str, value_col: str) -> pd.DataFrame:
    """Perform Pareto analysis (80/20) on a categorical vs numeric column."""
    grouped = df.groupby(category_col)[value_col].sum().sort_values(ascending=False)
    total = grouped.sum()
    cumsum = grouped.cumsum()
    cum_pct = 100 * cumsum / total
    pct = 100 * grouped / total
    result = pd.DataFrame({
        'Category': grouped.index,
        'Value': grouped.values,
        'Percentage': pct.values,
        'Cumulative Percentage': cum_pct.values
    })
    return result

def abc_analysis(df: pd.DataFrame, category_col: str, value_col: str, a_threshold: float = 0.8, b_threshold: float = 0.15) -> pd.DataFrame:
    """Perform ABC analysis based on cumulative contribution."""
    pareto = pareto_analysis(df, category_col, value_col)
    pareto['ABC'] = 'C'
    pareto.loc[pareto['Cumulative Percentage'] <= a_threshold * 100, 'ABC'] = 'A'
    pareto.loc[(pareto['Cumulative Percentage'] > a_threshold * 100) & (pareto['Cumulative Percentage'] <= (a_threshold + b_threshold) * 100), 'ABC'] = 'B'
    return pareto
