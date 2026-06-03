"""
Visualization module for Superstore Streamlit Dashboard.
Contains Matplotlib and Seaborn chart functions for all business questions.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime

# Set default style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("muted")


def plot_sales_by_date(df: pd.DataFrame) -> plt.Figure:
    """
    Question 2: Total sales by order date (bar chart).
    Aggregates by week if too many days, by day otherwise.
    """
    # Aggregate by Order Date
    sales_by_date = df.groupby('Order Date')['Sales'].sum().sort_index()
    
    # If more than 50 days, aggregate by week for readability
    if len(sales_by_date) > 50:
        df_temp = df.copy()
        df_temp['Week'] = df_temp['Order Date'].dt.to_period('W')
        sales_by_date = df_temp.groupby('Week')['Sales'].sum()
        sales_by_date.index = sales_by_date.index.to_timestamp()
    
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.bar(range(len(sales_by_date)), sales_by_date.values, color='steelblue')
    ax.set_xlabel('Order Date', fontsize=11, fontweight='bold')
    ax.set_ylabel('Total Sales ($)', fontsize=11, fontweight='bold')
    ax.set_title('Total de Vendas por Data do Pedido', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # Format x-axis with readable dates
    step = max(1, len(sales_by_date) // 10)
    ax.set_xticks(range(0, len(sales_by_date), step))
    date_labels = [str(d.date()) for d in sales_by_date.index[::step]]
    ax.set_xticklabels(date_labels, rotation=45, ha='right')
    
    plt.tight_layout()
    return fig


def plot_sales_by_state(df: pd.DataFrame) -> plt.Figure:
    """
    Question 3: Total sales by state (horizontal bar chart).
    """
    sales_by_state = df.groupby('State')['Sales'].sum().sort_values()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(range(len(sales_by_state)), sales_by_state.values, color='coral')
    ax.set_yticks(range(len(sales_by_state)))
    ax.set_yticklabels(sales_by_state.index)
    ax.set_xlabel('Total Sales ($)', fontsize=11, fontweight='bold')
    ax.set_title('Total de Vendas por Estado', fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_top_10_cities(df: pd.DataFrame) -> plt.Figure:
    """
    Question 4: Top 10 cities by total sales (bar chart).
    """
    sales_by_city = df.groupby('City')['Sales'].sum().nlargest(10).sort_values()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(range(len(sales_by_city)), sales_by_city.values, color='seagreen')
    
    # Add value annotations on top of bars
    for i, (idx, val) in enumerate(zip(range(len(sales_by_city)), sales_by_city.values)):
        ax.text(idx, val, f'${val:.0f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    ax.set_xticks(range(len(sales_by_city)))
    ax.set_xticklabels(sales_by_city.index, rotation=45, ha='right')
    ax.set_ylabel('Total Sales ($)', fontsize=11, fontweight='bold')
    ax.set_title('Top 10 Cidades com Maior Total de Vendas', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_segment_sales_pie(df: pd.DataFrame) -> plt.Figure:
    """
    Question 5: Total sales by segment (pie chart).
    """
    sales_by_segment = df.groupby('Segment')['Sales'].sum()
    
    fig, ax = plt.subplots(figsize=(8, 7))
    
    # Find the segment with max sales for explosion
    max_idx = sales_by_segment.idxmax()
    explode = [0.1 if seg == max_idx else 0 for seg in sales_by_segment.index]
    
    colors = sns.color_palette("Set2", len(sales_by_segment))
    ax.pie(
        sales_by_segment.values,
        labels=sales_by_segment.index,
        autopct='%1.1f%%',
        explode=explode,
        colors=colors,
        startangle=90
    )
    ax.set_title('Total de Vendas por Segmento', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    return fig


def plot_sales_by_segment_year(df: pd.DataFrame) -> plt.Figure:
    """
    Question 6: Total sales by segment and year (grouped bar chart).
    Returns a table and a visualization.
    """
    df_temp = df.copy()
    df_temp['Year'] = df_temp['Order Date'].dt.year
    
    sales_by_seg_year = df_temp.groupby(['Segment', 'Year'])['Sales'].sum().reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    segments = sales_by_seg_year['Segment'].unique()
    years = sorted(sales_by_seg_year['Year'].unique())
    
    x = range(len(segments))
    width = 0.25
    
    colors = sns.color_palette("muted", len(years))
    
    for i, year in enumerate(years):
        data = sales_by_seg_year[sales_by_seg_year['Year'] == year].sort_values('Segment')
        ax.bar(
            [xi + i * width for xi in x],
            data['Sales'].values,
            width,
            label=str(year),
            color=colors[i]
        )
    
    ax.set_xlabel('Segment', fontsize=11, fontweight='bold')
    ax.set_ylabel('Total Sales ($)', fontsize=11, fontweight='bold')
    ax.set_title('Total de Vendas por Segmento e por Ano', fontsize=14, fontweight='bold')
    ax.set_xticks([xi + width for xi in x])
    ax.set_xticklabels(segments)
    ax.legend(title='Year')
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_sales_per_segment_month(df: pd.DataFrame) -> plt.Figure:
    """
    Question 9: Average sales by segment, year, and month (line chart).
    """
    df_temp = df.copy()
    df_temp['Year'] = df_temp['Order Date'].dt.year
    df_temp['Month'] = df_temp['Order Date'].dt.month
    df_temp['YearMonth'] = df_temp['Order Date'].dt.strftime('%Y-%m')
    
    avg_sales = df_temp.groupby(['YearMonth', 'Segment'])['Sales'].mean().reset_index()
    avg_sales = avg_sales.sort_values('YearMonth')
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    for segment in avg_sales['Segment'].unique():
        data = avg_sales[avg_sales['Segment'] == segment]
        ax.plot(
            data['YearMonth'],
            data['Sales'],
            marker='o',
            label=segment,
            linewidth=2,
            markersize=6
        )
    
    ax.set_xlabel('Period (YYYY-MM)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Average Sales ($)', fontsize=11, fontweight='bold')
    ax.set_title('Média de Vendas por Segmento, Ano e Mês', fontsize=14, fontweight='bold')
    ax.legend(title='Segment')
    ax.grid(True, alpha=0.3)
    
    # Rotate x-axis labels
    step = max(1, len(avg_sales['YearMonth'].unique()) // 10)
    ax.set_xticks(range(0, len(avg_sales['YearMonth'].unique()), step))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    return fig


def plot_top_12_subcategories(df: pd.DataFrame) -> plt.Figure:
    """
    Question 10: Total sales by category and top 12 sub-categories (horizontal bar chart).
    """
    # Get top 12 subcategories by total sales
    top_12_subs = df.groupby('Sub-Category')['Sales'].sum().nlargest(12).index.tolist()
    df_filtered = df[df['Sub-Category'].isin(top_12_subs)]
    
    # Group by category and sub-category
    sales_by_subcat = df_filtered.groupby(['Category', 'Sub-Category'])['Sales'].sum().sort_values()
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create color mapping for categories
    categories = sales_by_subcat.index.get_level_values('Category').unique()
    color_map = dict(zip(categories, sns.color_palette("Set2", len(categories))))
    colors = [color_map[cat] for cat, _ in sales_by_subcat.index]
    
    bars = ax.barh(range(len(sales_by_subcat)), sales_by_subcat.values, color=colors)
    
    # Add value annotations
    for i, val in enumerate(sales_by_subcat.values):
        ax.text(val, i, f'  ${val:.0f}', va='center', fontweight='bold', fontsize=9)
    
    ax.set_yticks(range(len(sales_by_subcat)))
    ax.set_yticklabels([sub for _, sub in sales_by_subcat.index])
    ax.set_xlabel('Total Sales ($)', fontsize=11, fontweight='bold')
    ax.set_title('Total de Vendas por Categoria e Top 12 Subcategorias', fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=color_map[cat], label=cat) for cat in categories]
    ax.legend(handles=legend_elements, loc='lower right', title='Category')
    
    plt.tight_layout()
    return fig
