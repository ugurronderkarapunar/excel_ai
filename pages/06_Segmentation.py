import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from src.segmentation import quantile_segments, pareto_analysis, abc_analysis
from src.visualization import pareto_chart
from src.utils import get_numeric_columns, get_categorical_columns

st.set_page_config(page_title='Segmentation', layout='wide')

if 'analysis_df' not in st.session_state or st.session_state.analysis_df is None:
    st.warning('Please upload a file on the main page first.')
    st.stop()

df = st.session_state.analysis_df

st.title('🔖 Segmentation & Pareto Analysis')

numeric_cols = get_numeric_columns(df)
cat_cols = get_categorical_columns(df)

if not numeric_cols:
    st.warning('No numeric columns for segmentation.')
    st.stop()

# Quantile segmentation on numeric columns
st.subheader('Quantile Segmentation')
seg_col = st.selectbox('Numeric column to segment', numeric_cols)
segmented = quantile_segments(df[seg_col])
seg_df = df.copy()
seg_df['Segment'] = segmented
segment_counts = seg_df['Segment'].value_counts().reset_index()
segment_counts.columns = ['Segment', 'Count']
st.dataframe(segment_counts, use_container_width=True)

# Pareto analysis
st.subheader('Pareto Analysis (80/20)')
if cat_cols:
    pareto_cat = st.selectbox('Category column', cat_cols)
    pareto_val = st.selectbox('Value column', numeric_cols)
    pareto_df = pareto_analysis(df, pareto_cat, pareto_val)
    st.dataframe(pareto_df, use_container_width=True)
    fig = pareto_chart(pareto_df, title=f'Pareto Chart: {pareto_val} by {pareto_cat}')
    st.plotly_chart(fig, use_container_width=True)

# ABC analysis
st.subheader('ABC Analysis')
if cat_cols:
    abc_cat = st.selectbox('Category column for ABC', cat_cols)
    abc_val = st.selectbox('Value column for ABC', numeric_cols)
    a_thresh = st.slider('A threshold (cumulative %)', 0.0, 1.0, 0.8)
    b_thresh = st.slider('B threshold (cumulative %)', 0.0, 1.0, 0.15)
    abc_df = abc_analysis(df, abc_cat, abc_val, a_thresh, b_thresh)
    st.dataframe(abc_df, use_container_width=True)
