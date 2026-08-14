import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from src.insight_engine import generate_insights
from src.export import create_excel_report
from src.kpi_engine import discover_kpis
from src.data_quality import compute_quality_report
from src.relationship_analysis import correlation_matrix
from src.utils import get_numeric_columns

st.set_page_config(page_title='Report', layout='wide')

if 'analysis_df' not in st.session_state or st.session_state.analysis_df is None:
    st.warning('Please upload a file on the main page first.')
    st.stop()

df = st.session_state.analysis_df

st.title('📄 Executive Report & Export')

# Insights
st.subheader('Automated Insights')
insights = generate_insights(df)
for ins in insights:
    if ins['severity'] == 'POSITIVE':
        st.success(ins['text'])
    elif ins['severity'] == 'WARNING':
        st.warning(ins['text'])
    elif ins['severity'] == 'CRITICAL':
        st.error(ins['text'])
    else:
        st.info(ins['text'])

# KPI summary
st.subheader('Key Performance Indicators')
kpis = discover_kpis(df)
if kpis:
    kpi_df = pd.DataFrame(kpis)
    st.dataframe(kpi_df, use_container_width=True)

# Export
st.subheader('Export Report')
if st.button('Generate Excel Report'):
    quality = compute_quality_report(df)
    corr = correlation_matrix(df, get_numeric_columns(df))
    kpi_summary = pd.DataFrame(kpis)
    stats_summary = df.describe(include='all').T
    excel_bytes = create_excel_report(
        cleaned_data=df,
        kpi_summary=kpi_summary,
        statistics_summary=stats_summary,
        quality_report=quality,
        correlation_matrix=corr,
        insights=insights
    )
    st.download_button(
        label='Download Excel Report',
        data=excel_bytes,
        file_name='automated_data_analysis_report.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# Audit log
if 'audit_log' in st.session_state and st.session_state.audit_log:
    st.subheader('Audit Log')
    for log in st.session_state.audit_log:
        st.write(log)
