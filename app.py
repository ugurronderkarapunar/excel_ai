
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Proje kök dizinini Python modül arama yoluna ekle
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import pandas as pd
from src.data_loader import load_excel, load_csv, get_excel_sheets
from src.profiler import profile_dataframe
from src.type_detection import detect_column_types
from src.data_quality import overall_quality_score
from src.utils import optimize_dataframe

st.set_page_config(page_title='Automated Data Analyst', layout='wide', page_icon='📊')

# Initialize session state
if 'raw_df' not in st.session_state:
    st.session_state.raw_df = None
if 'clean_df' not in st.session_state:
    st.session_state.clean_df = None
if 'analysis_df' not in st.session_state:
    st.session_state.analysis_df = None
if 'audit_log' not in st.session_state:
    st.session_state.audit_log = []
if 'data_types' not in st.session_state:
    st.session_state.data_types = {}
if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = None

st.title('📊 Automated Data Analyst')
st.markdown('Upload your Excel or CSV file to begin automated analysis.')

uploaded_file = st.file_uploader('Choose a file', type=['xlsx', 'xls', 'csv'])

if uploaded_file is not None:
    try:
        file_name = uploaded_file.name
        # Reset state if new file uploaded
        if st.session_state.uploaded_file_name != file_name:
            st.session_state.raw_df = None
            st.session_state.clean_df = None
            st.session_state.analysis_df = None
            st.session_state.audit_log = []
            st.session_state.data_types = {}
            st.session_state.uploaded_file_name = file_name

        with st.spinner('Loading file...'):
            if file_name.endswith(('.xlsx', '.xls')):
                sheets = get_excel_sheets(uploaded_file)
                if len(sheets) > 1:
                    sheet = st.selectbox('Select sheet', sheets)
                    df = load_excel(uploaded_file, sheet)
                else:
                    df = load_excel(uploaded_file)
            else:
                df = load_csv(uploaded_file)

        if df.empty:
            st.error('The file is empty.')
            st.stop()

        df = optimize_dataframe(df)
        st.session_state.raw_df = df.copy()
        st.session_state.clean_df = df.copy()
        st.session_state.analysis_df = df.copy()
        st.session_state.data_types = detect_column_types(df)

        st.success(f'Loaded {len(df):,} rows and {len(df.columns)} columns.')

        # Show basic profile
        profile = profile_dataframe(df)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric('Rows', f'{profile["row_count"]:,}')
        col2.metric('Columns', profile['column_count'])
        col3.metric('Missing Cells', f'{profile["missing_cells"]:,}')
        col4.metric('Duplicate Rows', f'{profile["duplicate_rows"]:,}')

        # Data type overview
        st.subheader('Detected Column Types')
        type_counts = {}
        for t in st.session_state.data_types.values():
            type_counts[t] = type_counts.get(t, 0) + 1
        st.write(type_counts)

        st.subheader('Data Preview')
        st.dataframe(df.head(100), use_container_width=True)

    except Exception as e:
        st.error(f'An error occurred while loading the file: {e}')
else:
    st.info('Please upload a file to begin.')
