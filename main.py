# main.py - Point d'entrée principal
import streamlit as st
from datetime import datetime

from config import STREAMLIT_CONFIG, CUSTOM_CSS, KPIS
from etl import load_and_process_data, filter_data
from data import (
    create_kpi_cards_plotly,
    create_daily_evolution_plotly,
    create_region_comparison_plotly,
    create_daily_detail_plotly,
    create_heatmap_plotly,
    create_distribution_plotly,
    create_trend_analysis_plotly,
    create_correlation_matrix_plotly,
    create_weekly_pattern_plotly,
    create_pie_chart_plotly,
    create_region_boxplot_plotly,
    create_forecast_plotly,
    create_stats_table_plotly
)

# Configuration de la page
st.set_page_config(**STREAMLIT_CONFIG)

# Application du CSS personnalisé
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# En-tête
st.markdown("""
<div class="header-container">
    <h1 class="header-title">📊 MTN Performance Dashboard</h1>
    <p class="header-subtitle">Analyse des indicateurs clés de performance - Recharges & Activations</p>
</div>
""", unsafe_allow_html=True)

# Chargement des données
with st.spinner("🔄 Chargement des données MTN..."):
    df, status, global_stats = load_and_process_data()

if df.empty:
    st.error("❌ Aucune donnée disponible. Vérifiez votre connexion à la base de données.")
    st.stop()

# Sidebar avec filtres
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/MTN_Group_logo.svg/1200px-MTN_Group_logo.svg.png", 
             use_container_width=True)
    st.markdown("---")
    
    st.markdown("### 🔍 Filtres")
    
    regions = ['Toutes'] + sorted(df['region'].unique().tolist())
    selected_region = st.selectbox("📍 Région", regions)
    
    min_date = df['daynumber'].min().date()
    max_date = df['daynumber'].max().date()
    date_range = st.date_input("📅 Période", value=(min_date, max_date), 
                               min_value=min_date, max_value=max_date)
    
    st.markdown("---")
    st.caption(f"🔄 Dernière mise à jour : {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Application des filtres
df_filtered = filter_data(df, selected_region, date_range)

if df_filtered.empty:
    st.warning("⚠️ Aucune donnée après application des filtres")
    st.stop()

# Cartes KPI (Plotly)
st.plotly_chart(create_kpi_cards_plotly(df_filtered, global_stats), use_container_width=True)

st.markdown("---")

# Onglets principaux
tab1, tab2, tab3 = st.tabs(["📊 Vue Journalière", "📈 Analyse Statistique", "🔬 Analyses Avancées"])

# ============================================
# TAB 1: VUE JOURNALIÈRE
# ============================================
with tab1:
    # Sélecteur de date
    selected_date = st.date_input(
        "📅 Sélectionnez une date pour le détail",
        value=df_filtered['daynumber'].max().date(),
        min_value=df_filtered['daynumber'].min().date(),
        max_value=df_filtered['daynumber'].max().date()
    )
    
    # Graphiques par KPI
    for kpi_code, kpi_name in KPIS.items():
        st.markdown(f"### {kpi_name}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_evol = create_daily_evolution_plotly(df_filtered, kpi_code, kpi_name)
            st.plotly_chart(fig_evol, use_container_width=True)
        
        with col2:
            fig_comp = create_region_comparison_plotly(df_filtered, kpi_code, kpi_name)
            st.plotly_chart(fig_comp, use_container_width=True)
    
    # Détail journalier
    st.markdown("---")
    st.markdown("### 📅 Détail journalier")
    
    fig_detail = create_daily_detail_plotly(df_filtered, selected_date)
    if fig_detail:
        st.plotly_chart(fig_detail, use_container_width=True)
    
    # Heatmap
    st.markdown("---")
    fig_heatmap = create_heatmap_plotly(df_filtered)
    st.plotly_chart(fig_heatmap, use_container_width=True)

# ============================================
# TAB 2: ANALYSE STATISTIQUE
# ============================================
with tab2:
    # Distribution par KPI
    st.markdown("### 📊 Distribution des valeurs")
    
    for kpi_code, kpi_name in KPIS.items():
        fig_dist = create_distribution_plotly(df_filtered, kpi_code, kpi_name)
        st.plotly_chart(fig_dist, use_container_width=True)
    
    # Tendances
    st.markdown("---")
    fig_trends = create_trend_analysis_plotly(df_filtered)
    st.plotly_chart(fig_trends, use_container_width=True)
    
    # Corrélation
    st.markdown("---")
    fig_corr = create_correlation_matrix_plotly(df_filtered)
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # Pattern hebdomadaire
    st.markdown("---")
    fig_weekly = create_weekly_pattern_plotly(df_filtered)
    st.plotly_chart(fig_weekly, use_container_width=True)

# ============================================
# TAB 3: ANALYSES AVANCÉES
# ============================================
with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        fig_pie = create_pie_chart_plotly(df_filtered)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        selected_kpi_advanced = st.selectbox(
            "📊 Sélectionnez un KPI pour l'analyse détaillée",
            list(KPIS.keys()),
            format_func=lambda x: KPIS[x]
        )
        fig_box = create_region_boxplot_plotly(df_filtered, selected_kpi_advanced)
        st.plotly_chart(fig_box, use_container_width=True)
    
    # Prévision
    st.markdown("---")
    fig_forecast = create_forecast_plotly(df_filtered)
    st.plotly_chart(fig_forecast, use_container_width=True)
    
    # Tableau des statistiques
    st.markdown("---")
    st.markdown("### 📊 Récapitulatif statistique")
    
    fig_table = create_stats_table_plotly(df_filtered)
    if fig_table:
        st.plotly_chart(fig_table, use_container_width=True)

# Pied de page
st.markdown("""
<div class="footer">
    © 2024 MTN Dashboard - Version Plotly | Données mises à jour quotidiennement
</div>
""", unsafe_allow_html=True)