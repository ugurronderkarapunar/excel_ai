"""Column type detection based on content."""
import pandas as pd
import numpy as np
import re
from typing import Dict

def detect_column_types(df: pd.DataFrame) -> Dict[str, str]:
    """Detect column types based on content, not just pandas dtype."""
    type_map = {}
    for col in df.columns:
        type_map[col] = detect_single_column_type(df[col], df.shape[0])
    return type_map

def detect_single_column_type(series: pd.Series, total_rows: int) -> str:
    """Detect type of a single column."""
    sample = series.dropna()
    if len(sample) == 0:
        return 'Unknown'
    if pd.api.types.is_bool_dtype(series):
        return 'Boolean'
    if pd.api.types.is_datetime64_any_dtype(series):
        return 'Datetime'
    numeric_sample = pd.to_numeric(sample, errors='coerce')
    if numeric_sample.notna().sum() / len(sample) > 0.9:
        if series.nunique() == len(series) and total_rows > 10:
            if series.dtype == 'object':
                return 'ID'
            elif series.nunique() > 0.9 * total_rows:
                return 'ID' if pd.api.types.is_integer_dtype(series) else 'Numeric'
            else:
                return 'Numeric'
        else:
            return 'Numeric'
    datetime_sample = pd.to_datetime(sample, errors='coerce')
    if datetime_sample.notna().sum() / len(sample) > 0.8:
        return 'Datetime'
    str_sample = sample.astype(str)
    if str_sample.str.contains(r'[£$€₺]|\d+[\.,]\d+\s?[A-Z]{1,3}').sum() / len(sample) > 0.5:
        return 'Currency'
    if str_sample.str.contains(r'\d+[\.,]\d+\s?%|%\s?\d+').sum() / len(sample) > 0.5:
        return 'Percentage'
    nunique = series.nunique()
    if nunique / total_rows < 0.1 and nunique <= 100:
        return 'Categorical'
    if nunique == total_rows and total_rows > 10:
        return 'ID'
    if nunique > 100:
        return 'Text'
    return 'Categorical'
