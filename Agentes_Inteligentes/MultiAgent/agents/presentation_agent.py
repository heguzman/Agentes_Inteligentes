# -*- coding: utf-8 -*-
"""
Presentation Agent para generar presentaciones con gráficos de datos financieros
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import seaborn as sns
from io import BytesIO
import base64

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo


class PresentationAgent:
    """Agente especializado en generar presentaciones con gráficos"""
    
    def __init__(self, api_key: str):
        """Inicializa el agente de presentaciones"""
        self.api_key = api_key
        
        # Configurar estilo de gráficos
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Configurar el modelo Gemini
        model_client = OpenAIChatCompletionClient(
            api_key=api_key,
            model="gemini-2.5-flash-lite",
            model_info=ModelInfo(
                vision=True, 
                function_calling=True, 
                json_output=True, 
                family="unknown", 
                structured_output=True
            )
        )
        
        self.assistant_agent = AssistantAgent(
            name="presentation_agent",
            model_client=model_client
        )
    
    async def create_financial_presentation(self, report_file_path: str) -> Dict:
        """Crea una presentación completa con gráficos financieros"""
        try:
            # Cargar reporte de análisis
            with open(report_file_path, 'r', encoding='utf-8') as f:
                report = json.load(f)
            
            # Crear gráficos
            charts = await self._create_charts(report)
            
            # Generar HTML de presentación
            html_presentation = await self._generate_html_presentation(report, charts)
            
            # Generar insights adicionales con Gemini
            insights = await self._generate_presentation_insights(report)
            
            presentation = {
                'timestamp': datetime.now().isoformat(),
                'report_data': report,
                'charts': charts,
                'html_content': html_presentation,
                'insights': insights,
                'metadata': {
                    'total_charts': len(charts),
                    'presentation_type': 'financial_analysis',
                    'market': 'argentina'
                }
            }
            
            return presentation
            
        except Exception as e:
            print(f"Error creando presentación: {e}")
            return {}
    
    async def _create_charts(self, report: Dict) -> List[Dict]:
        """Crea gráficos basados en los datos del reporte"""
        charts = []
        
        try:
            # Gráfico 1: Análisis del MERVAL
            merval_chart = await self._create_merval_chart(report.get('merval_analysis', {}))
            if merval_chart:
                charts.append(merval_chart)
            
            # Gráfico 2: Análisis de acciones individuales
            stocks_chart = await self._create_stocks_chart(report.get('stocks_analysis', {}))
            if stocks_chart:
                charts.append(stocks_chart)
            
            # Gráfico 3: Análisis de divisas
            currency_chart = await self._create_currency_chart(report.get('currency_analysis', {}))
            if currency_chart:
                charts.append(currency_chart)
            
            # Gráfico 4: Tendencias del mercado
            trends_chart = await self._create_trends_chart(report.get('market_trends', {}))
            if trends_chart:
                charts.append(trends_chart)
            
        except Exception as e:
            print(f"Error creando gráficos: {e}")
        
        return charts
    
    async def _create_merval_chart(self, merval_data: Dict) -> Optional[Dict]:
        """Crea gráfico del análisis del MERVAL"""
        try:
            if not merval_data or merval_data.get('status') == 'no_data':
                return None
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Gráfico de precio
            price_str = merval_data.get('price', '0').replace(',', '').replace('.', '')
            try:
                price_value = float(price_str)
            except:
                price_value = 0
            
            ax1.bar(['MERVAL'], [price_value], color='blue', alpha=0.7)
            ax1.set_title('Índice MERVAL - Precio Actual', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Precio')
            ax1.grid(True, alpha=0.3)
            
            # Gráfico de cambio
            change_value = merval_data.get('change_value', 0)
            color = 'green' if change_value > 0 else 'red' if change_value < 0 else 'gray'
            
            ax2.bar(['Cambio %'], [change_value], color=color, alpha=0.7)
            ax2.set_title('MERVAL - Cambio Porcentual', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Cambio (%)')
            ax2.grid(True, alpha=0.3)
            ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            plt.tight_layout()
            
            # Convertir a base64
            chart_data = await self._chart_to_base64(fig)
            plt.close(fig)
            
            return {
                'type': 'merval_analysis',
                'title': 'Análisis del Índice MERVAL',
                'data': chart_data,
                'description': 'Análisis del comportamiento del índice principal de la bolsa argentina'
            }
            
        except Exception as e:
            print(f"Error creando gráfico MERVAL: {e}")
            return None
    
    async def _create_stocks_chart(self, stocks_data: Dict) -> Optional[Dict]:
        """Crea gráfico del análisis de acciones"""
        try:
            if not stocks_data or stocks_data.get('status') == 'no_data':
                return None
            
            stocks = stocks_data.get('stocks', [])
            if not stocks:
                return None
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
            
            # Gráfico de precios de acciones
            symbols = [stock['symbol'] for stock in stocks]
            prices = []
            for stock in stocks:
                try:
                    price_str = stock['price'].replace(',', '').replace('.', '')
                    prices.append(float(price_str))
                except:
                    prices.append(0)
            
            bars1 = ax1.bar(symbols, prices, color='skyblue', alpha=0.7)
            ax1.set_title('Precios de Acciones Argentinas', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Precio')
            ax1.grid(True, alpha=0.3)
            
            # Agregar valores en las barras
            for bar, price in zip(bars1, prices):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{price:.2f}', ha='center', va='bottom')
            
            # Gráfico de cambios porcentuales
            changes = [stock['change_value'] for stock in stocks]
            colors = ['green' if c > 0 else 'red' if c < 0 else 'gray' for c in changes]
            
            bars2 = ax2.bar(symbols, changes, color=colors, alpha=0.7)
            ax2.set_title('Cambios Porcentuales de Acciones', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Cambio (%)')
            ax2.grid(True, alpha=0.3)
            ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            # Agregar valores en las barras
            for bar, change in zip(bars2, changes):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{change:.2f}%', ha='center', va='bottom' if height > 0 else 'top')
            
            plt.tight_layout()
            
            # Convertir a base64
            chart_data = await self._chart_to_base64(fig)
            plt.close(fig)
            
            return {
                'type': 'stocks_analysis',
                'title': 'Análisis de Acciones Individuales',
                'data': chart_data,
                'description': 'Comparación de precios y cambios de las principales acciones argentinas'
            }
            
        except Exception as e:
            print(f"Error creando gráfico de acciones: {e}")
            return None
    
    async def _create_currency_chart(self, currency_data: Dict) -> Optional[Dict]:
        """Crea gráfico del análisis de divisas"""
        try:
            if not currency_data or currency_data.get('status') == 'no_data':
                return None
            
            fig, ax = plt.subplots(1, 1, figsize=(10, 6))
            
            # Gráfico del tipo de cambio USD/ARS
            price_str = currency_data.get('price', '0').replace(',', '').replace('.', '')
            try:
                price_value = float(price_str)
            except:
                price_value = 0
            
            ax.bar(['USD/ARS'], [price_value], color='orange', alpha=0.7)
            ax.set_title('Tipo de Cambio USD/ARS', fontsize=14, fontweight='bold')
            ax.set_ylabel('Precio (ARS por USD)')
            ax.grid(True, alpha=0.3)
            
            # Agregar valor en la barra
            ax.text(0, price_value, f'{price_value:.2f}', ha='center', va='bottom', fontsize=12)
            
            plt.tight_layout()
            
            # Convertir a base64
            chart_data = await self._chart_to_base64(fig)
            plt.close(fig)
            
            return {
                'type': 'currency_analysis',
                'title': 'Análisis de Divisas',
                'data': chart_data,
                'description': 'Tipo de cambio actual USD/ARS y su impacto en el mercado'
            }
            
        except Exception as e:
            print(f"Error creando gráfico de divisas: {e}")
            return None
    
    async def _create_trends_chart(self, trends_data: Dict) -> Optional[Dict]:
        """Crea gráfico de tendencias del mercado"""
        try:
            if not trends_data or trends_data.get('status') == 'no_data':
                return None
            
            fig, ax = plt.subplots(1, 1, figsize=(12, 6))
            
            # Gráfico de sentimiento del mercado
            sentiment_data = trends_data.get('trend_data', {})
            
            # Crear un gráfico de indicadores
            indicators = ['MERVAL', 'Acciones', 'Divisas']
            values = [1, 1, 1]  # Valores neutrales por defecto
            
            # Colores basados en tendencias
            colors = ['blue', 'green', 'orange']
            
            bars = ax.bar(indicators, values, color=colors, alpha=0.7)
            ax.set_title('Indicadores del Mercado Argentino', fontsize=14, fontweight='bold')
            ax.set_ylabel('Estado del Mercado')
            ax.set_ylim(0, 2)
            ax.grid(True, alpha=0.3)
            
            # Agregar etiquetas
            for bar, indicator in zip(bars, indicators):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        'Activo', ha='center', va='bottom', fontsize=10)
            
            plt.tight_layout()
            
            # Convertir a base64
            chart_data = await self._chart_to_base64(fig)
            plt.close(fig)
            
            return {
                'type': 'market_trends',
                'title': 'Tendencias del Mercado',
                'data': chart_data,
                'description': 'Resumen de las tendencias generales del mercado financiero argentino'
            }
            
        except Exception as e:
            print(f"Error creando gráfico de tendencias: {e}")
            return None
    
    async def _chart_to_base64(self, fig) -> str:
        """Convierte un gráfico matplotlib a base64"""
        try:
            buffer = BytesIO()
            fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            buffer.close()
            return image_base64
        except Exception as e:
            print(f"Error convirtiendo gráfico a base64: {e}")
            return ""
    
    async def _generate_html_presentation(self, report: Dict, charts: List[Dict]) -> str:
        """Genera una presentación HTML con los gráficos"""
        try:
            html_template = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Análisis Financiero Argentina - {datetime.now().strftime('%d/%m/%Y')}</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        margin: 0;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }}
                    .container {{
                        max-width: 1200px;
                        margin: 0 auto;
                        background-color: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 40px;
                        border-bottom: 3px solid #2c3e50;
                        padding-bottom: 20px;
                    }}
                    .header h1 {{
                        color: #2c3e50;
                        margin: 0;
                        font-size: 2.5em;
                    }}
                    .header p {{
                        color: #7f8c8d;
                        margin: 10px 0 0 0;
                        font-size: 1.2em;
                    }}
                    .chart-section {{
                        margin: 30px 0;
                        padding: 20px;
                        border: 1px solid #ecf0f1;
                        border-radius: 8px;
                        background-color: #fafafa;
                    }}
                    .chart-title {{
                        color: #2c3e50;
                        font-size: 1.5em;
                        margin-bottom: 15px;
                        font-weight: bold;
                    }}
                    .chart-description {{
                        color: #7f8c8d;
                        margin-bottom: 20px;
                        font-style: italic;
                    }}
                    .chart-image {{
                        text-align: center;
                        margin: 20px 0;
                    }}
                    .chart-image img {{
                        max-width: 100%;
                        height: auto;
                        border-radius: 5px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .summary {{
                        background-color: #ecf0f1;
                        padding: 20px;
                        border-radius: 8px;
                        margin-top: 30px;
                    }}
                    .summary h3 {{
                        color: #2c3e50;
                        margin-top: 0;
                    }}
                    .insights {{
                        background-color: #e8f5e8;
                        padding: 20px;
                        border-radius: 8px;
                        margin-top: 20px;
                        border-left: 4px solid #27ae60;
                    }}
                    .insights h3 {{
                        color: #27ae60;
                        margin-top: 0;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 40px;
                        padding-top: 20px;
                        border-top: 1px solid #ecf0f1;
                        color: #7f8c8d;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📊 Análisis Financiero Argentina</h1>
                        <p>Reporte del {datetime.now().strftime('%d de %B de %Y')}</p>
                    </div>
                    
                    {self._generate_chart_sections(charts)}
                    
                    <div class="summary">
                        <h3>📝 Resumen Ejecutivo</h3>
                        <p>{report.get('summary', 'No hay resumen disponible.')}</p>
                    </div>
                    
                    <div class="insights">
                        <h3>💡 Insights Adicionales</h3>
                        <p>{report.get('insights', 'No hay insights adicionales disponibles.')}</p>
                    </div>
                    
                    <div class="footer">
                        <p>Generado automáticamente por el Sistema Multiagente de Análisis Financiero</p>
                        <p>Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return html_template
            
        except Exception as e:
            print(f"Error generando HTML: {e}")
            return ""
    
    def _generate_chart_sections(self, charts: List[Dict]) -> str:
        """Genera las secciones HTML para cada gráfico"""
        sections = []
        
        for chart in charts:
            section = f"""
            <div class="chart-section">
                <div class="chart-title">{chart.get('title', 'Gráfico')}</div>
                <div class="chart-description">{chart.get('description', '')}</div>
                <div class="chart-image">
                    <img src="data:image/png;base64,{chart.get('data', '')}" alt="{chart.get('title', 'Gráfico')}">
                </div>
            </div>
            """
            sections.append(section)
        
        return ''.join(sections)
    
    async def _generate_presentation_insights(self, report: Dict) -> str:
        """Genera insights adicionales para la presentación"""
        try:
            insights_prompt = f"""
            Basándote en el siguiente análisis financiero argentino, genera insights adicionales para una presentación:
            
            Datos del reporte:
            {json.dumps(report, indent=2, ensure_ascii=False)}
            
            Proporciona:
            1. Puntos clave para destacar en la presentación
            2. Recomendaciones específicas para diferentes audiencias
            3. Alertas o advertencias importantes
            4. Oportunidades identificadas
            
            Formato: Máximo 2 párrafos, lenguaje profesional y directo.
            """
            
            result = await self.assistant_agent.run(task=insights_prompt)
            return result.messages[-1].content
            
        except Exception as e:
            print(f"Error generando insights: {e}")
            return "No se pudieron generar insights adicionales."
    
    async def save_presentation(self, presentation: Dict, filename: str = None) -> str:
        """Guarda la presentación en un archivo HTML"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"financial_presentation_{timestamp}.html"
        
        filepath = os.path.join("Agentes_Inteligentes/MultiAgent/presentations", filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(presentation.get('html_content', ''))
            
            print(f"Presentación guardada en: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error guardando presentación: {e}")
            return ""
    
    async def run(self, report_file_path: str) -> str:
        """Ejecuta el agente de presentaciones"""
        print("📊 Iniciando Presentation Agent...")
        
        # Crear presentación
        presentation = await self.create_financial_presentation(report_file_path)
        
        if presentation:
            # Guardar presentación
            filepath = await self.save_presentation(presentation)
            
            print("📈 Presentación creada exitosamente:")
            print(f"📁 Archivo HTML: {filepath}")
            print(f"📊 Gráficos generados: {presentation.get('metadata', {}).get('total_charts', 0)}")
            
            return filepath
        else:
            print("❌ No se pudo crear la presentación")
            return ""


async def main():
    """Función principal para probar el agente"""
    # Cargar API key desde variables de entorno
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY no encontrada en variables de entorno")
        return
    
    # Buscar el archivo de reporte más reciente
    reports_dir = "Agentes_Inteligentes/MultiAgent/reports"
    if not os.path.exists(reports_dir):
        print("❌ No se encontró el directorio de reportes")
        return
    
    report_files = [f for f in os.listdir(reports_dir) if f.startswith('financial_report_') and f.endswith('.json')]
    if not report_files:
        print("❌ No se encontraron archivos de reporte")
        return
    
    # Usar el archivo más reciente
    latest_file = sorted(report_files)[-1]
    report_file_path = os.path.join(reports_dir, latest_file)
    
    # Crear y ejecutar el agente
    presenter = PresentationAgent(api_key)
    result = await presenter.run(report_file_path)
    
    if result:
        print(f"✅ Presentation Agent completado. Presentación guardada en: {result}")
    else:
        print("❌ Presentation Agent falló")


if __name__ == "__main__":
    asyncio.run(main())
