import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from src.profiler import profile_dataframe
from src.data_quality import overall_quality_score

st.set_page_config(page_title='Overview', layout='wide')

if 'analysis_df' not in st.session_state or st.session_state.analysis_df is None:
    st.warning('Please upload a file on the main page first.')
    st.stop()

df = st.session_state.analysis_df
profile = profile_dataframe(df)

st.title('📋 Dataset Overview')

col1, col2, col3, col4 = st.columns(4)
col1.metric('Rows', f'{profile["row_count"]:,}')
col2.metric('Columns', profile['column_count'])
col3.metric('Memory Usage', f'{profile["memory_usage"]/1024/1024:.2f} MB')
col4.metric('Data Quality Score', f'{overall_quality_score(df)}/100')

st.subheader('Data Composition')
col_a, col_b = st.columns(2)
with col_a:
    st.write('Numeric columns:', len(profile['numeric_columns']))
    st.write('Categorical columns:', len(profile['categorical_columns']))
    st.write('Datetime columns:', len(profile['datetime_columns']))
with col_b:
    st.write('Boolean columns:', len(profile['boolean_columns']))
    st.write('Text columns:', len(profile['text_columns']))
    st.write('Constant columns:', len(profile['constant_columns']))

st.subheader('Detected Column Types')
types = st.session_state.data_types
type_df = pd.DataFrame(list(types.items()), columns=['Column', 'Detected Type'])
st.dataframe(type_df, use_container_width=True)

st.subheader('First 5 Rows')
st.dataframe(df.head(), use_container_width=True)
