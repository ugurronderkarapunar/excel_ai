"""Plotly visualization functions."""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Optional

def sample_dataframe(df: pd.DataFrame, max_rows: int = 50000) -> pd.DataFrame:
    """Sample dataframe for visualization."""
    if len(df) <= max_rows:
        return df
    return df.sample(n=max_rows, random_state=42)

def bar_chart(df: pd.DataFrame, x: str, y: str, color: Optional[str] = None, title: str = '') -> go.Figure:
    fig = px.bar(df, x=x, y=y, color=color, title=title)
    fig.update_layout(template='plotly_white')
    return fig

def line_chart(df: pd.DataFrame, x: str, y: str, color: Optional[str] = None, title: str = '') -> go.Figure:
    fig = px.line(df, x=x, y=y, color=color, title=title)
    fig.update_layout(template='plotly_white')
    return fig

def scatter_plot(df: pd.DataFrame, x: str, y: str, color: Optional[str] = None, title: str = '') -> go.Figure:
    fig = px.scatter(df, x=x, y=y, color=color, title=title)
    fig.update_layout(template='plotly_white')
    return fig

def histogram(df: pd.DataFrame, x: str, nbins: int = 30, title: str = '') -> go.Figure:
    fig = px.histogram(df, x=x, nbins=nbins, title=title)
    fig.update_layout(template='plotly_white')
    return fig

def box_plot(df: pd.DataFrame, y: str, x: Optional[str] = None, title: str = '') -> go.Figure:
    fig = px.box(df, x=x, y=y, title=title)
    fig.update_layout(template='plotly_white')
    return fig

def violin_plot(df: pd.DataFrame, y: str, x: Optional[str] = None, title: str = '') -> go.Figure:
    fig = px.violin(df, x=x, y=y, box=True, points='outliers', title=title)
    fig.update_layout(template='plotly_white')
    return fig

def heatmap(corr_matrix: pd.DataFrame, title: str = 'Correlation Heatmap') -> go.Figure:
    fig = px.imshow(corr_matrix, text_auto=True, aspect='auto', color_continuous_scale='RdBu_r', zmin=-1, zmax=1, title=title)
    fig.update_layout(template='plotly_white')
    return fig

def pareto_chart(pareto_df: pd.DataFrame, category_col: str = 'Category', value_col: str = 'Value', title: str = 'Pareto Chart') -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(x=pareto_df[category_col], y=pareto_df[value_col], name='Value'))
    fig.add_trace(go.Scatter(x=pareto_df[category_col], y=pareto_df['Cumulative Percentage'], name='Cumulative %', yaxis='y2', mode='lines+markers'))
    fig.update_layout(
        title=title,
        yaxis=dict(title='Value'),
        yaxis2=dict(title='Cumulative %', overlaying='y', side='right'),
        template='plotly_white'
    )
    return fig
