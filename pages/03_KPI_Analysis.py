import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from src.kpi_engine import calculate_kpis, discover_kpis
from src.utils import get_numeric_columns

st.set_page_config(page_title='KPI Analysis', layout='wide')

if 'analysis_df' not in st.session_state or st.session_state.analysis_df is None:
    st.warning('Please upload a file on the main page first.')
    st.stop()

df = st.session_state.analysis_df

st.title('📈 KPI Analysis')

numeric_cols = get_numeric_columns(df)
if not numeric_cols:
    st.warning('No numeric columns found for KPI analysis.')
    st.stop()

# Discover KPIs
st.subheader('Auto-Discovered KPIs')
kpi_list = discover_kpis(df)
if kpi_list:
    kpi_df = pd.DataFrame(kpi_list)
    st.dataframe(kpi_df, use_container_width=True)
else:
    st.write('No KPIs discovered.')

# Manual KPI summary
st.subheader('KPI Summary by Column')
kpi_summary = calculate_kpis(df, numeric_cols)
st.dataframe(kpi_summary, use_container_width=True)

# Groupby Analysis
st.subheader('GroupBy Analysis')
cat_cols = [col for col in df.columns if df[col].dtype == 'object' or df[col].dtype.name == 'category' or (pd.api.types.is_integer_dtype(df[col]) and df[col].nunique() < 50)]
if cat_cols:
    group_col = st.selectbox('Group by', cat_cols)
    value_col = st.selectbox('Value column', numeric_cols)
    agg_func = st.selectbox('Aggregation', ['sum', 'mean', 'median', 'min', 'max', 'count'])
    if group_col and value_col:
        grouped = df.groupby(group_col)[value_col].agg(agg_func).reset_index()
        st.dataframe(grouped, use_container_width=True)
        st.bar_chart(grouped.set_index(group_col)[value_col])
else:
    st.write('No categorical columns for grouping.')
