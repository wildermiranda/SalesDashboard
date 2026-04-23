import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests


# --- Carregamento dos dados ---
try:
    df_query_1 = pd.read_csv("data/query_1.csv")
    df_query_2 = pd.read_csv("data/query_2.csv")
    df_query_3 = pd.read_csv("data/query_3.csv")
    df_query_4 = pd.read_csv("data/query_4.csv")
    df_query_5 = pd.read_csv("data/query_5.csv")
except FileNotFoundError as e:
    st.error(f"**Erro de carregamento:** O arquivo `{e.filename}` não foi encontrado.")
    st.info("Certifique-se de que o arquivo está no diretório correto do projeto.")
    st.stop()




# --- Funções Utilitárias ---

def create_dual_axis_chart(df, x_col, bar_col, line_col, title, bar_name, line_name, bar_hover, line_hover, y1_title, y2_title, y2_range=[0, 100], is_percent=False):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Gráfico de Barras
    fig.add_trace(
        go.Bar(
            x=df[x_col],
            y=df[bar_col],
            name=bar_name,
            marker_color='#CBDCEB',
            marker=dict(cornerradius=5),
            text=df[bar_col],
            texttemplate='%{text:,.0f}',
            textposition="outside",
            hovertemplate=f'{bar_hover}: %{{y:,.0f}}<extra></extra>'
        ),
        secondary_y=False
    )

    # Gráfico de Linha
    line_y = df[line_col] * 100 if is_percent else df[line_col]
    text_template = '%{y:.0f}%' if is_percent else '%{y:.1f}'
    tick_format = ".0%" if is_percent else ".1f"
    
    fig.add_trace(
        go.Scatter(
            x=df[x_col],
            y=line_y,
            name=line_name,
            mode="lines+markers",
            line=dict(color='#6D94C5', width=3),
            texttemplate=text_template,
            hovertemplate=f'{line_hover}: {text_template}<extra></extra>'
        ),
        secondary_y=True
    )

    fig.update_layout(
        title_text=title,
        template="plotly_white",
        hovermode="x unified",
        margin=dict(t=80, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="center", x=0.5, font=dict(size=13)),
    )

    fig.update_xaxes(showspikes=True, spikethickness=1, spikemode="across", spikecolor="#C9CDCF")
    fig.update_yaxes(title_text=y1_title, secondary_y=False, tickformat=",d")
    fig.update_yaxes(title_text=y2_title, secondary_y=True, range=y2_range, showgrid=False, tickformat=tick_format)

    return fig


def create_horizontal_bar_chart(df, x_col, y_col, x_label, y_label, title):
    # Ordenar os dados para que a maior barra apareça no topo
    sorted_values = df.sort_values(by=x_col, ascending=True)

    # 2. Criação do Gráfico com Plotly
    fig = px.bar(
        sorted_values, 
        x=x_col, 
        y=y_col, 
        orientation='h',
        text=x_col,
        labels={x_col: x_label, y_col: y_label},
        title=title
    )

    fig.update_traces(
        marker_color='#CBDCEB',
        texttemplate='%{text}', 
        textposition='outside',
        marker=dict(cornerradius=5),
        cliponaxis=False,
        hovertemplate="%{y}<br>-<br>Total de Vendas: %{x}<extra></extra>",
    )

    fig.update_layout(
        plot_bgcolor='white',
        xaxis_title="",
        yaxis_title="",
        xaxis_showticklabels=False,
        margin=dict(l=150, r=150, t=150, b=150),
        height=600,
        hoverlabel=dict(align="left")
    )

    return fig

def render_query_result(query, df):
    code = query
    st.code(code, language='sql')

    st.write("")
    st.write("")

    st.badge("Data Output", color="green")

    st.dataframe(df, use_container_width=True)





# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Vendas",
    page_icon="📊",
    layout="wide",
)


# --- Layout do Dashboard ---

# --- Título ---
st.title("Dashboard de Vendas")

charts, queries = st.tabs(["Charts", "Queries"])

with charts:
    st.write("")

    # --- Cabeçalho ---
    st.markdown("Explore os principais drivers e indicadores de desempenho.")

    st.write("")

    # --- Gráficos com dois eixos ---
    fig1 = create_dual_axis_chart(
        df_query_1, 'month', 'revenue (k, R$)', 'average ticket (k, R$)',
        "Receita vs Ticket Médio", "Receita (k, R$)", "Ticket Médio (k, R$)", "Receita", "Ticket Médio", "Receita", "Ticket Médio", [0, 100]
    )
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = create_dual_axis_chart(
        df_query_1, 'month', 'leads', 'conversion rate',
        "Leads vs Conversão", "Leads (#)", "Conversão (%)", "Leads", "Conversão", "Leads", "Conversão", [0, 0.25], is_percent=True
    )
    st.plotly_chart(fig2, use_container_width=True)


    # --- Gráfico geográgico ---

    # Carregar os limites geográficos dos estados brasileiros (GeoJSON)
    @st.cache_data
    def get_geojson():
        url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
        return requests.get(url).json()

    brazil_geojson = get_geojson()

    # Lista completa os estádos para garantir que todos apareçam
    brazil_states = [
        'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
        'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 
        'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
    ]

    df_sales_states = pd.DataFrame({'state': brazil_states})
    df_merged_states = pd.merge(df_sales_states, df_query_2, on='state', how='left').fillna(0)

    fig3 = px.choropleth(
        df_merged_states,
        geojson=brazil_geojson,
        locations='state',
        featureidkey="properties.sigla",
        color='sales',
        color_continuous_scale="Blues",
        range_color=(0, df_merged_states['sales'].max()),
        scope="south america",
        labels={'sales': 'Total de Vendas', 'state': 'Estado'},
        title="Estados que mais venderam no mês"
    )

    fig3.update_traces(
        hovertemplate="Estado: %{location}<br>-<br>Total de Vendas: %{z}<extra></extra>"
    )

    # Focar no Brasil e esconder o resto do globo
    fig3.update_geos(
        fitbounds="locations", 
        visible=False,
        projection_type="mercator"
    )

    fig3.update_layout(
            height=700
    )

    st.plotly_chart(fig3, use_container_width=True)


    tab1, tab2, tab3 = st.tabs(["Top 5 marcas mais vendidas no mês", "Top 5 lojas que mais venderam no mês", "Visitas ao site por dia da semana no mês"])
    
    with tab1:
        fig4 = create_horizontal_bar_chart(
            df_query_3, 'sales', 'brand', 'Total de Vendas', 'Marcas', 'Top 5 marcas mais vendidas no mês'
        )

        st.plotly_chart(fig4, use_container_width=True)
    
    with tab2:
        fig5 = create_horizontal_bar_chart(
            df_query_4, 'sales', 'store', 'Total de Vendas', 'Lojas', 'Top 5 lojas que mais venderam no mês'
        )

        st.plotly_chart(fig5, use_container_width=True)

    with tab3:
        fig6 = px.bar(
            df_query_5, 
            x='day_of_week', 
            y='visits',
            text='visits',
            title='Visitas ao site por dia da semana no mês'
        )

        fig6.update_traces(
            marker_color='#CBDCEB',
            marker=dict(cornerradius=5),
            textposition='outside',
            hovertemplate="Dia da semana: %{x}<br>-<br>Total de Visitas: %{y}<extra></extra>"
        )

        fig6.update_layout(
            xaxis_title="",
            yaxis_title="",
            yaxis_showticklabels=False,
            margin=dict(l=150, r=150, t=150, b=150),
            height=600,
            hoverlabel=dict(align="left")
        )

        fig6.update_yaxes(showgrid=False)

        st.plotly_chart(fig6, use_container_width=True)


with queries:
    st.write("")

    st.markdown("Consultas SQL executadas para a extração de dados.")

    st.write("")

    with st.expander("Query 1"):
        render_query_result(
            '''with leads as (
	select
		date_trunc('month', visit_page_date)::date as visit_month,
		count(*) as visit_count
	from sales.funnel
	group by visit_month
	order by visit_month 
	),

	payments as (
		select
			date_trunc('month', f.paid_date)::date as paid_month,
			count(f.paid_date) as paid_count,
			sum(p.price * (1 + f.discount)) as revenue
		from sales.funnel as f
		left join sales.products as p
			on f.product_id = p.product_id
		where f.paid_date is not null
		group by paid_month
		order by paid_month
	)


select
	leads.visit_month as "month",
	leads.visit_count as "leads",
	payments.paid_count as "sales",
	(payments.revenue / 1000) as "revenue (k, R$)",
	(payments.paid_count::float / leads.visit_count::float) as "conversion rate",
	(payments.revenue / payments.paid_count / 1000) as "average ticket (k, R$)"
	
from leads 
left join payments
	on leads.visit_month = payments.paid_month''', 
            df_query_1
        )


    with st.expander("Query 2"):
        render_query_result(
            '''select
	c.state,
	count(f.paid_date) as sales
from sales.funnel as f
left join sales.customers as c
	on f.customer_id = c.customer_id
where paid_date between '2021-08-01' and '2021-08-31'
group by c.state
order by sales desc
limit 5''', 
            df_query_2
        )


    with st.expander("Query 3"):
        render_query_result(
            '''select
    p.brand,
    count(f.paid_date) as sales
from sales.funnel as f
left join sales.products as p
    on f.product_id = p.product_id
where paid_date between '2021-08-01' and '2021-08-31'
group by p.brand
order by sales desc
limit 5''', 
            df_query_3
        )

    with st.expander("Query 4"):
        render_query_result(
            '''select
    s.store_name as store,
    count(f.paid_date) as sales
    from sales.funnel as f
    left join sales.stores as s
    on f.store_id = s.store_id
    where paid_date between '2021-08-01' and '2021-08-31'
    group by s.store_name
    order by sales desc
    limit 5''', 
            df_query_4
        )


    with st.expander("Query 5"):
        render_query_result(
            '''select
	extract('dow' from visit_page_date) as number_of_week,
	case
		when extract('dow' from visit_page_date) = 0 then 'Domingo'
		when extract('dow' from visit_page_date) = 1 then 'Segunda'
		when extract('dow' from visit_page_date) = 2 then 'Terça'
		when extract('dow' from visit_page_date) = 3 then 'Quarta'
		when extract('dow' from visit_page_date) = 4 then 'Quinta'
		when extract('dow' from visit_page_date) = 5 then 'Sexta'
		when extract('dow' from visit_page_date) = 6 then 'Sábado'
		else null end as day_of_week,
	count(*) as visits
from sales.funnel
where visit_page_date between '2021-08-01' and '2021-08-31'
group by number_of_week
order by number_of_week''', 
            df_query_5
        )