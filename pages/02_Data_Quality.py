import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import datetime
from src.data_quality import compute_quality_report, overall_quality_score, outlier_summary
from src.data_cleaning import remove_duplicates, fill_missing_values, convert_dtype, trim_whitespace, standardize_text_case, replace_values, remove_empty_rows_columns

st.set_page_config(page_title='Data Quality', layout='wide')

if 'analysis_df' not in st.session_state or st.session_state.analysis_df is None:
    st.warning('Please upload a file on the main page first.')
    st.stop()

df = st.session_state.analysis_df

st.title('🔍 Data Quality & Cleaning')

score = overall_quality_score(df)
st.metric('Overall Data Quality Score', f'{score}/100')

st.subheader('Column Quality Report')
quality_df = compute_quality_report(df)
st.dataframe(quality_df, use_container_width=True)

st.subheader('Missing Values')
missing_summary = quality_df[quality_df['Missing Count'] > 0]
if not missing_summary.empty:
    st.dataframe(missing_summary[['Column', 'Missing Count', 'Missing %']], use_container_width=True)
else:
    st.write('No missing values found.')

st.subheader('Duplicate Analysis')
dup_count = int(df.duplicated().sum())
st.write(f'Exact duplicate rows: {dup_count}')
if dup_count > 0:
    if st.button('Remove Duplicates'):
        df_clean, removed = remove_duplicates(df)
        st.session_state.clean_df = df_clean
        st.session_state.analysis_df = df_clean
        st.session_state.audit_log.append(f'{datetime.datetime.now().strftime("%H:%M:%S")} — Removed {removed} duplicate rows')
        st.success(f'Removed {removed} duplicate rows.')
        st.experimental_rerun()

st.subheader('Outlier Analysis (IQR)')
outlier_df = outlier_summary(df)
if not outlier_df.empty:
    st.dataframe(outlier_df, use_container_width=True)
else:
    st.write('No numeric columns for outlier analysis.')

st.subheader('Data Cleaning Operations')
st.info('These operations create a new dataframe. Original data is preserved in session state.')

operation = st.selectbox('Select operation', ['None', 'Fill Missing Values', 'Convert Data Type', 'Trim Whitespace', 'Standardize Text Case', 'Replace Values', 'Remove Empty Rows/Columns'])

if operation == 'Fill Missing Values':
    col = st.selectbox('Column', df.columns)
    method = st.selectbox('Method', ['mean', 'median', 'mode', 'custom'])
    custom_val = None
    if method == 'custom':
        custom_val = st.text_input('Custom value')
        if custom_val:
            try:
                custom_val = pd.to_numeric(custom_val)
            except:
                pass
    if st.button('Apply'):
        try:
            df_clean = fill_missing_values(df, col, method, custom_val)
            st.session_state.clean_df = df_clean
            st.session_state.analysis_df = df_clean
            st.session_state.audit_log.append(f'{datetime.datetime.now().strftime("%H:%M:%S")} — Filled missing values in {col} using {method}')
            st.success(f'Missing values filled in {col}.')
            st.experimental_rerun()
        except Exception as e:
            st.error(f'Error: {e}')

elif operation == 'Convert Data Type':
    col = st.selectbox('Column', df.columns)
    new_type = st.selectbox('New Type', ['datetime', 'numeric', 'categorical', 'text', 'boolean'])
    if st.button('Apply'):
        try:
            df_clean = convert_dtype(df, col, new_type)
            st.session_state.clean_df = df_clean
            st.session_state.analysis_df = df_clean
            st.session_state.audit_log.append(f'{datetime.datetime.now().strftime("%H:%M:%S")} — Converted {col} to {new_type}')
            st.success(f'{col} converted to {new_type}.')
            st.experimental_rerun()
        except Exception as e:
            st.error(f'Error: {e}')

elif operation == 'Trim Whitespace':
    cols = st.multiselect('Columns (optional, default all object cols)', df.columns)
    if st.button('Apply'):
        try:
            df_clean = trim_whitespace(df, cols if cols else None)
            st.session_state.clean_df = df_clean
            st.session_state.analysis_df = df_clean
            st.session_state.audit_log.append(f'{datetime.datetime.now().strftime("%H:%M:%S")} — Trimmed whitespace')
            st.success('Whitespace trimmed.')
            st.experimental_rerun()
        except Exception as e:
            st.error(f'Error: {e}')

elif operation == 'Standardize Text Case':
    col = st.selectbox('Column', df.columns)
    case = st.selectbox('Case', ['lower', 'upper', 'title'])
    if st.button('Apply'):
        try:
            df_clean = standardize_text_case(df, col, case)
            st.session_state.clean_df = df_clean
            st.session_state.analysis_df = df_clean
            st.session_state.audit_log.append(f'{datetime.datetime.now().strftime("%H:%M:%S")} — Standardized case in {col}')
            st.success(f'Case standardized in {col}.')
            st.experimental_rerun()
        except Exception as e:
            st.error(f'Error: {e}')

elif operation == 'Replace Values':
    col = st.selectbox('Column', df.columns)
    old_val = st.text_input('Old value')
    new_val = st.text_input('New value')
    if st.button('Apply'):
        try:
            try:
                old_val = pd.to_numeric(old_val)
                new_val = pd.to_numeric(new_val)
            except:
                pass
            df_clean = replace_values(df, col, old_val, new_val)
            st.session_state.clean_df = df_clean
            st.session_state.analysis_df = df_clean
            st.session_state.audit_log.append(f'{datetime.datetime.now().strftime("%H:%M:%S")} — Replaced values in {col}')
            st.success(f'Values replaced in {col}.')
            st.experimental_rerun()
        except Exception as e:
            st.error(f'Error: {e}')

elif operation == 'Remove Empty Rows/Columns':
    threshold = st.slider('Missing threshold', 0.0, 1.0, 0.5)
    if st.button('Apply'):
        try:
            df_clean = remove_empty_rows_columns(df, threshold)
            st.session_state.clean_df = df_clean
            st.session_state.analysis_df = df_clean
            st.session_state.audit_log.append(f'{datetime.datetime.now().strftime("%H:%M:%S")} — Removed empty rows/columns with threshold {threshold}')
            st.success('Empty rows/columns removed.')
            st.experimental_rerun()
        except Exception as e:
            st.error(f'Error: {e}')
