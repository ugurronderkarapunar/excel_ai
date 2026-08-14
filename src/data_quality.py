"""Data quality metrics and scoring."""
import pandas as pd
import numpy as np
from typing import Any

def compute_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """Compute column-level quality report."""
    report = []
    for col in df.columns:
        series = df[col]
        missing = series.isna().sum()
        missing_pct = 100 * missing / len(df) if len(df) > 0 else 0
        nunique = series.nunique(dropna=True)
        unique_pct = 100 * nunique / len(df) if len(df) > 0 else 0
        duplicate_col = series.duplicated().sum()
        zero_count = int((series == 0).sum()) if pd.api.types.is_numeric_dtype(series) else 0
        negative_count = int((series < 0).sum()) if pd.api.types.is_numeric_dtype(series) else 0
        stats = {}
        if pd.api.types.is_numeric_dtype(series):
            stats['min'] = series.min()
            stats['max'] = series.max()
            stats['mean'] = series.mean()
            stats['median'] = series.median()
        else:
            stats['min'] = None
            stats['max'] = None
            stats['mean'] = None
            stats['median'] = None
        report.append({
            'Column': col,
            'Data Type': str(series.dtype),
            'Missing Count': missing,
            'Missing %': round(missing_pct, 2),
            'Unique Count': nunique,
            'Unique %': round(unique_pct, 2),
            'Duplicate Count': duplicate_col,
            'Zero Count': zero_count,
            'Negative Count': negative_count,
            'Min': stats['min'],
            'Max': stats['max'],
            'Mean': stats['mean'],
            'Median': stats['median'],
        })
    return pd.DataFrame(report)

def overall_quality_score(df: pd.DataFrame) -> int:
    """Compute an overall data quality score (0-100)."""
    if df.empty:
        return 0
    score = 100
    missing_pct = 100 * df.isna().sum().sum() / (df.shape[0] * df.shape[1])
    score -= min(30, missing_pct * 2)
    dup_pct = 100 * df.duplicated().sum() / len(df)
    score -= min(10, dup_pct * 0.5)
    constant_cols = [col for col in df.columns if df[col].nunique(dropna=False) <= 1]
    score -= len(constant_cols) * 2
    text_cols = [col for col in df.columns if pd.api.types.is_object_dtype(df[col]) and df[col].nunique() > 0.9 * len(df)]
    score -= len(text_cols) * 2
    numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col]) and not pd.api.types.is_bool_dtype(df[col])]
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        if IQR > 0:
            outlier_count = ((df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)).sum()
            outlier_pct = 100 * outlier_count / len(df)
            score -= min(5, outlier_pct / 10)
    return max(0, min(100, int(score)))

def outlier_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Compute outlier summary for numeric columns using IQR."""
    numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col]) and not pd.api.types.is_bool_dtype(df[col])]
    rows = []
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        outliers = (df[col] < lower) | (df[col] > upper)
        count = int(outliers.sum())
        pct = 100 * count / len(df)
        rows.append({
            'Column': col,
            'Q1': Q1,
            'Q3': Q3,
            'IQR': IQR,
            'Lower Bound': lower,
            'Upper Bound': upper,
            'Outlier Count': count,
            'Outlier %': round(pct, 2)
        })
    return pd.DataFrame(rows)
