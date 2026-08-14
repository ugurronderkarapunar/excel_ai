import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from src.relationship_analysis import pearson_correlation, spearman_correlation, correlation_matrix
from src.statistics import t_test, mannwhitneyu_test, anova_test, kruskal_wallis_test, chi_square_test
from src.visualization import heatmap, scatter_plot, box_plot
from src.utils import get_numeric_columns, get_categorical_columns

st.set_page_config(page_title='Relationships', layout='wide')

if 'analysis_df' not in st.session_state or st.session_state.analysis_df is None:
    st.warning('Please upload a file on the main page first.')
    st.stop()

df = st.session_state.analysis_df

st.title('🔗 Relationship Analysis')

numeric_cols = get_numeric_columns(df)
cat_cols = get_categorical_columns(df)

if len(numeric_cols) >= 2:
    st.subheader('Correlation Matrix')
    method = st.selectbox('Correlation method', ['pearson', 'spearman'])
    corr = correlation_matrix(df, numeric_cols, method)
    fig = heatmap(corr)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader('Pairwise Correlation')
    col1, col2 = st.columns(2)
    with col1:
        var1 = st.selectbox('Variable 1', numeric_cols)
    with col2:
        var2 = st.selectbox('Variable 2', numeric_cols)
    pearson = pearson_correlation(df[var1], df[var2])
    spearman = spearman_correlation(df[var1], df[var2])
    st.write('**Pearson:**', pearson)
    st.write('**Spearman:**', spearman)
    fig = scatter_plot(df, var1, var2, title=f'{var1} vs {var2}')
    st.plotly_chart(fig, use_container_width=True)

if cat_cols and numeric_cols:
    st.subheader('Categorical vs Numeric Analysis')
    cat = st.selectbox('Categorical variable', cat_cols)
    num = st.selectbox('Numeric variable', numeric_cols)
    groups = [group[num].dropna() for name, group in df.groupby(cat)]
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
    fig = box_plot(df, y=num, x=cat, title=f'{num} by {cat}')
    st.plotly_chart(fig, use_container_width=True)

if len(cat_cols) >= 2:
    st.subheader('Categorical vs Categorical Analysis')
    cat1 = st.selectbox('First categorical', cat_cols, key='c1')
    cat2 = st.selectbox('Second categorical', cat_cols, key='c2')
    contingency = pd.crosstab(df[cat1], df[cat2])
    st.dataframe(contingency, use_container_width=True)
    result = chi_square_test(contingency)
    st.write(result)
