"""Data loading functions for Excel and CSV files."""
import pandas as pd
from typing import List, Optional

def load_excel(file, sheet_name: Optional[str] = None) -> pd.DataFrame:
    """Load Excel file, optionally selecting a sheet."""
    try:
        if sheet_name and sheet_name != 'All':
            df = pd.read_excel(file, sheet_name=sheet_name)
        else:
            xls = pd.ExcelFile(file)
            sheet_names = xls.sheet_names
            if len(sheet_names) == 1:
                df = pd.read_excel(file, sheet_name=sheet_names[0])
            else:
                df = pd.read_excel(file, sheet_name=sheet_names[0])
        return df
    except Exception as e:
        raise ValueError(f"Error reading Excel file: {e}")

def get_excel_sheets(file) -> List[str]:
    """Return list of sheet names from an uploaded Excel file."""
    try:
        xls = pd.ExcelFile(file)
        return xls.sheet_names
    except Exception:
        return []

def load_csv(file, encodings: List[str] = ['utf-8', 'latin-1', 'iso-8859-9', 'cp1254', 'cp1252']) -> pd.DataFrame:
    """Load CSV file with encoding fallback."""
    last_error = None
    for enc in encodings:
        try:
            df = pd.read_csv(file, encoding=enc)
            return df
        except UnicodeDecodeError as e:
            last_error = e
            continue
        except Exception as e:
            last_error = e
            continue
    raise ValueError(f"Could not read CSV with any encoding. Last error: {last_error}")
