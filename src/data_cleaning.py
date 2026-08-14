"""Data cleaning operations."""
import pandas as pd
import numpy as np
from typing import Optional, List, Any

def remove_duplicates(df: pd.DataFrame, subset: Optional[List[str]] = None) -> tuple:
    """Remove duplicate rows. Returns (df_clean, rows_removed)."""
    before = len(df)
    if subset:
        df_clean = df.drop_duplicates(subset=subset)
    else:
        df_clean = df.drop_duplicates()
    after = len(df_clean)
    return df_clean, before - after

def fill_missing_values(df: pd.DataFrame, column: str, method: str = 'mean', value: Any = None) -> pd.DataFrame:
    """Fill missing values in a column."""
    df_clean = df.copy()
    if method == 'mean':
        df_clean[column] = df_clean[column].fillna(df_clean[column].mean())
    elif method == 'median':
        df_clean[column] = df_clean[column].fillna(df_clean[column].median())
    elif method == 'mode':
        mode_val = df_clean[column].mode()[0] if not df_clean[column].mode().empty else None
        df_clean[column] = df_clean[column].fillna(mode_val)
    elif method == 'custom':
        df_clean[column] = df_clean[column].fillna(value)
    return df_clean

def convert_dtype(df: pd.DataFrame, column: str, new_type: str) -> pd.DataFrame:
    """Convert column to a new dtype."""
    df_clean = df.copy()
    if new_type == 'datetime':
        df_clean[column] = pd.to_datetime(df_clean[column], errors='coerce')
    elif new_type == 'numeric':
        df_clean[column] = pd.to_numeric(df_clean[column], errors='coerce')
    elif new_type == 'categorical':
        df_clean[column] = df_clean[column].astype('category')
    elif new_type == 'text':
        df_clean[column] = df_clean[column].astype(str)
    elif new_type == 'boolean':
        df_clean[column] = df_clean[column].astype(bool)
    return df_clean

def trim_whitespace(df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """Trim whitespace from string columns."""
    df_clean = df.copy()
    if columns is None:
        columns = [col for col in df.columns if pd.api.types.is_object_dtype(df[col])]
    for col in columns:
        df_clean[col] = df_clean[col].str.strip()
    return df_clean

def standardize_text_case(df: pd.DataFrame, column: str, case: str = 'lower') -> pd.DataFrame:
    """Standardize text case."""
    df_clean = df.copy()
    if case == 'lower':
        df_clean[column] = df_clean[column].str.lower()
    elif case == 'upper':
        df_clean[column] = df_clean[column].str.upper()
    elif case == 'title':
        df_clean[column] = df_clean[column].str.title()
    return df_clean

def replace_values(df: pd.DataFrame, column: str, old_value: Any, new_value: Any) -> pd.DataFrame:
    """Replace values in a column."""
    df_clean = df.copy()
    df_clean[column] = df_clean[column].replace(old_value, new_value)
    return df_clean

def remove_empty_rows_columns(df: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
    """Remove rows and columns with excessive missing values."""
    df_clean = df.copy()
    row_thresh = int(df_clean.shape[1] * threshold)
    df_clean = df_clean.dropna(axis=0, thresh=row_thresh)
    col_thresh = int(df_clean.shape[0] * threshold)
    df_clean = df_clean.dropna(axis=1, thresh=col_thresh)
    return df_clean
