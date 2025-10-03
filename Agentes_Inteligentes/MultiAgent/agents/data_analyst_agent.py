# -*- coding: utf-8 -*-
"""
Data Analyst Agent para analizar datos financieros y generar reportes
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo


class DataAnalystAgent:
    """Agente especializado en análisis de datos financieros"""
    
    def __init__(self, api_key: str):
        """Inicializa el agente analista de datos"""
        self.api_key = api_key
        
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
            name="data_analyst",
            model_client=model_client
        )
    
    async def analyze_financial_data(self, data_file_path: str) -> Dict:
        """Analiza los datos financieros y genera insights"""
        try:
            # Cargar datos del archivo
            with open(data_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Análisis del MERVAL
            merval_analysis = await self._analyze_merval(data.get('merval', {}))
            
            # Análisis de acciones individuales
            stocks_analysis = await self._analyze_stocks(data.get('stocks', []))
            
            # Análisis de divisas
            currency_analysis = await self._analyze_currency(data.get('currency', {}))
            
            # Análisis de tendencias generales
            market_trends = await self._analyze_market_trends(data)
            
            # Generar reporte consolidado
            report = {
                'timestamp': datetime.now().isoformat(),
                'merval_analysis': merval_analysis,
                'stocks_analysis': stocks_analysis,
                'currency_analysis': currency_analysis,
                'market_trends': market_trends,
                'summary': await self._generate_executive_summary(data)
            }
            
            return report
            
        except Exception as e:
            print(f"Error analizando datos: {e}")
            return {}
    
    async def _analyze_merval(self, merval_data: Dict) -> Dict:
        """Analiza específicamente el índice MERVAL"""
        if not merval_data:
            return {'status': 'no_data', 'message': 'No hay datos del MERVAL disponibles'}
        
        try:
            # Extraer información numérica del cambio
            change_str = merval_data.get('change', '0%')
            change_value = float(change_str.replace('%', '').replace('+', ''))
            
            # Determinar tendencia
            trend = 'positiva' if change_value > 0 else 'negativa' if change_value < 0 else 'neutral'
            
            # Generar análisis con Gemini
            analysis_prompt = f"""
            Analiza el comportamiento del índice MERVAL argentino:
            
            Datos:
            - Precio: {merval_data.get('price', 'N/A')}
            - Cambio: {merval_data.get('change', 'N/A')}
            - Timestamp: {merval_data.get('timestamp', 'N/A')}
            
            Proporciona:
            1. Interpretación del movimiento del índice
            2. Posibles factores que influyen en esta tendencia
            3. Contexto histórico relevante
            4. Recomendaciones para inversores
            """
            
            result = await self.assistant_agent.run(task=analysis_prompt)
            gemini_analysis = result.messages[-1].content
            
            return {
                'price': merval_data.get('price'),
                'change': merval_data.get('change'),
                'change_value': change_value,
                'trend': trend,
                'analysis': gemini_analysis,
                'timestamp': merval_data.get('timestamp')
            }
            
        except Exception as e:
            print(f"Error analizando MERVAL: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _analyze_stocks(self, stocks_data: List[Dict]) -> Dict:
        """Analiza las acciones individuales"""
        if not stocks_data:
            return {'status': 'no_data', 'message': 'No hay datos de acciones disponibles'}
        
        try:
            # Calcular estadísticas básicas
            total_stocks = len(stocks_data)
            positive_changes = 0
            negative_changes = 0
            
            stock_summaries = []
            
            for stock in stocks_data:
                try:
                    change_str = stock.get('change', '0')
                    change_value = float(change_str.replace('%', '').replace('+', ''))
                    
                    if change_value > 0:
                        positive_changes += 1
                    elif change_value < 0:
                        negative_changes += 1
                    
                    stock_summaries.append({
                        'symbol': stock.get('symbol'),
                        'price': stock.get('price'),
                        'change': stock.get('change'),
                        'change_value': change_value
                    })
                    
                except ValueError:
                    continue
            
            # Generar análisis con Gemini
            analysis_prompt = f"""
            Analiza el comportamiento de las principales acciones argentinas:
            
            Datos de acciones:
            {json.dumps(stock_summaries, indent=2, ensure_ascii=False)}
            
            Estadísticas:
            - Total de acciones analizadas: {total_stocks}
            - Acciones con ganancias: {positive_changes}
            - Acciones con pérdidas: {negative_changes}
            
            Proporciona:
            1. Análisis sectorial del mercado argentino
            2. Identificación de las acciones más destacadas
            3. Patrones observados en el comportamiento
            4. Recomendaciones de inversión
            """
            
            result = await self.assistant_agent.run(task=analysis_prompt)
            gemini_analysis = result.messages[-1].content
            
            return {
                'total_stocks': total_stocks,
                'positive_changes': positive_changes,
                'negative_changes': negative_changes,
                'market_sentiment': 'positive' if positive_changes > negative_changes else 'negative',
                'stocks': stock_summaries,
                'analysis': gemini_analysis
            }
            
        except Exception as e:
            print(f"Error analizando acciones: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _analyze_currency(self, currency_data: Dict) -> Dict:
        """Analiza el comportamiento de las divisas"""
        if not currency_data:
            return {'status': 'no_data', 'message': 'No hay datos de divisas disponibles'}
        
        try:
            # Generar análisis con Gemini
            analysis_prompt = f"""
            Analiza el comportamiento del tipo de cambio USD/ARS:
            
            Datos:
            - Par: {currency_data.get('pair', 'N/A')}
            - Precio: {currency_data.get('price', 'N/A')}
            - Timestamp: {currency_data.get('timestamp', 'N/A')}
            
            Proporciona:
            1. Interpretación del nivel del tipo de cambio
            2. Impacto en la economía argentina
            3. Factores que influyen en la cotización
            4. Perspectivas para inversores y empresas
            """
            
            result = await self.assistant_agent.run(task=analysis_prompt)
            gemini_analysis = result.messages[-1].content
            
            return {
                'pair': currency_data.get('pair'),
                'price': currency_data.get('price'),
                'analysis': gemini_analysis,
                'timestamp': currency_data.get('timestamp')
            }
            
        except Exception as e:
            print(f"Error analizando divisas: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _analyze_market_trends(self, data: Dict) -> Dict:
        """Analiza tendencias generales del mercado"""
        try:
            # Recopilar información para análisis de tendencias
            trend_data = {
                'merval_trend': data.get('merval', {}).get('change', 'N/A'),
                'stocks_count': len(data.get('stocks', [])),
                'currency_level': data.get('currency', {}).get('price', 'N/A'),
                'timestamp': datetime.now().isoformat()
            }
            
            # Generar análisis de tendencias con Gemini
            analysis_prompt = f"""
            Analiza las tendencias generales del mercado financiero argentino:
            
            Datos consolidados:
            {json.dumps(trend_data, indent=2, ensure_ascii=False)}
            
            Proporciona:
            1. Resumen de las tendencias del día
            2. Correlaciones entre diferentes instrumentos
            3. Factores macroeconómicos relevantes
            4. Perspectivas a corto plazo
            5. Recomendaciones estratégicas
            """
            
            result = await self.assistant_agent.run(task=analysis_prompt)
            gemini_analysis = result.messages[-1].content
            
            return {
                'trend_data': trend_data,
                'analysis': gemini_analysis
            }
            
        except Exception as e:
            print(f"Error analizando tendencias: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _generate_executive_summary(self, data: Dict) -> str:
        """Genera un resumen ejecutivo del análisis"""
        try:
            summary_prompt = f"""
            Genera un resumen ejecutivo del análisis financiero argentino:
            
            Datos disponibles:
            {json.dumps(data, indent=2, ensure_ascii=False)}
            
            El resumen debe incluir:
            1. Puntos clave del día
            2. Conclusiones principales
            3. Recomendaciones para diferentes tipos de inversores
            4. Perspectivas para el próximo período
            
            Formato: Máximo 3 párrafos, lenguaje claro y directo.
            """
            
            result = await self.assistant_agent.run(task=summary_prompt)
            return result.messages[-1].content
            
        except Exception as e:
            print(f"Error generando resumen ejecutivo: {e}")
            return "No se pudo generar el resumen ejecutivo."
    
    async def save_report(self, report: Dict, filename: str = None) -> str:
        """Guarda el reporte de análisis en un archivo"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"financial_report_{timestamp}.json"
        
        # Asegurar que el directorio existe
        reports_dir = "reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir, exist_ok=True)
        
        filepath = os.path.join(reports_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"Reporte guardado en: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error guardando reporte: {e}")
            return ""
    
    async def run(self, data_file_path: str) -> str:
        """Ejecuta el agente analista de datos"""
        print("Iniciando Data Analyst Agent...")
        
        # Analizar datos financieros
        report = await self.analyze_financial_data(data_file_path)
        
        if report:
            # Guardar reporte
            filepath = await self.save_report(report)
            
            print("Analisis completado exitosamente:")
            print(f"Reporte guardado en: {filepath}")
            print(f"Resumen ejecutivo: {report.get('summary', 'N/A')[:200]}...")
            
            return filepath
        else:
            print("No se pudo completar el analisis")
            return ""


async def main():
    """Función principal para probar el agente"""
    # Cargar API key desde variables de entorno
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY no encontrada en variables de entorno")
        return
    
    # Buscar el archivo de datos más reciente
    data_dir = "data"
    if not os.path.exists(data_dir):
        print("No se encontro el directorio de datos")
        return
    
    data_files = [f for f in os.listdir(data_dir) if f.startswith('stock_data_') and f.endswith('.json')]
    if not data_files:
        print("No se encontraron archivos de datos")
        return
    
    # Usar el archivo más reciente
    latest_file = sorted(data_files)[-1]
    data_file_path = os.path.join(data_dir, latest_file)
    
    # Crear y ejecutar el agente
    analyst = DataAnalystAgent(api_key)
    result = await analyst.run(data_file_path)
    
    if result:
        print(f"Data Analyst Agent completado. Reporte guardado en: {result}")
    else:
        print("Data Analyst Agent fallo")


if __name__ == "__main__":
    asyncio.run(main())
