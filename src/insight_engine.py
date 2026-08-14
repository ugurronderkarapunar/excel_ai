"""Automated insight generation based on data."""
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from src.utils import safe_divide
from src.data_quality import overall_quality_score, outlier_summary
from src.segmentation import pareto_analysis

def generate_insights(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Generate automated insights from dataframe."""
    insights = []
    if df.empty:
        return insights

    # Data quality insights
    missing_pct = 100 * df.isna().sum().sum() / (df.shape[0] * df.shape[1])
    if missing_pct > 40:
        insights.append({'severity': 'CRITICAL', 'text': f'Overall missing data rate is {missing_pct:.1f}%. This is extremely high and may affect analysis reliability.'})
    elif missing_pct > 20:
        insights.append({'severity': 'WARNING', 'text': f'Missing data rate is {missing_pct:.1f}%. Consider imputation or careful handling.'})
    elif missing_pct > 5:
        insights.append({'severity': 'INFO', 'text': f'Missing data rate is {missing_pct:.1f}%. Some columns may need attention.'})
    else:
        insights.append({'severity': 'POSITIVE', 'text': f'Data completeness is excellent. Only {missing_pct:.1f}% missing overall.'})

    duplicate_pct = 100 * df.duplicated().sum() / len(df)
    if duplicate_pct > 10:
        insights.append({'severity': 'WARNING', 'text': f'Duplicate rows account for {duplicate_pct:.1f}% of data. Consider removing duplicates.'})
    elif duplicate_pct > 0:
        insights.append({'severity': 'INFO', 'text': f'There are {duplicate_pct:.1f}% duplicate rows.'})

    # Outlier insights
    outlier_df = outlier_summary(df)
    if not outlier_df.empty:
        high_outlier_cols = outlier_df[outlier_df['Outlier %'] > 5]
        for _, row in high_outlier_cols.iterrows():
            insights.append({'severity': 'WARNING', 'text': f"Column '{row['Column']}' has {row['Outlier %']:.1f}% outliers, which may skew analysis."})

    # Numeric columns
    numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col]) and not pd.api.types.is_bool_dtype(df[col])]
    date_cols = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]

    # Time trend insights
    if date_cols and numeric_cols:
        date_col = date_cols[0]
        value_col = numeric_cols[0]
        df_sorted = df.sort_values(date_col)
        mid = len(df_sorted) // 2
        if mid > 1:
            prev = df_sorted[value_col].iloc[:mid].sum()
            curr = df_sorted[value_col].iloc[mid:].sum()
            growth = safe_divide(curr - prev, prev, default=np.nan) * 100
            if pd.notna(growth):
                if growth > 5:
                    insights.append({'severity': 'POSITIVE', 'text': f'{value_col} increased by {growth:.1f}% in the second half compared to the first half.'})
                elif growth < -5:
                    insights.append({'severity': 'WARNING', 'text': f'{value_col} decreased by {abs(growth):.1f}% in the second half compared to the first half.'})
                else:
                    insights.append({'severity': 'INFO', 'text': f'{value_col} remained relatively stable between periods (change: {growth:.1f}%).'})

    # Correlation insights
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr()
        for i in range(len(numeric_cols)):
            for j in range(i+1, len(numeric_cols)):
                r = corr.iloc[i, j]
                if abs(r) > 0.7:
                    direction = 'positive' if r > 0 else 'negative'
                    insights.append({'severity': 'INFO', 'text': f'Strong {direction} correlation between {numeric_cols[i]} and {numeric_cols[j]} (r={r:.2f}).'})

    # Categorical concentration insights
    cat_cols = [col for col in df.columns if pd.api.types.is_object_dtype(df[col]) or (pd.api.types.is_integer_dtype(df[col]) and df[col].nunique() < 50)]
    for cat in cat_cols:
        if numeric_cols:
            value_col = numeric_cols[0]
            pareto = pareto_analysis(df, cat, value_col)
            if not pareto.empty:
                top_cat = pareto.iloc[0]
                if top_cat['Cumulative Percentage'] > 70:
                    insights.append({'severity': 'INFO', 'text': f"Category '{top_cat['Category']}' from '{cat}' contributes {top_cat['Percentage']:.1f}% of {value_col}, indicating high concentration."})

    quality_score = overall_quality_score(df)
    if quality_score < 50:
        insights.append({'severity': 'CRITICAL', 'text': f'Overall data quality score is {quality_score}/100. Significant issues present.'})
    elif quality_score < 80:
        insights.append({'severity': 'WARNING', 'text': f'Overall data quality score is {quality_score}/100. Some improvements recommended.'})
    else:
        insights.append({'severity': 'POSITIVE', 'text': f'Overall data quality score is {quality_score}/100. Data is in good condition.'})

    return insights
