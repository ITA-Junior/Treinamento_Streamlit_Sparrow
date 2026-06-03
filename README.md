# 📊 Superstore Dashboard - Streamlit + Supabase

Dashboard interativo de análise de negócios desenvolvido para o **Curso de Python ITA Júnior 2026**. Conecta-se a um banco de dados Supabase (PostgreSQL) e apresenta análises de 10 perguntas de negócio sobre vendas de uma rede de varejo multi-canal (Superstore).

## 🎯 Visão Geral do Projeto

Este aplicativo Streamlit permite exploração interativa do dataset Superstore com:

- **4 abas principais** de navegação estruturadas por tipo de análise
- **Filtros globais** no sidebar que afetam todas as análises
- **10 perguntas de negócio** respondidas com dados, visualizações e insights
- **Visualizações profissionais** usando Matplotlib e Seaborn
- **Exportação de dados** em formato CSV para análises adicionais

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Acesso a um projeto Supabase com a tabela **Orders** (e opcionalmente People e Returns)
- Chave de API Supabase (URL e API Key públicos)

## 🚀 Como Configurar e Executar

### 1. Clonar o Repositório

```bash
git clone <seu-repositorio>
cd Treinamento_Streamlit_Sparrow
```

### 2. Criar Ambiente Virtual

#### No Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### No macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto copiando o modelo:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e substitua com suas credenciais Supabase:

```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_publica_aqui
```

**Onde encontrar:**
1. Acesse seu projeto em [supabase.com](https://supabase.com)
2. Vá para **Project Settings > API**
3. Copie a **Project URL** (URL)
4. Copie a **anon public** key (API Key)

### 5. Executar a Aplicação

```bash
streamlit run app.py
```

A aplicação abrirá no navegador em `http://localhost:8501`

## 🏗️ Arquitetura e Estrutura de Arquivos

```
Treinamento_Streamlit_Sparrow/
│
├── app.py                      # Aplicação principal (4 abas, filtros)
├── requirements.txt            # Dependências Python
├── .env.example               # Template de variáveis de ambiente
├── .env                       # Variáveis de ambiente (NÃO commitar!)
├── .gitignore                 # Ignora arquivos sensíveis
├── README.md                  # Este arquivo
│
└── src/
    ├── __init__.py            # Torna src um módulo Python
    ├── data.py                # Funções de carregamento e limpeza de dados
    └── charts.py              # Funções de visualização (Matplotlib/Seaborn)
```

### Descrição dos Módulos

#### `app.py`
- **Estrutura principal** com navegação em abas
- **Sidebar com filtros globais** (datas, regiões, segmentos, categorias, etc.)
- **4 abas principais**:
  1. **Visão Geral**: Métricas resumidas e preview do dataset
  2. **Perguntas 1–5**: Análises de localização, categoria e segmentação
  3. **Perguntas 6–10**: Análises temporais, simulações e desempenho
  4. **Conclusões & Recomendações**: Insights estratégicos e download de dados

#### `src/data.py`
Responsável por:
- `get_supabase_client()`: Inicializa conexão com Supabase
- `load_orders()`: Carrega e limpa dados com filtros aplicados
  - Converte tipos de dados (datas, números)
  - Remove valores nulos críticos
  - Usa `@st.cache_data()` para performance
- `get_distinct_values()`: Busca valores únicos para filtros
- `get_table_count()`: Obtém contagem de registros

#### `src/charts.py`
Funções de visualização para cada pergunta:
- `plot_sales_by_date()`: Gráfico de barras temporal
- `plot_sales_by_state()`: Gráfico de barras horizontal por estado
- `plot_top_10_cities()`: Top 10 cidades com anotações
- `plot_segment_sales_pie()`: Gráfico de pizza por segmento
- `plot_sales_by_segment_year()`: Barras agrupadas por ano
- `plot_sales_per_segment_month()`: Linhas temporais por segmento
- `plot_top_12_subcategories()`: Top 12 subcategorias com cores

Todas usam:
- **Estilo**: `seaborn-v0_8-whitegrid`
- **Paleta**: `muted`
- **Tamanhos otimizados** para legibilidade

## 📊 As 10 Perguntas de Negócio

### Aba 2: Perguntas 1–5

| # | Pergunta | Tipo | Visualização |
|---|----------|------|--------------|
| 1 | Qual cidade com maior valor de venda em Office Supplies? | Métrica | Tabela |
| 2 | Total de vendas por data do pedido | Série temporal | Barras |
| 3 | Total de vendas por estado | Agregação geográfica | Barras (horizontal) |
| 4 | Top 10 cidades com maior total de vendas | Ranking | Barras com anotações |
| 5 | Segmento com maior total de vendas | Distribuição | Pizza |

### Aba 3: Perguntas 6–10

| # | Pergunta | Tipo | Visualização |
|---|----------|------|--------------|
| 6 | Total de vendas por segmento e por ano | Série temporal + Segmentação | Barras agrupadas + Tabela |
| 7 | Quantas vendas receberiam 15% de desconto? | Simulação (Sales > 1000) | Métricas |
| 8 | Média antes e depois do desconto (15%) | Impacto financeiro | Métricas |
| 9 | Média de vendas por segmento, ano e mês | Série temporal granular | Linhas |
| 10 | Total de vendas por categoria (Top 12 subcategorias) | Ranking com categorização | Barras (horizontal) |

## 🔧 Filtros Globais

No **sidebar**, ajuste os filtros que afetam **todas as abas**:

- **Período de Order Date** (data range picker)
- **Região** (multiselect: West, East, Central, South)
- **Estado** (multiselect: dinâmico)
- **Cidade** (multiselect: dinâmico)
- **Segmento** (multiselect: Consumer, Corporate, Home Office)
- **Categoria** (multiselect: Furniture, Office Supplies, Technology)
- **Subcategoria** (multiselect: dinâmico)
- **Tipo de Envio/Ship Mode** (multiselect)
- **Botão "Limpar Filtros"** para reset

## 💾 Exportar Dados

Na aba **"Conclusões & Recomendações"**, há um botão para baixar os dados filtrados em formato CSV:

```
⬇️ Baixar Dados Filtrados (CSV)
```

O arquivo exportado contém todas as linhas após aplicar os filtros do sidebar.

## 🔒 Segurança

### ✅ Práticas Implementadas

- ✓ Variáveis de ambiente via `python-dotenv`
- ✓ Arquivo `.gitignore` com entrada `.env`
- ✓ `.env.example` com valores vazios para template
- ✓ Credenciais **nunca** commitadas no repositório

### ⚠️ Importante

**NUNCA commite seu arquivo `.env` com credenciais reais!**

Verifique antes de fazer commit:
```bash
git status
```

Se vir `.env`, remova com:
```bash
git rm --cached .env
```

## 📊 Dataset Esperado (Supabase)

### Tabela: Orders

Colunas necessárias:
- `Order ID` (texto) - Identificador do pedido
- `Order Date` (data) - Data do pedido
- `Ship Date` (data) - Data de envio
- `Ship Mode` (texto) - Tipo de envio
- `Customer Name` (texto) - Nome do cliente
- `Segment` (texto) - Consumer, Corporate, Home Office
- `Country` (texto) - País
- `City` (texto) - Cidade
- `State` (texto) - Estado
- `Region` (texto) - Região
- `Product Name` (texto) - Nome do produto
- `Category` (texto) - Categoria (Furniture, Office Supplies, Technology)
- `Sub-Category` (texto) - Subcategoria
- `Sales` (número) - Valor de vendas
- `Quantity` (número) - Quantidade
- `Discount` (número) - Desconto aplicado (0–1)
- `Profit` (número) - Lucro

### Tabelas Opcionais

- **People**: Representantes por região (Region, Person)
- **Returns**: Dados de devoluções (Order ID, Returned status)

## 🐛 Troubleshooting

### Erro: "SUPABASE_URL e SUPABASE_KEY não foram encontradas"
- Verifique se o arquivo `.env` existe na raiz do projeto
- Confirme que as variáveis estão preenchidas
- Reinicie o aplicativo com `Ctrl+C` e `streamlit run app.py`

### Erro: "Could not find the table Orders"
- Verifique o nome exato da tabela no Supabase (case-sensitive)
- Confirme que a tabela está no esquema público

### Erro: "invalid_api_key"
- A API Key pode ter expirado; gere uma nova no Supabase
- Verifique se você está usando a **anon public key** (não secret)

### Gráficos não aparecem
- Verifique se há dados retornados pelos filtros
- Confirme que as colunas necessárias existem no dataset

## 📈 Performance e Otimizações

- **Cache com `@st.cache_data(ttl=600)`**: Dados são cacheados por 10 minutos
- **Lazy loading de gráficos**: Apenas o gráfico visível é renderizado
- **Filtering no Supabase**: Reduz volume de dados transferidos
- **Client-side cleanup**: Remove nulls e converte tipos

## 🎓 Objetivos de Aprendizado (Curso ITA Júnior)

Este projeto demonstra:

✓ Integração com API REST (Supabase)  
✓ Manipulação de dados (Pandas)  
✓ Visualização de dados (Matplotlib + Seaborn)  
✓ Interface web interativa (Streamlit)  
✓ Boas práticas de segurança (variáveis de ambiente)  
✓ Análise de negócio (insights e recomendações)  
✓ Estrutura e modularização de código  
✓ Git e versionamento (GitHub)  

## 📚 Recursos Adicionais

- [Documentação Streamlit](https://docs.streamlit.io)
- [Documentação Supabase](https://supabase.com/docs)
- [Pandas Documentation](https://pandas.pydata.org/docs)
- [Matplotlib Gallery](https://matplotlib.org/stable/gallery/index.html)
- [Seaborn Tutorial](https://seaborn.pydata.org/tutorial.html)

## 📝 Changelog

### v1.0 (Release Inicial)
- ✓ 4 abas de navegação
- ✓ 10 perguntas de negócio implementadas
- ✓ Filtros globais no sidebar
- ✓ Visualizações com Matplotlib/Seaborn
- ✓ Exportação de dados em CSV
- ✓ Sistema de insights e recomendações

## 👥 Autores

Desenvolvido como projeto final do **Curso de Python ITA Júnior 2026**.

## 📄 Licença

Este projeto é fornecido como material educacional.

---

**Última atualização**: Junho de 2026  
**Versão**: 1.0
