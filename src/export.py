"""Excel export functions."""
import pandas as pd
from typing import List, Dict, Any
import io

def create_excel_report(
    cleaned_data: pd.DataFrame,
    kpi_summary: pd.DataFrame,
    statistics_summary: pd.DataFrame,
    quality_report: pd.DataFrame,
    correlation_matrix: pd.DataFrame,
    insights: List[Dict[str, Any]],
    grouped_analysis: pd.DataFrame = None,
) -> bytes:
    """Create an Excel report with multiple sheets."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        cleaned_data.to_excel(writer, sheet_name='Cleaned_Data', index=False)
        kpi_summary.to_excel(writer, sheet_name='KPIs', index=False)
        statistics_summary.to_excel(writer, sheet_name='Statistics', index=False)
        quality_report.to_excel(writer, sheet_name='Quality', index=False)
        correlation_matrix.to_excel(writer, sheet_name='Correlations', index=True)
        if grouped_analysis is not None:
            grouped_analysis.to_excel(writer, sheet_name='Grouped_Analysis', index=False)
        insights_df = pd.DataFrame(insights)
        insights_df.to_excel(writer, sheet_name='Insights', index=False)
    return output.getvalue()
