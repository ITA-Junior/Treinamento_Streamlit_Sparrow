import os
import datetime
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client

# 1. Carrega as variáveis salvas no arquivo .env
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# 2. Configuração visual da página do Streamlit
st.set_page_config(page_title='Curso Python ITA Júnior 2026', page_icon='🐍', layout='wide')

# 3. Valida as variáveis de ambiente antes de criar o cliente
if not SUPABASE_URL or not SUPABASE_KEY:
    st.title('🚀 Entregável Streamlit + Supabase')
    st.subheader('Curso de Python ITA Júnior 2026')
    st.write('---')
    st.error('As variáveis SUPABASE_URL e SUPABASE_KEY não foram encontradas no arquivo .env.')
    st.write('Crie um arquivo .env com essas variáveis e reinicie o app.')
    st.stop()

# 4. Inicializa o cliente de conexão com o banco
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title('🚀 Entregável Streamlit + Supabase')
st.subheader('Curso de Python ITA Júnior 2026')

st.write('---')

tabelas_disponiveis = ['Orders', 'People', 'Returns']
selected_table = st.sidebar.selectbox('📌 Escolha a tabela Supabase', tabelas_disponiveis, index=0)
rows_to_show = st.sidebar.slider('Linhas exibidas', min_value=10, max_value=300, value=100, step=10)

st.sidebar.write('---')
st.sidebar.markdown('## Filtros específicos')

# 5. Funções de utilidade
def get_distinct_values(table_name: str, column_name: str):
    try:
        response = supabase.table(table_name).select(column_name).execute()
        if response.data:
            values = sorted({row.get(column_name) for row in response.data if row.get(column_name) not in (None, '')})
            return values
    except Exception:
        pass
    return []


def get_table_count(table_name: str):
    try:
        result = supabase.table(table_name).select('*', count='exact').limit(1).execute()
        return result.count or 0
    except Exception:
        return None


def format_date(value: datetime.date):
    return value.strftime('%Y-%m-%d')


# 6. Exibe resumo das tabelas
table_counts = {name: get_table_count(name) for name in tabelas_disponiveis}

with st.expander('📊 Estado das tabelas do Supabase', expanded=True):
    for name, count in table_counts.items():
        if count is None:
            st.warning(f'Tabela {name}: não foi possível consultar o número de registros.')
        else:
            st.success(f'Tabela {name}: {count} registros encontrados')

st.write('---')

# 7. Filtros por tabela
if selected_table == 'Orders':
    st.sidebar.markdown('### Orders')
    ship_modes = get_distinct_values('Orders', 'Ship Mode') or ['Standard Class', 'Second Class', 'First Class', 'Same Day']
    segments = get_distinct_values('Orders', 'Segment') or ['Consumer', 'Corporate', 'Home Office']
    regions = get_distinct_values('Orders', 'Region') or ['West', 'East', 'Central', 'South']
    categories = get_distinct_values('Orders', 'Category') or ['Furniture', 'Office Supplies', 'Technology']
    sub_categories = get_distinct_values('Orders', 'Sub-Category')
    countries = get_distinct_values('Orders', 'Country')

    order_date_range = st.sidebar.date_input(
        'Período de Order Date',
        [datetime.date(2016, 1, 1), datetime.date(2017, 12, 31)],
        key='order_date_range'
    )
    use_ship_date = st.sidebar.checkbox('Filtrar por Ship Date', value=False)
    ship_date_range = None
    if use_ship_date:
        ship_date_range = st.sidebar.date_input(
            'Período de Ship Date',
            [datetime.date(2016, 1, 1), datetime.date(2017, 12, 31)],
            key='ship_date_range'
        )

    selected_ship_modes = st.sidebar.multiselect('Ship Mode', ship_modes, default=ship_modes)
    selected_segments = st.sidebar.multiselect('Segment', segments, default=segments)
    selected_regions = st.sidebar.multiselect('Region', regions, default=regions)
    selected_categories = st.sidebar.multiselect('Category', categories, default=categories)
    selected_sub_categories = st.sidebar.multiselect('Sub-Category', sub_categories, default=sub_categories)
    selected_countries = st.sidebar.multiselect('Country', countries, default=countries)
    order_id_filter = st.sidebar.text_input('Order ID')
    customer_filter = st.sidebar.text_input('Customer Name')
    product_filter = st.sidebar.text_input('Product Name')
    min_sales = st.sidebar.number_input('Sales mínimo', value=0.0, step=1.0)
    max_sales = st.sidebar.number_input('Sales máximo', value=10000.0, step=1.0)
    min_profit = st.sidebar.number_input('Profit mínimo', value=-10000.0, step=1.0)
    max_profit = st.sidebar.number_input('Profit máximo', value=10000.0, step=1.0)

    # Build a select builder and a separate count builder (count is only accepted when set on initial select)
    def apply_order_filters(builder):
        if selected_ship_modes:
            builder = builder.in_('Ship Mode', selected_ship_modes)
        if selected_segments:
            builder = builder.in_('Segment', selected_segments)
        if selected_regions:
            builder = builder.in_('Region', selected_regions)
        if selected_categories:
            builder = builder.in_('Category', selected_categories)
        if selected_sub_categories:
            builder = builder.in_('Sub-Category', selected_sub_categories)
        if selected_countries:
            builder = builder.in_('Country', selected_countries)
        if order_id_filter:
            builder = builder.ilike('Order ID', f'%{order_id_filter}%')
        if customer_filter:
            builder = builder.ilike('Customer Name', f'%{customer_filter}%')
        if product_filter:
            builder = builder.ilike('Product Name', f'%{product_filter}%')
        builder = builder.gte('Sales', min_sales).lte('Sales', max_sales)
        builder = builder.gte('Profit', min_profit).lte('Profit', max_profit)
        return builder

    select_builder = supabase.table('Orders').select('*')
    select_builder = apply_order_filters(select_builder)

    # For exact total count of filtered rows, build a separate select with count='exact'
    count_builder = supabase.table('Orders').select('*', count='exact')
    count_builder = apply_order_filters(count_builder)

    def parse_order_date(value):
        if not value:
            return None
        for fmt in ('%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d'):
            try:
                return datetime.datetime.strptime(value, fmt).date()
            except Exception:
                continue
        return None

    def filter_order_rows(rows):
        filtered = []
        for row in rows:
            order_date = parse_order_date(row.get('Order Date'))
            ship_date = parse_order_date(row.get('Ship Date'))
            if order_date_range and len(order_date_range) == 2:
                if order_date is None:
                    continue
                if order_date < order_date_range[0] or order_date > order_date_range[1]:
                    continue
            if ship_date_range and len(ship_date_range) == 2:
                if ship_date is None:
                    continue
                if ship_date < ship_date_range[0] or ship_date > ship_date_range[1]:
                    continue
            filtered.append(row)
        return filtered

elif selected_table == 'People':
    st.sidebar.markdown('### People')
    people_regions = get_distinct_values('People', 'Region') or ['West', 'East', 'Central', 'South']
    selected_people_regions = st.sidebar.multiselect('Region', people_regions, default=people_regions)
    person_search = st.sidebar.text_input('Person')

    query = supabase.table('People').select('*')
    if selected_people_regions:
        query = query.in_('Region', selected_people_regions)
    if person_search:
        query = query.ilike('Person', f'%{person_search}%')

else:
    st.sidebar.markdown('### Returns')
    returned_status = st.sidebar.selectbox('Returned', ['All', 'Yes', 'No'], index=0)
    returns_order_id = st.sidebar.text_input('Order ID')

    query = supabase.table('Returns').select('*')
    if returned_status != 'All':
        query = query.eq('Returned', returned_status)
    if returns_order_id:
        query = query.ilike('Order ID', f'%{returns_order_id}%')

# 8. Execução da consulta
try:
    fetch_limit = rows_to_show if selected_table != 'Orders' else max(rows_to_show, 500)

    if selected_table == 'Orders':
        # execute data query
        response = select_builder.limit(fetch_limit).execute()
        if getattr(response, 'error', None):
            raise Exception(response.error)
        records = response.data or []

        # apply client-side date parsing/filtering when needed
        if 'order_date_range' in locals():
            records = filter_order_rows(records)

        # execute count separately (count='exact' must be provided on the initial select call)
        try:
            count_resp = count_builder.limit(1).execute()
            total_count = getattr(count_resp, 'count', None)
        except Exception:
            total_count = None

        displayed_rows = min(len(records), rows_to_show)

        st.write(f'### Resultados - {selected_table}')
        if total_count is not None:
            st.metric('Registros filtrados (servidor)', total_count)
        else:
            st.metric('Registros filtrados (servidor)', len(records))
        st.metric('Registros exibidos', displayed_rows)

        if records:
            st.dataframe(records[:rows_to_show])
            with st.expander('Ver JSON cru dos resultados', expanded=False):
                st.json(records[:rows_to_show])
        else:
            st.warning('Nenhum registro encontrado com os filtros aplicados.')
            st.info('Ajuste os filtros ou confirme se há dados na tabela selecionada.')

    else:
        # non-orders tables use the common query variable
        response = query.limit(fetch_limit).execute()
        if getattr(response, 'error', None):
            raise Exception(response.error)
        records = response.data or []

        total_rows = len(records)
        displayed_rows = min(total_rows, rows_to_show)

        st.write(f'### Resultados - {selected_table}')
        st.metric('Registros filtrados', total_rows)
        st.metric('Registros exibidos', displayed_rows)

        if records:
            st.dataframe(records[:rows_to_show])
            with st.expander('Ver JSON cru dos resultados', expanded=False):
                st.json(records[:rows_to_show])
        else:
            st.warning('Nenhum registro encontrado com os filtros aplicados.')
            st.info('Ajuste os filtros ou confirme se há dados na tabela selecionada.')

except Exception as erro:
    st.error('Ops, algo deu errado ao consultar o Supabase.')
    st.code(str(erro))
    if 'Could not find the table' in str(erro) or 'PGRST205' in str(erro):
        st.info('A tabela selecionada não foi encontrada. Verifique o nome e o esquema no Supabase.')
    if 'invalid_api_key' in str(erro).lower() or 'authentication' in str(erro).lower():
        st.info('Verifique se a chave SUPABASE_KEY no .env está correta e com permissão de leitura.')
