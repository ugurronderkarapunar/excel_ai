import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from src.utils import get_numeric_columns, get_categorical_columns
from src.statistics import t_test, mannwhitneyu_test, anova_test, kruskal_wallis_test, chi_square_test, interpret_effect_size
from src.visualization import histogram, box_plot, violin_plot

st.set_page_config(page_title='Statistics', layout='wide')

if 'analysis_df' not in st.session_state or st.session_state.analysis_df is None:
    st.warning('Please upload a file on the main page first.')
    st.stop()

df = st.session_state.analysis_df

st.title('🧪 Statistical Analysis')

numeric_cols = get_numeric_columns(df)
cat_cols = get_categorical_columns(df)

if numeric_cols:
    st.subheader('Numeric Column Statistics')
    stats_df = df[numeric_cols].describe().T
    stats_df['variance'] = df[numeric_cols].var()
    stats_df['skewness'] = df[numeric_cols].skew()
    stats_df['kurtosis'] = df[numeric_cols].kurtosis()
    stats_df['cv'] = stats_df['std'] / stats_df['mean']
    st.dataframe(stats_df, use_container_width=True)

    # Distribution analysis
    st.subheader('Distribution Analysis')
    selected_col = st.selectbox('Select numeric column', numeric_cols)
    fig1 = histogram(df, selected_col, title=f'Histogram of {selected_col}')
    fig2 = box_plot(df, y=selected_col, title=f'Boxplot of {selected_col}')
    fig3 = violin_plot(df, y=selected_col, title=f'Violin Plot of {selected_col}')
    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)
    st.plotly_chart(fig3, use_container_width=True)

    # Statistical tests
    st.subheader('Statistical Tests')
    if cat_cols:
        test_cat = st.selectbox('Categorical variable for tests', cat_cols)
        test_num = st.selectbox('Numeric variable', numeric_cols)
        groups = [group[test_num].dropna() for name, group in df.groupby(test_cat)]
        if len(groups) == 2:
            t_result = t_test(groups[0], groups[1])
            mw_result = mannwhitneyu_test(groups[0], groups[1])
            st.write('**t-test:**', t_result)
            st.write('**Mann-Whitney U:**', mw_result)
        elif len(groups) > 2:
            anova_result = anova_test(groups)
            kw_result = kruskal_wallis_test(groups)
            st.write('**ANOVA:**', anova_result)
            st.write('**Kruskal-Wallis:**', kw_result)
else:
    st.warning('No numeric columns for statistical analysis.')

if len(cat_cols) >= 2:
    st.subheader('Chi-Square Test')
    cat1 = st.selectbox('First categorical', cat_cols, key='c1')
    cat2 = st.selectbox('Second categorical', cat_cols, key='c2')
    if st.button('Run Chi-Square'):
        contingency = pd.crosstab(df[cat1], df[cat2])
        result = chi_square_test(contingency)
        st.write(result)
