"""
Data loading and processing module for Superstore Streamlit Dashboard.
Handles database queries and data cleaning.
"""

import os
import pandas as pd
import streamlit as st
from supabase import create_client, Client
from typing import Optional


def get_supabase_client() -> Client:
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL e SUPABASE_KEY não estão configuradas no .env")

    return create_client(supabase_url, supabase_key)


@st.cache_data(ttl=600)
def load_orders() -> pd.DataFrame:
    """
    Load all orders from Supabase with pagination.
    Filters are applied in the app layer (Python), not here.
    """
    try:
        supabase = get_supabase_client()
        all_data = []
        page_size = 1000
        offset = 0

        while True:
            response = (
                supabase.table('Orders')
                .select('*')
                .range(offset, offset + page_size - 1)
                .execute()
            )
            if not response.data:
                break
            all_data.extend(response.data)
            if len(response.data) < page_size:
                break
            offset += page_size

        if not all_data:
            return pd.DataFrame()

        df = pd.DataFrame(all_data)

        if 'Order Date' in df.columns:
            df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
        if 'Ship Date' in df.columns:
            df['Ship Date'] = pd.to_datetime(df['Ship Date'], errors='coerce')

        numeric_cols = ['Sales', 'Discount', 'Profit', 'Quantity']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        if 'Sales' in df.columns and 'Quantity' in df.columns:
            df['Sales'] = df['Sales'] * df['Quantity']

        critical_cols = ['Order Date', 'Sales', 'Category']
        df = df.dropna(subset=[col for col in critical_cols if col in df.columns])

        return df.reset_index(drop=True)

    except Exception as e:
        st.error(f"Erro ao carregar dados do Supabase: {str(e)}")
        return pd.DataFrame()


def apply_filters(
    df: pd.DataFrame,
    date_range: Optional[tuple] = None,
    regions: Optional[list] = None,
    states: Optional[list] = None,
    cities: Optional[list] = None,
    segments: Optional[list] = None,
    categories: Optional[list] = None,
    sub_categories: Optional[list] = None,
    ship_modes: Optional[list] = None,
) -> pd.DataFrame:
    """Apply sidebar filters to the full dataframe in Python."""
    filtered = df.copy()

    if date_range and len(date_range) == 2:
        start, end = date_range
        if pd.notna(start) and pd.notna(end):
            filtered = filtered[
                (filtered['Order Date'] >= pd.Timestamp(start)) &
                (filtered['Order Date'] <= pd.Timestamp(end))
            ]

    if regions:
        filtered = filtered[filtered['Region'].isin(regions)]
    if states:
        filtered = filtered[filtered['State'].isin(states)]
    if cities:
        filtered = filtered[filtered['City'].isin(cities)]
    if segments:
        filtered = filtered[filtered['Segment'].isin(segments)]
    if categories:
        filtered = filtered[filtered['Category'].isin(categories)]
    if sub_categories:
        filtered = filtered[filtered['Sub-Category'].isin(sub_categories)]
    if ship_modes:
        filtered = filtered[filtered['Ship Mode'].isin(ship_modes)]

    return filtered.reset_index(drop=True)
