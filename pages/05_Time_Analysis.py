import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.express as px
from src.time_analysis import aggregate_time_series, extract_time_features, compute_seasonal_stats, compute_growth
from src.utils import get_numeric_columns
from src.visualization import line_chart, bar_chart

st.set_page_config(page_title='Time Analysis', layout='wide')

if 'analysis_df' not in st.session_state or st.session_state.analysis_df is None:
    st.warning('Please upload a file on the main page first.')
    st.stop()

df = st.session_state.analysis_df

st.title('⏳ Time Series Analysis')

# Detect datetime columns
date_cols = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
if not date_cols:
    # Try to convert object columns that look like dates
    for col in df.columns:
        if pd.api.types.is_object_dtype(df[col]):
            try:
                pd.to_datetime(df[col])
                date_cols.append(col)
            except:
                pass
if not date_cols:
    st.warning('No datetime column detected. Please convert a column to datetime in Data Quality page.')
    st.stop()

date_col = st.selectbox('Date column', date_cols)
numeric_cols = get_numeric_columns(df)
if not numeric_cols:
    st.warning('No numeric columns for time analysis.')
    st.stop()
value_col = st.selectbox('Value column', numeric_cols)

# Aggregate frequency
freq = st.selectbox('Frequency', ['Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly'])
freq_map = {'Daily': 'D', 'Weekly': 'W', 'Monthly': 'M', 'Quarterly': 'Q', 'Yearly': 'Y'}
agg_df = aggregate_time_series(df.copy(), date_col, value_col, freq_map[freq])

st.subheader('Time Series Trend')
fig = line_chart(agg_df, date_col, value_col, title=f'{value_col} over time ({freq})')
st.plotly_chart(fig, use_container_width=True)

# Growth
st.subheader('Growth')
periods = st.slider('Periods for growth calculation', 1, 12, 1)
agg_df['Growth %'] = compute_growth(agg_df[value_col], periods)
st.dataframe(agg_df[['Date' if 'Date' in agg_df.columns else date_col, value_col, 'Growth %']].tail(10), use_container_width=True)

# Seasonal stats
st.subheader('Seasonal Analysis')
period_type = st.selectbox('Period type', ['Month', 'Day of Week', 'Hour', 'Quarter', 'Year'])
season_stats = compute_seasonal_stats(df.copy(), date_col, value_col, period_type)
st.dataframe(season_stats, use_container_width=True)
if period_type == 'Month':
    fig = bar_chart(season_stats, 'period', 'mean', title=f'Average {value_col} by Month')
    st.plotly_chart(fig, use_container_width=True)
