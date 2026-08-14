"""Utility functions for data analysis."""
import pandas as pd
import numpy as np
from typing import List, Optional, Any

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero or NaN."""
    try:
        if denominator == 0 or pd.isna(denominator) or np.isinf(denominator):
            return default
        result = numerator / denominator
        if pd.isna(result) or np.isinf(result):
            return default
        return result
    except (TypeError, ZeroDivisionError):
        return default

def optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Optimize dataframe dtypes to reduce memory usage."""
    result = df.copy()
    for col in result.columns:
        col_type = result[col].dtype
        if col_type != object:
            c_min = result[col].min()
            c_max = result[col].max()
            if str(col_type)[:3] == 'int':
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    result[col] = result[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    result[col] = result[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    result[col] = result[col].astype(np.int32)
                else:
                    result[col] = result[col].astype(np.int64)
            elif str(col_type)[:5] == 'float':
                if c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    result[col] = result[col].astype(np.float32)
                else:
                    result[col] = result[col].astype(np.float64)
        else:
            nunique = result[col].nunique(dropna=False)
            if nunique / len(result[col]) < 0.5:
                result[col] = result[col].astype('category')
    return result

def get_numeric_columns(df: pd.DataFrame) -> List[str]:
    """Return list of numeric column names."""
    return [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col]) and not pd.api.types.is_bool_dtype(df[col])]

def get_categorical_columns(df: pd.DataFrame) -> List[str]:
    """Return list of categorical columns."""
    cats = []
    for col in df.columns:
        if pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_categorical_dtype(df[col]):
            cats.append(col)
        elif pd.api.types.is_integer_dtype(df[col]) and df[col].nunique() < 50:
            cats.append(col)
    return cats
