# etl.py
import pandas as pd
import streamlit as st
from pyhive import presto
import urllib3
import logging
from typing import Optional, Tuple
from datetime import datetime

from config import PRESTO_CONFIG, SQL_QUERY, KPIS, CACHE_TTL  # Ajout de CACHE_TTL

# Désactivation des warnings SSL
urllib3.disable_warnings()

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataETL:
    """Classe pour gérer l'ETL des données Presto"""
    
    def __init__(self):
        self.conn = None
        self.df_raw = None
        self.df_processed = None
    
    def connect(self) -> bool:
        """Établit la connexion à Presto"""
        try:
            self.conn = presto.connect(
                host=PRESTO_CONFIG['host'],
                port=PRESTO_CONFIG['port'],
                username=PRESTO_CONFIG['username'],
                catalog=PRESTO_CONFIG['catalog'],
                schema=PRESTO_CONFIG['schema'],
                protocol=PRESTO_CONFIG['protocol'],
                requests_kwargs={'verify': PRESTO_CONFIG['verify_ssl']}
            )
            logger.info("Connexion à Presto établie avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur de connexion à Presto : {str(e)}")
            st.error(f"Erreur de connexion : {str(e)}")
            return False
    
    def extract_data(self) -> Optional[pd.DataFrame]:
        """Extrait les données depuis Presto"""
        try:
            if not self.conn and not self.connect():
                return None
            
            logger.info("Extraction des données en cours...")
            df = pd.read_sql_query(SQL_QUERY, self.conn)
            self.df_raw = df
            logger.info(f"Extraction réussie : {len(df)} lignes extraites")
            return df
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction : {str(e)}")
            st.error(f"Erreur d'extraction : {str(e)}")
            return None
    
    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transforme et nettoie les données"""
        try:
            logger.info("Transformation des données en cours...")
            
            # Nettoyage des noms de colonnes
            df.columns = df.columns.str.lower()
            
            # Conversion des dates
            df['daynumber'] = pd.to_datetime(df['daynumber'])
            
            # Nettoyage des valeurs nulles
            df['region'] = df['region'].fillna('Non spécifié')
            df['kpi_value'] = df['kpi_value'].fillna(0)
            
            # Ajout des noms français des KPIs
            df['kpi_name_fr'] = df['kpi_name'].map(KPIS)
            
            # Ajout de colonnes temporelles pour l'analyse
            df['date'] = df['daynumber'].dt.date
            df['month'] = df['daynumber'].dt.month
            df['year'] = df['daynumber'].dt.year
            df['week'] = df['daynumber'].dt.isocalendar().week
            df['day_name'] = df['daynumber'].dt.day_name()
            df['quarter'] = df['daynumber'].dt.quarter
            df['day_of_week'] = df['daynumber'].dt.dayofweek
            
            self.df_processed = df
            logger.info(f"Transformation réussie : {len(df)} lignes traitées")
            logger.info(f"Période: {df['daynumber'].min()} à {df['daynumber'].max()}")
            
            return df
            
        except Exception as e:
            logger.error(f"Erreur lors de la transformation : {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, dict]:
        """Valide l'intégrité des données"""
        if df.empty:
            return False, {'error': 'DataFrame vide'}
        
        validation_results = {
            'total_rows': len(df),
            'total_regions': df['region'].nunique(),
            'total_kpis': df['kpi_name'].nunique(),
            'date_range': {
                'min': df['daynumber'].min(),
                'max': df['daynumber'].max()
            },
            'total_value': df['kpi_value'].sum()
        }
        
        is_valid = validation_results['total_rows'] > 0 and validation_results['total_value'] > 0
        
        if is_valid:
            logger.info("Validation des données réussie")
        else:
            logger.warning("Échec de la validation des données")
            
        return is_valid, validation_results
    
    def run_etl(self) -> Tuple[pd.DataFrame, dict]:
        """Exécute le pipeline ETL complet"""
        try:
            # Extraction
            df = self.extract_data()
            if df is None or df.empty:
                return pd.DataFrame(), {'error': 'Aucune donnée extraite'}
            
            # Transformation
            df = self.transform_data(df)
            if df.empty:
                return pd.DataFrame(), {'error': 'Échec de la transformation'}
            
            # Validation
            is_valid, validation = self.validate_data(df)
            
            # Fermeture de la connexion
            if self.conn:
                self.conn.close()
                logger.info("Connexion fermée")
            
            if not is_valid:
                return df, validation
            
            return df, {'success': True, **validation}
            
        except Exception as e:
            logger.error(f"Erreur dans le pipeline ETL : {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame(), {'error': str(e)}
    
    def get_kpi_stats(self, df: pd.DataFrame, kpi_code: str) -> dict:
        """Génère des statistiques pour un KPI spécifique"""
        kpi_df = df[df['kpi_name'] == kpi_code]
        
        if kpi_df.empty:
            return {}
        
        stats = {
            'total': kpi_df['kpi_value'].sum(),
            'avg': kpi_df['kpi_value'].mean(),
            'median': kpi_df['kpi_value'].median(),
            'max': kpi_df['kpi_value'].max(),
            'min': kpi_df['kpi_value'].min(),
            'std': kpi_df['kpi_value'].std(),
            'total_days': kpi_df['daynumber'].nunique(),
            'total_regions': kpi_df['region'].nunique(),
            'top_region': kpi_df.groupby('region')['kpi_value'].sum().idxmax(),
            'daily_trend': kpi_df.groupby('daynumber')['kpi_value'].sum().tolist()
        }
        
        return stats


# Fonction de chargement avec cache
@st.cache_data(ttl=CACHE_TTL)
def load_and_process_data():
    """Charge et traite les données avec mise en cache"""
    etl = DataETL()
    df, status = etl.run_etl()
    
    if df.empty:
        return df, status, {}
    
    # Calcul des statistiques globales
    global_stats = {
        'total_value': df['kpi_value'].sum(),
        'avg_daily': df.groupby('daynumber')['kpi_value'].sum().mean(),
        'total_regions': df['region'].nunique(),
        'period_days': (df['daynumber'].max() - df['daynumber'].min()).days + 1
    }
    
    return df, status, global_stats


def filter_data(df: pd.DataFrame, selected_region: str, date_range: tuple) -> pd.DataFrame:
    """Applique les filtres sur les données"""
    df_filtered = df.copy()
    
    if selected_region != 'Toutes':
        df_filtered = df_filtered[df_filtered['region'] == selected_region]
    
    if len(date_range) == 2:
        df_filtered = df_filtered[
            (df_filtered['daynumber'].dt.date >= date_range[0]) &
            (df_filtered['daynumber'].dt.date <= date_range[1])
        ]
    
    return df_filtered