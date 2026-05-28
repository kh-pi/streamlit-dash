# config.py
import streamlit as st
from datetime import datetime

# Configuration de la page Streamlit
STREAMLIT_CONFIG = {
    'page_title': "MTN Dashboard - KPIs",
    'page_icon': "📊",
    'layout': "wide",
    'initial_sidebar_state': "expanded"
}

# Configuration de la base de données Presto
PRESTO_CONFIG = {
    'host': 'lnx-eva-master01.mtn.bj',
    'port': 8443,
    'username': 'akinnin',
    'catalog': 'hive',
    'schema': 'snd_bi',
    'protocol': 'https',
    'verify_ssl': False
}

# Configuration de la requête SQL
SQL_QUERY = """
SELECT 
    sk.DAYNUMBER,
    sk.KPI_NAME,
    b.region,
    sk.KPI_VALUE
FROM 
    snd_bireports_svc.sd_kpis_eva_ sk
LEFT JOIN snd_bi.site_new_info_dealer b ON sk.site_id = b.site_id 
WHERE 
    sk.KPI_NAME IN (
        'TOTAL_REFILL_AMOUNT',
        'TOTAL_MOMO_REFILL_FROM_SUBSCRIBERS_AMOUNT',
        'NEW_ACTIVATION')
    AND sk.DAYNUMBER BETWEEN DATE_ADD('day', -89, current_date) 
              AND DATE_ADD('day', -1, current_date)
"""

# Liste des KPIs
KPIS = {
    'TOTAL_REFILL_AMOUNT': 'Recharges Total',
    'TOTAL_MOMO_REFILL_FROM_SUBSCRIBERS_AMOUNT': 'Recharges Mobile Money',
    'NEW_ACTIVATION': 'Nouvelles Activations'
}

# Couleurs MTN
MTN_COLORS = {
    'primary': '#FFC72C',
    'secondary': '#005B9F',
    'accent': '#E31837',
    'background': '#F8F9FA',
    'success': '#28A745',
    'warning': '#FF9800',
    'info': '#00BCD4'
}

# Palette de couleurs pour les régions
REGION_COLORS = [
    '#FFC72C', '#005B9F', '#E31837', '#28A745', 
    '#FF9800', '#00BCD4', '#9C27B0', '#FF5722'
]

# CSS personnalisé
CUSTOM_CSS = """
<style>
    .main { background-color: #F8F9FA; }
    h1, h2, h3 { color: #005B9F; font-weight: 600; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; 
        font-size: 18px; 
        font-weight: 500;
    }
    .header-container {
        text-align: center; 
        padding: 20px; 
        background: linear-gradient(135deg, #FFC72C20, #005B9F20); 
        border-radius: 15px; 
        margin-bottom: 20px;
    }
    .header-title {
        color: #005B9F;
        font-size: 2.5rem;
        font-weight: 600;
        margin: 0;
    }
    .header-subtitle {
        color: #666;
        font-size: 1rem;
        margin-top: 10px;
    }
    .footer {
        text-align: center;
        color: gray;
        padding: 20px;
        margin-top: 30px;
    }
</style>
"""

# Cache TTL (seconds)
CACHE_TTL = 3600