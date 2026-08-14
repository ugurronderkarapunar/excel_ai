"""Correlation and relationship analysis."""
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any, List

def pearson_correlation(series1: pd.Series, series2: pd.Series) -> Dict[str, Any]:
    """Compute Pearson correlation."""
    r, p = stats.pearsonr(series1.dropna(), series2.dropna())
    return {
        'method': 'Pearson',
        'correlation': r,
        'p_value': p,
        'strength': interpret_correlation(r),
        'direction': 'Positive' if r > 0 else 'Negative'
    }

def spearman_correlation(series1: pd.Series, series2: pd.Series) -> Dict[str, Any]:
    """Compute Spearman correlation."""
    rho, p = stats.spearmanr(series1.dropna(), series2.dropna())
    return {
        'method': 'Spearman',
        'correlation': rho,
        'p_value': p,
        'strength': interpret_correlation(rho),
        'direction': 'Positive' if rho > 0 else 'Negative'
    }

def interpret_correlation(r: float) -> str:
    abs_r = abs(r)
    if abs_r < 0.1: return 'Negligible'
    elif abs_r < 0.3: return 'Weak'
    elif abs_r < 0.5: return 'Moderate'
    elif abs_r < 0.7: return 'Strong'
    else: return 'Very Strong'

def correlation_matrix(df: pd.DataFrame, numeric_cols: List[str], method: str = 'pearson') -> pd.DataFrame:
    """Compute correlation matrix."""
    if method == 'pearson':
        corr = df[numeric_cols].corr(method='pearson')
    else:
        corr = df[numeric_cols].corr(method='spearman')
    return corr
