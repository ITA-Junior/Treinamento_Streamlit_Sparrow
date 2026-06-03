"""
Superstore Streamlit Dashboard - ITA Júnior 2026 Python Course

A comprehensive business intelligence dashboard connecting to Supabase (PostgreSQL)
with interactive filters and analysis of 10 key business questions.
"""

import os
import datetime
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv

from src import data, charts

# Load environment variables
load_dotenv()

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title='Superstore Dashboard - ITA Júnior 2026',
    page_icon='📊',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Custom CSS for better formatting
st.markdown("""
    <style>
        .metric-container { margin: 10px 0; }
        .insight-box { background-color: #e8f4f8; padding: 15px; border-radius: 8px; margin: 10px 0; }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================

st.title('📊 Superstore Dashboard')
st.subheader('Curso de Python ITA Júnior 2026')
st.markdown('---')

# ============================================================================
# VALIDATE ENVIRONMENT
# ============================================================================

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error('❌ As variáveis SUPABASE_URL e SUPABASE_KEY não foram encontradas no arquivo .env.')
    st.write('Crie um arquivo .env com essas variáveis e reinicie o app.')
    st.stop()

# ============================================================================
# SIDEBAR - GLOBAL FILTERS
# ============================================================================

st.sidebar.markdown('## 🔍 Filtros Globais')
st.sidebar.markdown('Estes filtros afetam todas as abas')

# ============================================================================
# LOAD ALL DATA (unfiltered, cached)
# ============================================================================

df_all = data.load_orders()

if df_all.empty:
    st.error('❌ Nenhum dado encontrado no banco. Verifique a conexão com o Supabase.')
    st.stop()

# Derive filter options from the actual data
def _vals(col):
    return sorted(df_all[col].dropna().unique().tolist()) if col in df_all.columns else []

all_regions       = _vals('Region')
all_states        = _vals('State')
all_cities        = _vals('City')
all_segments      = _vals('Segment')
all_categories    = _vals('Category')
all_sub_categories = _vals('Sub-Category')
all_ship_modes    = _vals('Ship Mode')


def _set_index_starting_at_one(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of the DataFrame with row index starting at 1."""
    df = df.copy()
    df.index = pd.RangeIndex(start=1, stop=len(df) + 1)
    return df

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================

# Date range filter (empty = sem restrição)
date_range = st.sidebar.date_input(
    'Período de Order Date',
    [],
    key='date_range_sidebar'
)

selected_regions = st.sidebar.multiselect(
    'Região (Region)', all_regions, key='regions_filter'
)
selected_states = st.sidebar.multiselect(
    'Estado (State)', all_states, key='states_filter'
)
selected_cities = st.sidebar.multiselect(
    'Cidade (City)', all_cities, key='cities_filter'
)
selected_segments = st.sidebar.multiselect(
    'Segmento (Segment)', all_segments, key='segments_filter'
)
selected_categories = st.sidebar.multiselect(
    'Categoria (Category)', all_categories, key='categories_filter'
)
selected_sub_categories = st.sidebar.multiselect(
    'Subcategoria (Sub-Category)', all_sub_categories, key='sub_categories_filter'
)
selected_ship_modes = st.sidebar.multiselect(
    'Tipo de Envio (Ship Mode)', all_ship_modes, key='ship_modes_filter'
)

st.sidebar.markdown('---')

# Clear filters button
if st.sidebar.button('🔄 Limpar Filtros', use_container_width=True):
    for key in [
        'date_range_sidebar', 'regions_filter', 'states_filter', 'cities_filter',
        'segments_filter', 'categories_filter', 'sub_categories_filter', 'ship_modes_filter'
    ]:
        st.session_state.pop(key, None)
    st.rerun()

# ============================================================================
# APPLY FILTERS IN PYTHON
# ============================================================================

df = data.apply_filters(
    df_all,
    date_range=tuple(date_range) if len(date_range) == 2 else None,
    regions=selected_regions if selected_regions else None,
    states=selected_states if selected_states else None,
    cities=selected_cities if selected_cities else None,
    segments=selected_segments if selected_segments else None,
    categories=selected_categories if selected_categories else None,
    sub_categories=selected_sub_categories if selected_sub_categories else None,
    ship_modes=selected_ship_modes if selected_ship_modes else None,
)

if df.empty:
    st.warning('⚠️ Nenhum dado encontrado com os filtros aplicados. Verifique as seleções no sidebar.')
    st.stop()

# ============================================================================
# MAIN TABS
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "🏠 Visão Geral",
    "📊 Perguntas 1–5",
    "📈 Perguntas 6–10",
    "💡 Conclusões & Recomendações"
])

# ============================================================================
# TAB 1: VISÃO GERAL (OVERVIEW)
# ============================================================================

with tab1:
    st.header('Visão Geral do Dataset')
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric('Total de Pedidos', f'{len(df):,}')
    
    with col2:
        total_sales = df['Sales'].sum()
        st.metric('Total de Vendas', f'${total_sales:,.2f}')
    
    with col3:
        total_profit = df['Profit'].sum()
        st.metric('Lucro Total', f'${total_profit:,.2f}')
    
    with col4:
        avg_sales = df['Sales'].mean()
        st.metric('Ticket Médio', f'${avg_sales:,.2f}')
    
    st.markdown('---')
    
    # Data quality info
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader('📈 Informações do Dataset')
        st.write(f'- **Período**: {df["Order Date"].min().strftime("%d/%m/%Y")} a {df["Order Date"].max().strftime("%d/%m/%Y")}')
        st.write(f'- **Regiões**: {df["Region"].nunique()} únicas')
        st.write(f'- **Estados**: {df["State"].nunique()} únicos')
        st.write(f'- **Cidades**: {df["City"].nunique()} únicas')
        st.write(f'- **Segmentos**: {df["Segment"].nunique()}')
        st.write(f'- **Categorias**: {df["Category"].nunique()}')
        st.write(f'- **Subcategorias**: {df["Sub-Category"].nunique()}')
    
    with col2:
        st.subheader('💹 Estatísticas de Vendas')
        st.write(f'- **Sales Min**: ${df["Sales"].min():,.2f}')
        st.write(f'- **Sales Max**: ${df["Sales"].max():,.2f}')
        st.write(f'- **Sales Mediana**: ${df["Sales"].median():,.2f}')
        st.write(f'- **Profit Min**: ${df["Profit"].min():,.2f}')
        st.write(f'- **Profit Max**: ${df["Profit"].max():,.2f}')
        st.write(f'- **Discount Médio**: {df["Discount"].mean():.2%}')
    
    st.markdown('---')
    
    # Data preview
    st.subheader('Primeiras Linhas do Dataset')
    st.dataframe(
        df.head(20),
        use_container_width=True,
        height=400,
        hide_index=True
    )

# ============================================================================
# TAB 2: PERGUNTAS 1–5
# ============================================================================

with tab2:
    st.header('Análise de Negócio - Perguntas 1 a 5')
    
    # QUESTION 1: City with highest sales for Office Supplies
    st.subheader('❓ Pergunta 1 — Cidade com maior valor de venda em Office Supplies')
    
    office_supplies = df[df['Category'] == 'Office Supplies']
    if not office_supplies.empty:
        sales_by_city = office_supplies.groupby('City')['Sales'].sum().sort_values(ascending=False)
        top_city = sales_by_city.index[0]
        top_sales = sales_by_city.iloc[0]
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.metric('🏆 Cidade Líder', top_city, f'${top_sales:,.2f}')
        with col2:
            st.dataframe(
                _set_index_starting_at_one(
                    sales_by_city.head(5).reset_index().rename(columns={'City': 'Cidade', 'Sales': 'Vendas'})
                ),
                use_container_width=True
            )
        
        st.info('💡 **Insight:** A concentração de vendas de Office Supplies em ' + top_city + 
                ' sugere uma oportunidade para otimizar a logística e expandir para outras cidades com potencial de crescimento.')
    else:
        st.warning('Nenhum dado de Office Supplies encontrado com os filtros aplicados.')
    
    st.divider()
    
    # QUESTION 2: Total sales by order date
    st.subheader('❓ Pergunta 2 — Total de vendas por data do pedido')
    
    try:
        fig = charts.plot_sales_by_date(df)
        st.pyplot(fig)
        plt.close(fig)
        
        st.info('💡 **Insight:** Analise padrões sazonais e picos de vendas para melhor planejamento de estoque e campanhas de marketing.')
    except Exception as e:
        st.error(f'Erro ao gerar gráfico: {str(e)}')
    
    st.divider()
    
    # QUESTION 3: Total sales by state
    st.subheader('❓ Pergunta 3 — Total de vendas por estado')
    
    try:
        fig = charts.plot_sales_by_state(df)
        st.pyplot(fig)
        plt.close(fig)
        
        st.info('💡 **Insight:** Os estados com maiores vendas devem receber atenção especial para retenção e crescimento estratégico.')
    except Exception as e:
        st.error(f'Erro ao gerar gráfico: {str(e)}')
    
    st.divider()
    
    # QUESTION 4: Top 10 cities
    st.subheader('❓ Pergunta 4 — Top 10 cidades com maior total de vendas')
    
    try:
        fig = charts.plot_top_10_cities(df)
        st.pyplot(fig)
        plt.close(fig)
        
        st.info('💡 **Insight:** Concentração urbana é evidente; considere estratégias específicas para cada metrópole.')
    except Exception as e:
        st.error(f'Erro ao gerar gráfico: {str(e)}')
    
    st.divider()
    
    # QUESTION 5: Segment with highest sales
    st.subheader('❓ Pergunta 5 — Segmento com maior total de vendas')
    
    try:
        fig = charts.plot_segment_sales_pie(df)
        st.pyplot(fig)
        plt.close(fig)
        
        sales_by_segment = df.groupby('Segment')['Sales'].sum().sort_values(ascending=False)
        st.dataframe(
            _set_index_starting_at_one(
                sales_by_segment.reset_index().rename(columns={'Segment': 'Segmento', 'Sales': 'Vendas Totais'})
            ),
            use_container_width=True
        )
        
        st.info('💡 **Insight:** O segmento líder merece investimento contínuo, enquanto segmentos menores têm potencial de crescimento com ações direcionadas.')
    except Exception as e:
        st.error(f'Erro ao gerar gráfico: {str(e)}')

# ============================================================================
# TAB 3: PERGUNTAS 6–10
# ============================================================================

with tab3:
    st.header('Análise de Negócio - Perguntas 6 a 10')
    
    # QUESTION 6: Sales by segment and year
    st.subheader('❓ Pergunta 6 — Total de vendas por segmento e por ano')
    
    try:
        df_temp = df.copy()
        df_temp['Year'] = df_temp['Order Date'].dt.year
        sales_pivot = df_temp.pivot_table(
            values='Sales',
            index='Segment',
            columns='Year',
            aggfunc='sum'
        )
        
        st.dataframe(sales_pivot.style.format('${:,.2f}'), use_container_width=True)
        
        fig = charts.plot_sales_by_segment_year(df)
        st.pyplot(fig)
        plt.close(fig)
        
        st.info('💡 **Insight:** Identifique segmentos em crescimento ou declínio para ajustar estratégias comerciais.')
    except Exception as e:
        st.error(f'Erro ao gerar análise: {str(e)}')
    
    st.divider()
    
    # QUESTION 7: Discount simulation (15% vs 10%)
    st.subheader('❓ Pergunta 7 — Simulação de desconto: quantas vendas receberiam 15%?')
    
    try:
        # Apply discount logic: Sales > 1000 → 15%, else → 10%
        df_temp = df.copy()
        df_temp['Discount_Rate'] = df_temp['Sales'].apply(lambda x: 0.15 if x > 1000 else 0.10)
        
        count_15_percent = (df_temp['Discount_Rate'] == 0.15).sum()
        count_10_percent = (df_temp['Discount_Rate'] == 0.10).sum()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric('Vendas com 15% de desconto', count_15_percent)
        with col2:
            st.metric('Vendas com 10% de desconto', count_10_percent)
        with col3:
            percent_15 = (count_15_percent / len(df_temp)) * 100
            st.metric('% de Vendas com 15%', f'{percent_15:.1f}%')
        
        # Summary table
        summary_data = pd.DataFrame({
            'Faixa de Desconto': ['15% (Sales > 1000)', '10% (Sales ≤ 1000)'],
            'Quantidade': [count_15_percent, count_10_percent],
            'Percentual': [f'{(count_15_percent/len(df_temp))*100:.1f}%', 
                          f'{(count_10_percent/len(df_temp))*100:.1f}%']
        })
        
        st.dataframe(summary_data, use_container_width=True, hide_index=True)
        
        st.info('💡 **Insight:** A proporção de transações de alto valor (>$1000) indica a relevância de políticas de desconto diferenciadas.')
    except Exception as e:
        st.error(f'Erro ao gerar simulação: {str(e)}')
    
    st.divider()
    
    # QUESTION 8: Average before and after discount
    st.subheader('❓ Pergunta 8 — Média do valor de venda antes e depois do desconto de 15%')
    
    try:
        df_temp = df.copy()
        df_temp['Discount_Rate'] = df_temp['Sales'].apply(lambda x: 0.15 if x > 1000 else 0.10)
        
        # Only high-value sales (15% discount)
        high_value_sales = df_temp[df_temp['Sales'] > 1000]['Sales']
        
        if not high_value_sales.empty:
            avg_before = high_value_sales.mean()
            avg_after = avg_before * (1 - 0.15)  # 15% discount = 85% of original
            difference = avg_before - avg_after
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric('Média Antes do Desconto', f'${avg_before:,.2f}')
            with col2:
                st.metric('Média Depois do Desconto (15%)', f'${avg_after:,.2f}')
            with col3:
                st.metric('Diferença Média', f'${difference:,.2f}', delta=-f'${difference:,.2f}')
            
            st.info('💡 **Insight:** O desconto de 15% reduz a receita média em ' + f'${difference:,.2f}' + 
                   ', que pode ser compensado pelo aumento no volume de vendas.')
        else:
            st.warning('Nenhuma venda com valor > $1000 encontrada nos filtros aplicados.')
    except Exception as e:
        st.error(f'Erro ao gerar análise: {str(e)}')
    
    st.divider()
    
    # QUESTION 9: Average sales by segment, year, month
    st.subheader('❓ Pergunta 9 — Média de vendas por segmento, por ano e por mês')
    
    try:
        fig = charts.plot_sales_per_segment_month(df)
        st.pyplot(fig)
        plt.close(fig)
        
        st.info('💡 **Insight:** Padrões temporais por segmento ajudam a prever demanda e otimizar recursos.')
    except Exception as e:
        st.error(f'Erro ao gerar gráfico: {str(e)}')
    
    st.divider()
    
    # QUESTION 10: Top 12 sub-categories
    st.subheader('❓ Pergunta 10 — Total de vendas por categoria e subcategoria (Top 12)')
    
    try:
        fig = charts.plot_top_12_subcategories(df)
        st.pyplot(fig)
        plt.close(fig)
        
        # Detail table
        top_12_subs = df.groupby('Sub-Category')['Sales'].sum().nlargest(12).index.tolist()
        df_top12 = df[df['Sub-Category'].isin(top_12_subs)]
        detail_table = df_top12.groupby(['Category', 'Sub-Category']).agg({
            'Sales': 'sum',
            'Order ID': 'count'
        }).rename(columns={'Sales': 'Total Vendas', 'Order ID': 'Num Pedidos'}).sort_values('Total Vendas', ascending=False)
        
        st.dataframe(
            detail_table.style.format({'Total Vendas': '${:,.2f}', 'Num Pedidos': '{:.0f}'}),
            use_container_width=True
        )
        
        st.info('💡 **Insight:** As subcategorias líderes concentram a maioria das receitas; otimize a apresentação e promoção desses produtos.')
    except Exception as e:
        st.error(f'Erro ao gerar gráfico: {str(e)}')

# ============================================================================
# TAB 4: CONCLUSÕES & RECOMENDAÇÕES
# ============================================================================

with tab4:
    st.header('💡 Conclusões & Recomendações')
    
    st.markdown("""
    ## Resumo dos Principais Insights
    
    Com base na análise do dataset Superstore filtrado, identificamos os seguintes pontos-chave:
    
    ### 📌 Insights Principais
    
    1. **Concentração Geográfica**: As vendas estão fortemente concentradas em um pequeno número de cidades 
       e estados, indicando um mercado altamente urbanizado.
    
    2. **Distribuição de Segmentos**: A distribuição entre Consumer, Corporate e Home Office revela 
       oportunidades de crescimento em segmentos menos desenvolvidos.
    
    3. **Padrões Sazonais**: Há evidência de sazonalidade nas vendas, com picos em determinados períodos 
       do ano que demandam preparação logística.
    
    4. **Performance por Categoria**: Algumas categorias e subcategorias são muito mais rentáveis que outras, 
       sugerindo necessidade de alocação diferenciada de recursos.
    
    5. **Impacto de Descontos**: Transações de alto valor (>$1000) representam uma fração significativa 
       do volume, e políticas de desconto devem ser cuidadosamente calibradas.
    
    ---
    
    ## 🎯 Recomendações Estratégicas
    
    ### 1. **Diversificação Geográfica**
       - Expandir presença em cidades e estados com baixa penetração atual
       - Investir em campanhas de marketing direcionadas para regiões emergentes
       - Considerar parcerias locais para reduzir barreiras de entrada
    
    ### 2. **Otimização de Segmentos**
       - Fortalecer segmento líder com programas de fidelização
       - Desenvolver estratégias customizadas para crescimento dos segmentos menores
       - Investigar diferenças nas necessidades e comportamentos de compra por segmento
    
    ### 3. **Gestão de Inventário**
       - Antecipar demanda sazonal com modelos de previsão
       - Concentrar estoque em regiões e épocas de pico
       - Reduzir estoque de produtos sazonais em períodos baixos
    
    ### 4. **Política de Preços e Descontos**
       - Implementar sistema de descontos progressivos baseado em volume
       - Monitorar margem de lucro de forma contínua
       - A/B testar diferentes estratégias de precificação
    
    ### 5. **Racionalização de Portfólio**
       - Focar em subcategorias de alto desempenho
       - Revisar a continuidade de produtos de baixa rentabilidade
       - Diversificar oferta em categorias líderes
    
    ---
    
    ## ⚠️ Limitações dos Dados
    
    Algumas considerações importantes sobre a qualidade e contexto dos dados:
    
    - **Amplitude Temporal**: O dataset atual cobre apenas 2 anos; análises de tendências de longo prazo 
      requerem dados históricos mais extensos.
    
    - **Falta de Contexto Externo**: Não há informações sobre campanha de marketing, eventos econômicos 
      ou ações da concorrência que possam explicar variações sazonais.
    
    - **Dados Demográficos Limitados**: Informações sobre características do cliente além de localização 
      e segmento são escassas, limitando análises de personalização.
    
    - **Possíveis Dados Faltantes**: Podem haver inconsistências ou registros incompletos não detectados 
      nesta análise inicial.
    
    - **Defasagem de Dados**: A análise reflete dados históricos; mudanças recentes no mercado podem não 
      estar capturadas.
    
    ---
    
    ## 📥 Exportar Dados
    
    Baixe o dataset filtrado para análises adicionais em ferramentas externas.
    """)
    
    st.markdown('---')
    
    # Download button
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label='⬇️ Baixar Dados Filtrados (CSV)',
        data=csv_data,
        file_name='superstore_filtrado.csv',
        mime='text/csv',
        use_container_width=True
    )
    
    st.markdown('---')
    st.markdown('**Relatório gerado em**: ' + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

# ============================================================================
# FOOTER
# ============================================================================

st.markdown('---')
st.markdown(
    '📚 Dashboard desenvolvido para o **Curso de Python ITA Júnior 2026** | '
    '🔗 Dados via Supabase | '
    '📊 Visualizações com Matplotlib & Seaborn'
)
