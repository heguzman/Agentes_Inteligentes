# -*- coding: utf-8 -*-
"""
Configuración del Sistema Multiagente de Análisis Financiero
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración centralizada del sistema"""
    
    # API Configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL = "gemini-2.5-flash-lite"
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    REPORTS_DIR = os.path.join(BASE_DIR, "reports")
    PRESENTATIONS_DIR = os.path.join(BASE_DIR, "presentations")
    AGENTS_DIR = os.path.join(BASE_DIR, "agents")
    
    # Web Scraping Configuration
    SCRAPING_TIMEOUT = 10
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    
    # URLs de fuentes de datos
    DATA_SOURCES = {
        'investing_merval': 'https://es.investing.com/indices/s-and-p-merval',
        'investing_usd_ars': 'https://es.investing.com/currencies/usd-ars',
        'yahoo_base': 'https://finance.yahoo.com/quote/'
    }
    
    # Acciones argentinas principales
    ARGENTINE_STOCKS = ['GGAL', 'PAMP', 'TXAR', 'YPFD', 'MIRG', 'BBAR', 'CRES', 'EDN', 'HARG', 'LOMA']
    
    # Configuración de gráficos
    CHART_CONFIG = {
        'figure_size': (15, 10),
        'dpi': 300,
        'style': 'seaborn-v0_8',
        'color_palette': 'husl'
    }
    
    # Configuración de presentaciones
    PRESENTATION_CONFIG = {
        'title': 'Análisis Financiero Argentina',
        'company': 'Sistema Multiagente',
        'template': 'financial_analysis'
    }
    
    @classmethod
    def validate_config(cls):
        """Valida que la configuración esté completa"""
        errors = []
        
        if not cls.GOOGLE_API_KEY:
            errors.append("GOOGLE_API_KEY no configurada")
        
        # Verificar que los directorios existan
        for dir_name, dir_path in [
            ('DATA_DIR', cls.DATA_DIR),
            ('REPORTS_DIR', cls.REPORTS_DIR),
            ('PRESENTATIONS_DIR', cls.PRESENTATIONS_DIR)
        ]:
            if not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                except Exception as e:
                    errors.append(f"No se pudo crear {dir_name}: {e}")
        
        return errors
    
    @classmethod
    def get_stock_url(cls, symbol: str) -> str:
        """Obtiene la URL de Yahoo Finance para una acción argentina"""
        return f"{cls.DATA_SOURCES['yahoo_base']}{symbol}.BA"
    
    @classmethod
    def get_model_info(cls):
        """Obtiene la configuración del modelo Gemini"""
        from autogen_core.models import ModelInfo
        return ModelInfo(
            vision=True,
            function_calling=True,
            json_output=True,
            family="unknown",
            structured_output=True
        )
