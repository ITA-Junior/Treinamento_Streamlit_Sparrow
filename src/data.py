"""
Data loading and processing module for Superstore Streamlit Dashboard.
Handles database queries with filters and data cleaning.
"""

import os
import pandas as pd
import streamlit as st
from supabase import create_client, Client
from datetime import datetime
from typing import Optional, List


def get_supabase_client() -> Client:
    """Initialize and return Supabase client."""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL e SUPABASE_KEY não estão configuradas no .env")
    
    return create_client(supabase_url, supabase_key)


@st.cache_data(ttl=600)
def load_orders(
    date_range: Optional[tuple] = None,
    regions: Optional[List[str]] = None,
    states: Optional[List[str]] = None,
    cities: Optional[List[str]] = None,
    segments: Optional[List[str]] = None,
    categories: Optional[List[str]] = None,
    sub_categories: Optional[List[str]] = None,
    ship_modes: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Load and clean orders data from Supabase with applied filters.
    
    Args:
        date_range: tuple of (start_date, end_date) for Order Date filtering
        regions: list of regions to include
        states: list of states to include
        cities: list of cities to include
        segments: list of segments (Consumer, Corporate, Home Office)
        categories: list of categories (Furniture, Office Supplies, Technology)
        sub_categories: list of sub-categories
        ship_modes: list of ship modes (Standard Class, Second Class, etc.)
    
    Returns:
        pd.DataFrame: Cleaned and filtered orders data
    """
    try:
        supabase = get_supabase_client()
        
        # Build query with filters
        query = supabase.table('Orders').select('*')
        
        if regions:
            query = query.in_('Region', regions)
        if states:
            query = query.in_('State', states)
        if cities:
            query = query.in_('City', cities)
        if segments:
            query = query.in_('Segment', segments)
        if categories:
            query = query.in_('Category', categories)
        if sub_categories:
            query = query.in_('Sub-Category', sub_categories)
        if ship_modes:
            query = query.in_('Ship Mode', ship_modes)
        
        # Execute query (fetch all matching records)
        response = query.execute()
        
        if not response.data:
            return pd.DataFrame()
        
        df = pd.DataFrame(response.data)
        
        # Data type conversions and cleaning
        if 'Order Date' in df.columns:
            df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
        
        if 'Ship Date' in df.columns:
            df['Ship Date'] = pd.to_datetime(df['Ship Date'], errors='coerce')
        
        numeric_cols = ['Sales', 'Discount', 'Profit', 'Quantity']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Apply date range filter (client-side since server may not support date comparisons)
        if date_range and len(date_range) == 2:
            start_date, end_date = date_range
            if pd.notna(start_date) and pd.notna(end_date):
                df = df[
                    (df['Order Date'] >= pd.Timestamp(start_date)) &
                    (df['Order Date'] <= pd.Timestamp(end_date))
                ]
        
        # Remove rows with critical null values
        critical_cols = ['Order Date', 'Sales', 'Category']
        df = df.dropna(subset=[col for col in critical_cols if col in df.columns])
        
        return df.reset_index(drop=True)
    
    except Exception as e:
        st.error(f"Erro ao carregar dados do Supabase: {str(e)}")
        return pd.DataFrame()


def get_distinct_values(table_name: str, column_name: str) -> List[str]:
    """Fetch distinct values for a column from Supabase."""
    try:
        supabase = get_supabase_client()
        response = supabase.table(table_name).select(column_name).execute()
        
        if response.data:
            values = []
            for row in response.data:
                if isinstance(row, dict) and column_name in row:
                    val = row.get(column_name)
                    if val not in (None, ''):
                        values.append(str(val))
            return sorted(list(set(values)))
    except Exception:
        pass
    
    return []


def get_table_count(table_name: str) -> Optional[int]:
    """Get total count of records in a table."""
    try:
        supabase = get_supabase_client()
        result = supabase.table(table_name).select('*').limit(1).execute()
        return len(result.data) if result.data else 0
    except Exception:
        return None
