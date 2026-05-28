# data.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import MTN_COLORS, REGION_COLORS, KPIS

# ============================================
# CARTES ET INDICATEURS
# ============================================

def create_kpi_cards_plotly(df: pd.DataFrame, global_stats: dict):
    """Crée des cartes KPI avec Plotly (gauge charts)"""
    fig = make_subplots(
        rows=1, cols=4,
        subplot_titles=('Valeur Totale', 'Moyenne Journalière', 'Régions', 'Jours'),
        specs=[[{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}]]
    )
    
    fig.add_trace(go.Indicator(
        mode="number",
        value=global_stats['total_value'],
        number={'font': {'size': 40, 'color': MTN_COLORS['secondary']}, 'valueformat': ',.0f'},
        title={'text': "💰", 'font': {'size': 24}},
        domain={'row': 0, 'column': 0}
    ), row=1, col=1)
    
    fig.add_trace(go.Indicator(
        mode="number",
        value=global_stats['avg_daily'],
        number={'font': {'size': 40, 'color': MTN_COLORS['secondary']}, 'valueformat': ',.0f'},
        title={'text': "📊", 'font': {'size': 24}},
        domain={'row': 0, 'column': 1}
    ), row=1, col=2)
    
    fig.add_trace(go.Indicator(
        mode="number",
        value=global_stats['total_regions'],
        number={'font': {'size': 40, 'color': MTN_COLORS['secondary']}, 'valueformat': 'd'},
        title={'text': "📍", 'font': {'size': 24}},
        domain={'row': 0, 'column': 2}
    ), row=1, col=3)
    
    fig.add_trace(go.Indicator(
        mode="number",
        value=global_stats['period_days'],
        number={'font': {'size': 40, 'color': MTN_COLORS['secondary']}, 'valueformat': 'd'},
        title={'text': "📅", 'font': {'size': 24}},
        domain={'row': 0, 'column': 3}
    ), row=1, col=4)
    
    fig.update_layout(
        height=150,
        showlegend=False,
        margin=dict(t=50, b=0, l=0, r=0)
    )
    
    return fig


# ============================================
# VUE JOURNALIÈRE
# ============================================

def create_daily_evolution_plotly(df: pd.DataFrame, kpi_code: str, kpi_name: str):
    """Graphique d'évolution quotidienne"""
    kpi_df = df[df['kpi_name'] == kpi_code]
    daily_region = kpi_df.groupby(['daynumber', 'region'])['kpi_value'].sum().reset_index()
    
    fig = px.line(
        daily_region,
        x='daynumber',
        y='kpi_value',
        color='region',
        title=f"📈 Évolution quotidienne - {kpi_name}",
        labels={'daynumber': 'Date', 'kpi_value': 'Valeur', 'region': 'Région'},
        color_discrete_sequence=REGION_COLORS,
        markers=True
    )
    
    fig.update_layout(
        height=450,
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        title_font_size=16,
        title_font_color=MTN_COLORS['secondary'],
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor='rgba(255,255,255,0.8)')
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    return fig


def create_region_comparison_plotly(df: pd.DataFrame, kpi_code: str, kpi_name: str):
    """Graphique de comparaison par région"""
    kpi_df = df[df['kpi_name'] == kpi_code]
    region_total = kpi_df.groupby('region')['kpi_value'].sum().sort_values(ascending=True).reset_index()
    
    fig = px.bar(
        region_total,
        x='kpi_value',
        y='region',
        orientation='h',
        title=f"🏆 Total par région - {kpi_name}",
        labels={'kpi_value': 'Valeur totale', 'region': 'Région'},
        color='kpi_value',
        color_continuous_scale=[MTN_COLORS['primary'], MTN_COLORS['secondary']],
        text='kpi_value'
    )
    
    fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig.update_layout(
        height=450,
        plot_bgcolor='white',
        paper_bgcolor='white',
        title_font_size=16,
        title_font_color=MTN_COLORS['secondary'],
        coloraxis_showscale=False
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    return fig


def create_daily_detail_plotly(df: pd.DataFrame, selected_date):
    """Graphique du détail journalier"""
    daily_detail = df[df['daynumber'].dt.date == selected_date]
    
    if daily_detail.empty:
        return None
    
    detail_data = daily_detail.groupby(['kpi_name_fr', 'region'])['kpi_value'].sum().reset_index()
    
    fig = px.bar(
        detail_data,
        x='region',
        y='kpi_value',
        color='kpi_name_fr',
        title=f"📅 Détail du {selected_date}",
        labels={'region': 'Région', 'kpi_value': 'Valeur', 'kpi_name_fr': 'KPI'},
        color_discrete_sequence=[MTN_COLORS['primary'], MTN_COLORS['secondary'], MTN_COLORS['accent']],
        barmode='group'
    )
    
    fig.update_layout(
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        title_font_size=16,
        title_font_color=MTN_COLORS['secondary']
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    return fig


def create_heatmap_plotly(df: pd.DataFrame):
    """Heatmap des performances"""
    heatmap_data = df.pivot_table(
        values='kpi_value',
        index='region',
        columns=df['daynumber'].dt.strftime('%Y-%m-%d'),
        aggfunc='sum'
    ).fillna(0)
    
    fig = px.imshow(
        heatmap_data,
        title="🔥 Heatmap des performances (Région vs Date)",
        labels={'x': 'Date', 'y': 'Région', 'color': 'Valeur KPI'},
        color_continuous_scale='Viridis',
        aspect='auto'
    )
    
    fig.update_layout(
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
        title_font_size=16,
        title_font_color=MTN_COLORS['secondary']
    )
    
    return fig


# ============================================
# ANALYSE STATISTIQUE
# ============================================

def create_distribution_plotly(df: pd.DataFrame, kpi_code: str, kpi_name: str):
    """Graphique de distribution des valeurs"""
    kpi_df = df[df['kpi_name'] == kpi_code]
    
    fig = px.histogram(
        kpi_df,
        x='kpi_value',
        nbins=30,
        title=f"📊 Distribution des valeurs - {kpi_name}",
        labels={'kpi_value': 'Valeur', 'count': 'Fréquence'},
        color_discrete_sequence=[MTN_COLORS['primary']],
        marginal='box'
    )
    
    fig.update_layout(
        height=450,
        plot_bgcolor='white',
        paper_bgcolor='white',
        title_font_size=16,
        title_font_color=MTN_COLORS['secondary']
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    return fig


def create_trend_analysis_plotly(df: pd.DataFrame):
    """Analyse des tendances avec moyenne mobile"""
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=list(KPIS.values()),
        shared_xaxes=True,
        vertical_spacing=0.1
    )
    
    colors = [MTN_COLORS['primary'], MTN_COLORS['secondary'], MTN_COLORS['accent']]
    
    for idx, (kpi_code, kpi_name) in enumerate(KPIS.items(), 1):
        kpi_df = df[df['kpi_name'] == kpi_code]
        daily_total = kpi_df.groupby('daynumber')['kpi_value'].sum().reset_index()
        daily_total['trend_7d'] = daily_total['kpi_value'].rolling(window=7, min_periods=1).mean()
        daily_total['trend_30d'] = daily_total['kpi_value'].rolling(window=30, min_periods=1).mean()
        
        # Valeurs quotidiennes
        fig.add_trace(
            go.Scatter(
                x=daily_total['daynumber'],
                y=daily_total['kpi_value'],
                mode='lines',
                name=f"{kpi_name} (quotidien)",
                line=dict(color='lightgray', width=1),
                showlegend=False
            ),
            row=idx, col=1
        )
        
        # Tendance 7 jours
        fig.add_trace(
            go.Scatter(
                x=daily_total['daynumber'],
                y=daily_total['trend_7d'],
                mode='lines',
                name=f"{kpi_name} (tendance 7j)",
                line=dict(color=colors[idx-1], width=3),
                showlegend=False
            ),
            row=idx, col=1
        )
    
    fig.update_layout(
        height=900,
        plot_bgcolor='white',
        paper_bgcolor='white',
        title_text="📈 Analyse des tendances (Moyennes mobiles)",
        title_font_size=18,
        title_font_color=MTN_COLORS['secondary'],
        showlegend=False
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    return fig


def create_correlation_matrix_plotly(df: pd.DataFrame):
    """Matrice de corrélation entre KPIs"""
    corr_data = df.pivot_table(
        values='kpi_value',
        index=['daynumber', 'region'],
        columns='kpi_name'
    ).fillna(0)
    
    corr_matrix = corr_data.corr()
    
    labels = [KPIS.get(col, col) for col in corr_matrix.columns]
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=labels,
        y=labels,
        colorscale='RdBu',
        zmin=-1, zmax=1,
        text=corr_matrix.round(3).values,
        texttemplate='%{text}',
        textfont={"size": 12, "color": "black"},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title="🔗 Matrice de corrélation entre KPIs",
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
        title_font_size=16,
        title_font_color=MTN_COLORS['secondary']
    )
    
    return fig


def create_weekly_pattern_plotly(df: pd.DataFrame):
    """Pattern hebdomadaire"""
    weekly_data = df.groupby(['day_name', 'kpi_name_fr'])['kpi_value'].mean().reset_index()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly_data['day_name'] = pd.Categorical(weekly_data['day_name'], categories=day_order, ordered=True)
    weekly_data = weekly_data.sort_values('day_name')
    
    fig = px.line(
        weekly_data,
        x='day_name',
        y='kpi_value',
        color='kpi_name_fr',
        title="📅 Pattern hebdomadaire (moyenne par jour)",
        labels={'day_name': 'Jour', 'kpi_value': 'Valeur moyenne', 'kpi_name_fr': 'KPI'},
        color_discrete_sequence=[MTN_COLORS['primary'], MTN_COLORS['secondary'], MTN_COLORS['accent']],
        markers=True
    )
    
    fig.update_layout(
        height=450,
        plot_bgcolor='white',
        paper_bgcolor='white',
        title_font_size=16,
        title_font_color=MTN_COLORS['secondary']
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    return fig


# ============================================
# ANALYSES AVANCÉES
# ============================================

def create_pie_chart_plotly(df: pd.DataFrame):
    """Camembert de répartition par KPI"""
    kpi_total = df.groupby('kpi_name_fr')['kpi_value'].sum().reset_index()
    
    fig = px.pie(
        kpi_total,
        values='kpi_value',
        names='kpi_name_fr',
        title="🥧 Répartition par type de KPI",
        color_discrete_sequence=[MTN_COLORS['primary'], MTN_COLORS['secondary'], MTN_COLORS['accent']],
        hole=0.3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        height=450,
        plot_bgcolor='white',
        paper_bgcolor='white',
        title_font_size=16,
        title_font_color=MTN_COLORS['secondary']
    )
    
    return fig


def create_region_boxplot_plotly(df: pd.DataFrame, selected_kpi: str):
    """Boxplot par région"""
    kpi_df = df[df['kpi_name'] == selected_kpi]
    
    fig = px.box(
        kpi_df,
        x='region',
        y='kpi_value',
        title=f"📦 Distribution par région - {KPIS[selected_kpi]}",
        labels={'region': 'Région', 'kpi_value': 'Valeur KPI'},
        color='region',
        color_discrete_sequence=REGION_COLORS,
        points='all'
    )
    
    fig.update_layout(
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
        title_font_size=16,
        title_font_color=MTN_COLORS['secondary'],
        showlegend=False
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    return fig


def create_forecast_plotly(df: pd.DataFrame):
    """Graphique de prévision"""
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=list(KPIS.values()),
        specs=[[{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}]]
    )
    
    for idx, (kpi_code, kpi_name) in enumerate(KPIS.items(), 1):
        kpi_df = df[df['kpi_name'] == kpi_code]
        daily_total = kpi_df.groupby('daynumber')['kpi_value'].sum()
        
        if len(daily_total) >= 14:
            last_14_avg = daily_total.tail(14).mean()
            forecast_7d = last_14_avg * 7
            
            fig.add_trace(
                go.Indicator(
                    mode="number+gauge",
                    value=forecast_7d,
                    title={'text': f"{kpi_name}<br>Prévision 7 jours", 'font': {'size': 14}},
                    number={'font': {'size': 28, 'color': MTN_COLORS['secondary']}, 'valueformat': ',.0f'},
                    gauge={
                        'axis': {'range': [0, forecast_7d * 1.5], 'visible': False},
                        'bar': {'color': MTN_COLORS['primary']},
                        'steps': [
                            {'range': [0, forecast_7d * 0.7], 'color': '#E8F5E9'},
                            {'range': [forecast_7d * 0.7, forecast_7d * 1.2], 'color': '#FFF3E0'},
                            {'range': [forecast_7d * 1.2, forecast_7d * 1.5], 'color': '#FFEBEE'}
                        ],
                        'threshold': {
                            'line': {'color': MTN_COLORS['accent'], 'width': 4},
                            'thickness': 0.75,
                            'value': forecast_7d
                        }
                    }
                ),
                row=1, col=idx
            )
    
    fig.update_layout(
        height=300,
        plot_bgcolor='white',
        paper_bgcolor='white',
        title_text="🔮 Prévision des 7 prochains jours",
        title_font_size=18,
        title_font_color=MTN_COLORS['secondary']
    )
    
    return fig


def create_stats_table_plotly(df: pd.DataFrame):
    """Tableau des statistiques avec Plotly"""
    stats_data = []
    for kpi_code, kpi_name in KPIS.items():
        kpi_df = df[df['kpi_name'] == kpi_code]
        if not kpi_df.empty:
            stats_data.append({
                'KPI': kpi_name,
                'Total': f"{kpi_df['kpi_value'].sum():,.0f}",
                'Moyenne': f"{kpi_df['kpi_value'].mean():,.0f}",
                'Médiane': f"{kpi_df['kpi_value'].median():,.0f}",
                'Max': f"{kpi_df['kpi_value'].max():,.0f}",
                'Min': f"{kpi_df['kpi_value'].min():,.0f}",
                'Écart-type': f"{kpi_df['kpi_value'].std():,.0f}",
                'Top Région': kpi_df.groupby('region')['kpi_value'].sum().idxmax()
            })
    
    if not stats_data:
        return None
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(stats_data[0].keys()),
            fill_color=MTN_COLORS['secondary'],
            font=dict(color='white', size=12),
            align='center'
        ),
        cells=dict(
            values=[list(col) for col in zip(*[list(d.values()) for d in stats_data])],
            fill_color='white',
            align='center',
            font=dict(size=11),
            height=30
        )
    )])
    
    fig.update_layout(height=350, margin=dict(t=0, b=0, l=0, r=0))
    return fig