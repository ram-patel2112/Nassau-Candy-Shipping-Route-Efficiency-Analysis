import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nassau Candy – Route Efficiency",
    page_icon="🍬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stSidebar"] { background: #1a1a2e; }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #16213e 100%);
        border-radius: 12px;
        padding: 24px 18px;
        text-align: center;
        border-left: 4px solid #f4a261;
        margin-bottom: 10px;
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .metric-card h2 { color: #f4a261 !important; font-size: 2rem; margin: 0; white-space: nowrap; }
    .metric-card p  { color: #aac4de !important; font-size: 0.95rem; margin: 10px 0 0; }
    .section-header {
        font-size: 1.3rem; font-weight: 700; color: #f4a261;
        border-bottom: 2px solid #f4a261; padding-bottom: 6px; margin: 20px 0 12px;
    }
    .stTabs [data-baseweb="tab"] { font-size: 1rem; font-weight: 600; }
    .stTabs [aria-selected="true"] { color: #f4a261 !important; border-bottom-color: #f4a261 !important; }
</style>
""", unsafe_allow_html=True)

# ─── Factory Maps ────────────────────────────────────────────────────────────
FACTORY_MAP = {
    'Wonka Bar - Nutty Crunch Surprise':    "Lot's O' Nuts",
    'Wonka Bar - Fudge Mallows':            "Lot's O' Nuts",
    "Wonka Bar -Scrumdiddlyumptious":       "Lot's O' Nuts",
    'Wonka Bar - Milk Chocolate':           "Wicked Choccy's",
    'Wonka Bar - Triple Dazzle Caramel':    "Wicked Choccy's",
    'Laffy Taffy':                          'Sugar Shack',
    'SweeTARTS':                            'Sugar Shack',
    'Nerds':                                'Sugar Shack',
    'Fun Dip':                              'Sugar Shack',
    'Fizzy Lifting Drinks':                 'Sugar Shack',
    'Everlasting Gobstopper':               'Secret Factory',
    'Hair Toffee':                          'The Other Factory',
    'Lickable Wallpaper':                   'Secret Factory',
    'Wonka Gum':                            'Secret Factory',
    'Kazookles':                            'The Other Factory',
}

FACTORY_COORDS = {
    "Lot's O' Nuts":      (32.881893, -111.768036),
    "Wicked Choccy's":    (32.076176, -81.088371),
    'Sugar Shack':        (48.11914,  -96.18115),
    'Secret Factory':     (41.446333, -90.565487),
    'The Other Factory':  (35.1175,   -89.971107),
}

FACTORY_COLORS = {
    "Lot's O' Nuts":      '#f4a261',
    "Wicked Choccy's":    '#e76f51',
    'Sugar Shack':        '#2a9d8f',
    'Secret Factory':     '#457b9d',
    'The Other Factory':  '#a8dadc',
}

# ─── Load & Prepare Data ─────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('Nassau Candy Distributor.csv')
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
    df['Ship Date']  = pd.to_datetime(df['Ship Date'],  dayfirst=True)
    df['Lead Time']  = (df['Ship Date'] - df['Order Date']).dt.days
    df['Factory']    = df['Product Name'].map(FACTORY_MAP)
    df['Route']      = df['Factory'] + ' → ' + df['State/Province']
    df['Route_Region'] = df['Factory'] + ' → ' + df['Region']
    # Delay flag: lead time > mean + 1 std
    threshold        = df['Lead Time'].mean() + df['Lead Time'].std()
    df['Delayed']    = df['Lead Time'] > threshold
    df['Order Month'] = df['Order Date'].dt.to_period('M').astype(str)
    return df, threshold

df_raw, DELAY_THRESHOLD = load_data()

# ─── Sidebar Filters ─────────────────────────────────────────────────────────
st.sidebar.markdown("<div style='font-size:2.5rem; text-align:center; margin-bottom: 8px;'>🍬</div>", unsafe_allow_html=True)
st.sidebar.title("Nassau Candy")
st.sidebar.markdown("**Shipping Intelligence Dashboard**")
st.sidebar.markdown("---")

min_date = df_raw['Order Date'].min().date()
max_date = df_raw['Order Date'].max().date()
date_range = st.sidebar.date_input("📅 Order Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

regions    = st.sidebar.multiselect("🗺️ Region", sorted(df_raw['Region'].unique()), default=list(df_raw['Region'].unique()))
ship_modes = st.sidebar.multiselect("🚚 Ship Mode", sorted(df_raw['Ship Mode'].unique()), default=list(df_raw['Ship Mode'].unique()))
factories  = st.sidebar.multiselect("🏭 Factory", sorted(df_raw['Factory'].unique()), default=list(df_raw['Factory'].unique()))
delay_thresh = st.sidebar.slider("⚠️ Delay Threshold (days)", int(df_raw['Lead Time'].min()), int(df_raw['Lead Time'].max()), int(DELAY_THRESHOLD), step=10)

# Apply Filters
if len(date_range) == 2:
    d_start, d_end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    d_start, d_end = pd.Timestamp(min_date), pd.Timestamp(max_date)

df = df_raw[
    (df_raw['Order Date'] >= d_start) &
    (df_raw['Order Date'] <= d_end) &
    (df_raw['Region'].isin(regions)) &
    (df_raw['Ship Mode'].isin(ship_modes)) &
    (df_raw['Factory'].isin(factories))
].copy()
df['Delayed'] = df['Lead Time'] > delay_thresh

st.sidebar.markdown("---")
st.sidebar.markdown(f"**📊 Records:** {len(df):,} / {len(df_raw):,}")

# ─── Main Title ──────────────────────────────────────────────────────────────
st.markdown("## 🍬 Nassau Candy Distributor — Shipping Route Efficiency")
st.markdown("*Factory-to-Customer logistics intelligence across the US supply chain*")

# ─── Tabs ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", "🗺️ Geographic Map", "🚚 Ship Mode", "📦 Route Drill-Down", "📈 Trends"
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 – OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    # KPI Cards
    total_orders    = len(df)
    avg_lead        = df['Lead Time'].mean()
    delay_pct       = df['Delayed'].mean() * 100
    total_revenue   = df['Sales'].sum()
    total_profit    = df['Gross Profit'].sum()
    unique_routes   = df['Route'].nunique()

    c1, c2, c3, c4, c5, c6 = st.columns(6, gap='small')
    for col, val, label in zip(
        [c1, c2, c3, c4, c5, c6],
        [f"{total_orders:,}", f"{avg_lead:.0f} days", f"{delay_pct:.1f}%",
         f"${total_revenue:,.0f}", f"${total_profit:,.0f}", f"{unique_routes:,}"],
        ["Total Orders", "Avg Lead Time", "Delay Rate", "Total Sales", "Gross Profit", "Unique Routes"]
    ):
        col.markdown(f'<div class="metric-card"><h2>{val}</h2><p>{label}</p></div>', unsafe_allow_html=True)

    st.markdown("---")

    col_l, col_r = st.columns(2)

    # Route Efficiency Leaderboard
    with col_l:
        st.markdown('<div class="section-header">🏆 Top 10 Most Efficient Routes</div>', unsafe_allow_html=True)
        route_perf = df.groupby('Route').agg(
            Avg_Lead_Time=('Lead Time', 'mean'),
            Total_Shipments=('Row ID', 'count'),
            Delay_Rate=('Delayed', 'mean'),
        ).reset_index()
        route_perf['Efficiency_Score'] = (
            1 - (route_perf['Avg_Lead_Time'] - route_perf['Avg_Lead_Time'].min()) /
            (route_perf['Avg_Lead_Time'].max() - route_perf['Avg_Lead_Time'].min())
        ) * 100
        top10 = route_perf.nsmallest(10, 'Avg_Lead_Time')
        fig = px.bar(top10, x='Avg_Lead_Time', y='Route', orientation='h',
                     color='Efficiency_Score', color_continuous_scale='Greens',
                     labels={'Avg_Lead_Time': 'Avg Lead Time (days)', 'Route': ''},
                     title="Fastest Routes (lowest avg lead time)")
        fig.update_layout(height=380, margin=dict(l=0, r=10, t=40, b=0),
                          coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        fig.update_xaxes(showgrid=True, gridcolor='#2a2a3a')
        fig.update_yaxes(showgrid=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-header">⚠️ Bottom 10 Least Efficient Routes</div>', unsafe_allow_html=True)
        bot10 = route_perf.nlargest(10, 'Avg_Lead_Time')
        fig2 = px.bar(bot10, x='Avg_Lead_Time', y='Route', orientation='h',
                      color='Delay_Rate', color_continuous_scale='Reds',
                      labels={'Avg_Lead_Time': 'Avg Lead Time (days)', 'Route': ''},
                      title="Slowest Routes (highest avg lead time)")
        fig2.update_layout(height=380, margin=dict(l=0, r=10, t=40, b=0),
                           coloraxis_colorbar=dict(title='Delay Rate'), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        fig2.update_xaxes(showgrid=True, gridcolor='#2a2a3a')
        fig2.update_yaxes(showgrid=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="section-header">🏭 Factory Performance Comparison</div>', unsafe_allow_html=True)
        fac_perf = df.groupby('Factory').agg(
            Avg_Lead=('Lead Time', 'mean'),
            Delay_Rate=('Delayed', 'mean'),
            Volume=('Row ID', 'count'),
        ).reset_index()
        fig3 = px.scatter(fac_perf, x='Avg_Lead', y='Delay_Rate', size='Volume',
                          color='Factory', color_discrete_map={f: FACTORY_COLORS.get(f, '#999') for f in fac_perf['Factory']},
                          labels={'Avg_Lead': 'Avg Lead Time (days)', 'Delay_Rate': 'Delay Rate'},
                          title="Factory: Lead Time vs Delay Rate (bubble = volume)")
        fig3.update_layout(height=340, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        fig3.update_xaxes(showgrid=True, gridcolor='#2a2a3a')
        fig3.update_yaxes(showgrid=True, gridcolor='#2a2a3a', tickformat='.0%')
        st.plotly_chart(fig3, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-header">📦 Division-wise Delay Distribution</div>', unsafe_allow_html=True)
        div_delay = df.groupby(['Division', 'Delayed']).size().reset_index(name='Count')
        div_delay['Status'] = div_delay['Delayed'].map({True: 'Delayed', False: 'On Time'})
        fig4 = px.bar(div_delay, x='Division', y='Count', color='Status',
                      color_discrete_map={'Delayed': '#e76f51', 'On Time': '#2a9d8f'},
                      title="Shipment Status by Product Division", barmode='stack')
        fig4.update_layout(height=340, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        fig4.update_xaxes(showgrid=False)
        fig4.update_yaxes(showgrid=True, gridcolor='#2a2a3a')
        st.plotly_chart(fig4, use_container_width=True)

    # Full Route Leaderboard Table
    st.markdown('<div class="section-header">📋 Full Route Performance Table</div>', unsafe_allow_html=True)
    route_perf['Avg_Lead_Time'] = route_perf['Avg_Lead_Time'].round(1)
    route_perf['Delay_Rate']    = (route_perf['Delay_Rate'] * 100).round(1)
    route_perf['Efficiency_Score'] = route_perf['Efficiency_Score'].round(1)
    route_perf_sorted = route_perf.sort_values('Avg_Lead_Time')
    route_perf_sorted.columns = ['Route', 'Avg Lead Time (days)', 'Total Shipments', 'Delay Rate (%)', 'Efficiency Score']
    st.dataframe(route_perf_sorted, use_container_width=True, height=300)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 – GEOGRAPHIC MAP
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">🗺️ US Shipping Efficiency Heatmap by State</div>', unsafe_allow_html=True)

    state_perf = df.groupby('State/Province').agg(
        Avg_Lead=('Lead Time', 'mean'),
        Volume=('Row ID', 'count'),
        Delay_Rate=('Delayed', 'mean'),
        Total_Sales=('Sales', 'sum'),
    ).reset_index()

    state_abbr = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
        'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
        'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
        'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
        'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
        'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH',
        'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC',
        'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
        'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN',
        'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
        'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY', 'District of Columbia': 'DC',
    }
    state_perf['State_Code'] = state_perf['State/Province'].map(state_abbr)

    metric_choice = st.radio("Color map by:", ["Avg Lead Time", "Delay Rate (%)", "Volume", "Total Sales"], horizontal=True)
    metric_col_map = {
        "Avg Lead Time": ("Avg_Lead", "Reds", "Avg Lead Time (days)"),
        "Delay Rate (%)": ("Delay_Rate", "OrRd", "Delay Rate"),
        "Volume": ("Volume", "Blues", "Shipment Volume"),
        "Total Sales": ("Total_Sales", "Greens", "Total Sales ($)"),
    }
    col_key, cscale, clabel = metric_col_map[metric_choice]
    if col_key == "Delay_Rate":
        state_perf['Display'] = (state_perf['Delay_Rate'] * 100).round(1)
        col_to_use = 'Display'
    else:
        col_to_use = col_key

    fig_map = px.choropleth(
        state_perf, locations='State_Code', locationmode='USA-states',
        color=col_to_use, scope='usa',
        color_continuous_scale=cscale,
        hover_name='State/Province',
        hover_data={
            'State_Code': False,
            'Avg_Lead': ':.1f',
            'Volume': ':,',
            'Delay_Rate': ':.1%',
        },
        labels={col_to_use: clabel},
        title=f"US State-Level: {metric_choice}",
    )
    fig_map.update_layout(
        height=520,
        geo=dict(bgcolor='rgba(0,0,0,0)'),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=50, b=0),
    )
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown('<div class="section-header">📍 Factory Locations</div>', unsafe_allow_html=True)
    factory_df = pd.DataFrame([
        {'Factory': f, 'Lat': c[0], 'Lon': c[1],
         'Orders': len(df[df['Factory'] == f]),
         'Avg Lead': round(df[df['Factory'] == f]['Lead Time'].mean(), 1) if f in df['Factory'].values else 0}
        for f, c in FACTORY_COORDS.items()
    ])
    fig_fac = px.scatter_geo(factory_df, lat='Lat', lon='Lon', scope='usa',
                              text='Factory', size='Orders',
                              color='Factory', color_discrete_map={f: FACTORY_COLORS.get(f,'#999') for f in factory_df['Factory']},
                              hover_data={'Avg Lead': True, 'Orders': True},
                              title="Factory Locations & Order Volume")
    fig_fac.update_traces(textposition='top center')
    fig_fac.update_layout(
        height=420, showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=50, b=0),
        geo=dict(bgcolor='rgba(0,0,0,0)', showland=True, landcolor='#1e3a5f',
                 showcoastlines=True, coastlinecolor='#aac4de',
                 showlakes=True, lakecolor='#16213e',
                 showsubunits=True, subunitcolor='#2a2a4a', subunitwidth=0.5)
    )
    st.plotly_chart(fig_fac, use_container_width=True)

    st.markdown('<div class="section-header">🔥 Regional Bottleneck Analysis</div>', unsafe_allow_html=True)
    region_perf = df.groupby('Region').agg(
        Avg_Lead=('Lead Time', 'mean'),
        Volume=('Row ID', 'count'),
        Delay_Rate=('Delayed', 'mean'),
    ).reset_index()
    fig_reg = make_subplots(specs=[[{"secondary_y": True}]])
    fig_reg.add_trace(go.Bar(x=region_perf['Region'], y=region_perf['Avg_Lead'],
                              name='Avg Lead Time', marker_color='#f4a261'), secondary_y=False)
    fig_reg.add_trace(go.Scatter(x=region_perf['Region'], y=region_perf['Volume'],
                                  name='Order Volume', mode='lines+markers',
                                  line=dict(color='#2a9d8f', width=3), marker=dict(size=10)),
                      secondary_y=True)
    fig_reg.update_layout(height=360, title="Region: Lead Time vs Order Volume",
                           plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    fig_reg.update_yaxes(title_text="Avg Lead Time (days)", secondary_y=False, showgrid=True, gridcolor='#2a2a3a')
    fig_reg.update_yaxes(title_text="Order Volume", secondary_y=True, showgrid=False)
    st.plotly_chart(fig_reg, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 – SHIP MODE
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">🚚 Ship Mode Performance Analysis</div>', unsafe_allow_html=True)

    mode_perf = df.groupby('Ship Mode').agg(
        Avg_Lead=('Lead Time', 'mean'),
        Median_Lead=('Lead Time', 'median'),
        Std_Lead=('Lead Time', 'std'),
        Volume=('Row ID', 'count'),
        Delay_Rate=('Delayed', 'mean'),
        Avg_Cost=('Cost', 'mean'),
        Avg_Sales=('Sales', 'mean'),
        Total_Revenue=('Sales', 'sum'),
    ).reset_index().sort_values('Avg_Lead')

    c1, c2, c3, c4 = st.columns(4)
    for col, row in zip([c1, c2, c3, c4], mode_perf.itertuples()):
        col.markdown(
            f'<div class="metric-card"><h2>{row.Avg_Lead:.0f}d</h2>'
            f'<p>{row._1}<br>Vol: {row.Volume:,} | Delay: {row.Delay_Rate:.0%}</p></div>',
            unsafe_allow_html=True
        )

    col_l, col_r = st.columns(2)
    with col_l:
        fig_box = px.box(df, x='Ship Mode', y='Lead Time', color='Ship Mode',
                          title="Lead Time Distribution by Ship Mode",
                          color_discrete_sequence=['#f4a261', '#e76f51', '#2a9d8f', '#457b9d'])
        fig_box.update_layout(height=380, showlegend=False,
                               plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        fig_box.update_xaxes(showgrid=False)
        fig_box.update_yaxes(showgrid=True, gridcolor='#2a2a3a')
        st.plotly_chart(fig_box, use_container_width=True)

    with col_r:
        fig_cost = px.scatter(mode_perf, x='Avg_Lead', y='Avg_Cost', size='Volume',
                               text='Ship Mode', color='Ship Mode',
                               color_discrete_sequence=['#f4a261', '#e76f51', '#2a9d8f', '#457b9d'],
                               title="Cost vs Lead Time Tradeoff by Ship Mode")
        fig_cost.update_traces(textposition='top center')
        fig_cost.update_layout(height=380, showlegend=False,
                                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        fig_cost.update_xaxes(showgrid=True, gridcolor='#2a2a3a')
        fig_cost.update_yaxes(showgrid=True, gridcolor='#2a2a3a')
        st.plotly_chart(fig_cost, use_container_width=True)

    st.markdown('<div class="section-header">📊 Ship Mode × Region Performance</div>', unsafe_allow_html=True)
    mode_region = df.groupby(['Ship Mode', 'Region'])['Lead Time'].mean().reset_index()
    fig_hm = px.density_heatmap(mode_region, x='Region', y='Ship Mode', z='Lead Time',
                                  color_continuous_scale='RdYlGn_r',
                                  title="Avg Lead Time Heatmap: Ship Mode × Region")
    fig_hm.update_layout(height=360, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_hm, use_container_width=True)

    st.markdown('<div class="section-header">💰 Revenue & Profit by Ship Mode</div>', unsafe_allow_html=True)
    fig_rev = px.bar(mode_perf, x='Ship Mode', y=['Total_Revenue'],
                      color='Ship Mode', title="Total Revenue by Ship Mode",
                      color_discrete_sequence=['#f4a261', '#e76f51', '#2a9d8f', '#457b9d'])
    fig_rev.update_layout(height=320, showlegend=False,
                           plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_rev, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 – ROUTE DRILL-DOWN
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">🔍 Route Deep Dive</div>', unsafe_allow_html=True)

    col_f, col_s = st.columns(2)
    with col_f:
        sel_factory = st.selectbox("Select Factory", sorted(df['Factory'].unique()))
    with col_s:
        states_for_factory = sorted(df[df['Factory'] == sel_factory]['State/Province'].unique())
        sel_state = st.selectbox("Select State", states_for_factory)

    route_df = df[(df['Factory'] == sel_factory) & (df['State/Province'] == sel_state)]
    if route_df.empty:
        st.warning("No data for this combination.")
    else:
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Total Orders", f"{len(route_df):,}")
        r2.metric("Avg Lead Time", f"{route_df['Lead Time'].mean():.1f} days")
        r3.metric("Delay Rate", f"{route_df['Delayed'].mean():.1%}")
        r4.metric("Total Sales", f"${route_df['Sales'].sum():,.0f}")

        col_la, col_ra = st.columns(2)
        with col_la:
            fig_hist = px.histogram(route_df, x='Lead Time', nbins=30, color='Delayed',
                                     color_discrete_map={True: '#e76f51', False: '#2a9d8f'},
                                     title=f"Lead Time Distribution: {sel_factory} → {sel_state}")
            fig_hist.add_vline(x=delay_thresh, line_dash='dash', line_color='yellow',
                                annotation_text=f"Threshold: {delay_thresh:.0f}d")
            fig_hist.update_layout(height=340, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_hist, use_container_width=True)

        with col_ra:
            prod_perf = route_df.groupby('Product Name').agg(
                Orders=('Row ID', 'count'), Avg_Lead=('Lead Time', 'mean'), Delay_Rate=('Delayed', 'mean')
            ).reset_index()
            fig_prod = px.bar(prod_perf, x='Orders', y='Product Name', orientation='h',
                               color='Avg_Lead', color_continuous_scale='RdYlGn_r',
                               title="Orders & Avg Lead by Product")
            fig_prod.update_layout(height=340, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                    coloraxis_showscale=False)
            st.plotly_chart(fig_prod, use_container_width=True)

        st.markdown('<div class="section-header">🕒 Order-Level Shipment Timeline</div>', unsafe_allow_html=True)
        timeline_df = route_df[['Order ID', 'Order Date', 'Ship Date', 'Lead Time', 'Ship Mode', 'Product Name', 'Delayed']].copy()
        timeline_df = timeline_df.sort_values('Order Date').head(50)
        fig_tl = px.timeline(timeline_df, x_start='Order Date', x_end='Ship Date', y='Order ID',
                              color='Delayed', color_discrete_map={True: '#e76f51', False: '#2a9d8f'},
                              hover_data=['Ship Mode', 'Product Name', 'Lead Time'],
                              title=f"Shipment Timelines (first 50 orders) — {sel_factory} → {sel_state}")
        fig_tl.update_layout(height=500, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_tl, use_container_width=True)

        st.markdown('<div class="section-header">📄 Order-Level Data</div>', unsafe_allow_html=True)
        st.dataframe(route_df[['Order ID', 'Order Date', 'Ship Date', 'Lead Time', 'Ship Mode',
                                 'Product Name', 'Sales', 'Gross Profit', 'Delayed']].reset_index(drop=True),
                     use_container_width=True, height=300)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 – TRENDS
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">📈 Monthly Shipping Trends</div>', unsafe_allow_html=True)

    monthly = df.groupby('Order Month').agg(
        Orders=('Row ID', 'count'),
        Avg_Lead=('Lead Time', 'mean'),
        Delay_Rate=('Delayed', 'mean'),
        Revenue=('Sales', 'sum'),
    ).reset_index().sort_values('Order Month')

    fig_trend = make_subplots(rows=2, cols=2, subplot_titles=[
        "Monthly Order Volume", "Monthly Avg Lead Time",
        "Monthly Delay Rate", "Monthly Revenue"
    ])
    colors = ['#f4a261', '#e76f51', '#2a9d8f', '#457b9d']
    metrics = [('Orders', 'bar'), ('Avg_Lead', 'line'), ('Delay_Rate', 'line'), ('Revenue', 'bar')]
    positions = [(1,1), (1,2), (2,1), (2,2)]

    for (metric, chart_type), (r, c), color in zip(metrics, positions, colors):
        if chart_type == 'bar':
            fig_trend.add_trace(go.Bar(x=monthly['Order Month'], y=monthly[metric],
                                        name=metric, marker_color=color, showlegend=False), row=r, col=c)
        else:
            fig_trend.add_trace(go.Scatter(x=monthly['Order Month'], y=monthly[metric],
                                            mode='lines+markers', name=metric,
                                            line=dict(color=color, width=2),
                                            showlegend=False), row=r, col=c)

    fig_trend.update_layout(height=580, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                             title_text="Monthly Shipping Performance Trends")
    fig_trend.update_xaxes(showgrid=False, tickangle=45)
    fig_trend.update_yaxes(showgrid=True, gridcolor='#2a2a3a')
    st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown('<div class="section-header">🏭 Factory Trend Over Time</div>', unsafe_allow_html=True)
    fac_monthly = df.groupby(['Order Month', 'Factory'])['Lead Time'].mean().reset_index()
    fig_fac_trend = px.line(fac_monthly, x='Order Month', y='Lead Time', color='Factory',
                             color_discrete_map={f: FACTORY_COLORS.get(f,'#999') for f in fac_monthly['Factory'].unique()},
                             title="Avg Lead Time per Factory (Monthly)", markers=True)
    fig_fac_trend.update_layout(height=380, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    fig_fac_trend.update_xaxes(showgrid=False, tickangle=45)
    fig_fac_trend.update_yaxes(showgrid=True, gridcolor='#2a2a3a')
    st.plotly_chart(fig_fac_trend, use_container_width=True)

    st.markdown('<div class="section-header">📦 Product-Level Lead Time Analysis</div>', unsafe_allow_html=True)
    prod_lead = df.groupby('Product Name').agg(
        Avg_Lead=('Lead Time', 'mean'),
        Volume=('Row ID', 'count'),
        Delay_Rate=('Delayed', 'mean'),
    ).reset_index().sort_values('Avg_Lead')

    fig_prod_all = px.bar(prod_lead, x='Product Name', y='Avg_Lead',
                           color='Delay_Rate', color_continuous_scale='RdYlGn_r',
                           title="Avg Lead Time by Product (colored by Delay Rate)",
                           labels={'Avg_Lead': 'Avg Lead Time (days)', 'Product Name': ''})
    fig_prod_all.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    fig_prod_all.update_xaxes(tickangle=30, showgrid=False)
    fig_prod_all.update_yaxes(showgrid=True, gridcolor='#2a2a3a')
    st.plotly_chart(fig_prod_all, use_container_width=True)

# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center style='color:#666; font-size:0.8rem;'>🍬 Nassau Candy Distributor · "
    "Shipping Route Intelligence · Built for Unified Mentor Internship Project</center>",
    unsafe_allow_html=True
)