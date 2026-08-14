"""Data profiling functions."""
import pandas as pd
import numpy as np
from typing import Dict, Any

def profile_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute basic dataframe profile."""
    profile = {
        'row_count': len(df),
        'column_count': len(df.columns),
        'memory_usage': df.memory_usage(deep=True).sum(),
        'numeric_columns': [],
        'categorical_columns': [],
        'datetime_columns': [],
        'boolean_columns': [],
        'text_columns': [],
        'duplicate_rows': int(df.duplicated().sum()),
        'duplicate_percentage': 100 * df.duplicated().sum() / len(df) if len(df) > 0 else 0,
        'missing_cells': int(df.isna().sum().sum()),
        'missing_percentage': 100 * df.isna().sum().sum() / (df.shape[0] * df.shape[1]) if df.shape[0] > 0 else 0,
        'unique_columns': [],
        'constant_columns': [],
    }
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]) and not pd.api.types.is_bool_dtype(df[col]):
            profile['numeric_columns'].append(col)
        elif pd.api.types.is_bool_dtype(df[col]):
            profile['boolean_columns'].append(col)
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            profile['datetime_columns'].append(col)
        elif pd.api.types.is_object_dtype(df[col]):
            nunique = df[col].nunique(dropna=False)
            if nunique / len(df[col]) < 0.1 and nunique <= 50:
                profile['categorical_columns'].append(col)
            else:
                profile['text_columns'].append(col)
        else:
            profile['categorical_columns'].append(col)
        if df[col].nunique(dropna=False) == 1:
            profile['constant_columns'].append(col)
        if df[col].nunique(dropna=False) == len(df) and len(df) > 1:
            profile['unique_columns'].append(col)
    return profile
