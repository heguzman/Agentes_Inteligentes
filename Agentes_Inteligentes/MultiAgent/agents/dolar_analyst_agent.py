# -*- coding: utf-8 -*-
"""
Dolar Analyst Agent para analizar específicamente datos de DolarAPI
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo


class DolarAnalystAgent:
    """Agente especializado en análisis de datos de DolarAPI"""
    
    def __init__(self, api_key: str):
        """Inicializa el agente analista de DolarAPI"""
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
            name="dolar_analyst",
            model_client=model_client
        )
    
    async def analyze_dolar_data(self, data_file_path: str) -> Dict:
        """Analiza los datos de DolarAPI y genera insights"""
        try:
            # Cargar datos del archivo
            with open(data_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Verificar que son datos de DolarAPI
            if data.get('data_type') != 'dolar_cotizations_only':
                print("Advertencia: Los datos no parecen ser específicos de DolarAPI")
            
            dolar_data = data.get('dolar_data', [])
            if not dolar_data:
                return {'error': 'No se encontraron datos de DolarAPI'}
            
            # Análisis de las diferentes cotizaciones
            cotizations_analysis = await self._analyze_cotizations(dolar_data)
            
            # Análisis de brechas cambiarias
            gaps_analysis = await self._analyze_exchange_gaps(dolar_data)
            
            # Análisis de tendencias
            trends_analysis = await self._analyze_trends(dolar_data)
            
            # Generar reporte consolidado
            report = {
                'timestamp': datetime.now().isoformat(),
                'data_source': 'DolarAPI',
                'cotizations_analysis': cotizations_analysis,
                'gaps_analysis': gaps_analysis,
                'trends_analysis': trends_analysis,
                'summary': await self._generate_executive_summary(dolar_data)
            }
            
            return report
            
        except Exception as e:
            print(f"Error analizando datos de DolarAPI: {e}")
            return {}
    
    async def _analyze_cotizations(self, dolar_data: List[Dict]) -> Dict:
        """Analiza las diferentes cotizaciones del dólar"""
        try:
            analysis_prompt = f"""
            Analiza las siguientes cotizaciones del dólar en Argentina obtenidas de DolarAPI:
            
            {json.dumps(dolar_data, indent=2, ensure_ascii=False)}
            
            Proporciona un análisis detallado que incluya:
            1. Interpretación de cada tipo de cotización (oficial, blue, bolsa, etc.)
            2. Diferencias entre las cotizaciones y su significado
            3. Factores que influyen en cada tipo de cotización
            4. Implicaciones para diferentes tipos de usuarios (inversores, empresas, consumidores)
            5. Recomendaciones específicas para cada tipo de cotización
            """
            
            result = await self.assistant_agent.run(task=analysis_prompt)
            analysis = result.messages[-1].content
            
            return {
                'total_cotizations': len(dolar_data),
                'cotizations': dolar_data,
                'analysis': analysis
            }
            
        except Exception as e:
            print(f"Error analizando cotizaciones: {e}")
            return {'error': str(e)}
    
    async def _analyze_exchange_gaps(self, dolar_data: List[Dict]) -> Dict:
        """Analiza las brechas cambiarias entre diferentes cotizaciones"""
        try:
            # Calcular brechas
            gaps = {}
            oficial = None
            
            for cotization in dolar_data:
                if cotization.get('casa') == 'oficial':
                    oficial = cotization
                    break
            
            if oficial:
                oficial_venta = oficial.get('venta', 0)
                for cotization in dolar_data:
                    if cotization.get('casa') != 'oficial':
                        casa = cotization.get('casa')
                        venta = cotization.get('venta', 0)
                        gap = ((venta - oficial_venta) / oficial_venta) * 100
                        gaps[casa] = {
                            'gap_percentage': round(gap, 2),
                            'gap_amount': round(venta - oficial_venta, 2),
                            'cotization': cotization
                        }
            
            analysis_prompt = f"""
            Analiza las brechas cambiarias en Argentina basándote en estos datos:
            
            Cotización Oficial: {oficial.get('venta') if oficial else 'N/A'}
            Brechas calculadas: {json.dumps(gaps, indent=2, ensure_ascii=False)}
            
            Proporciona:
            1. Interpretación de las brechas cambiarias
            2. Factores que generan estas diferencias
            3. Impacto económico de las brechas
            4. Perspectivas sobre la convergencia o divergencia
            5. Recomendaciones para diferentes actores económicos
            """
            
            result = await self.assistant_agent.run(task=analysis_prompt)
            analysis = result.messages[-1].content
            
            return {
                'oficial_cotization': oficial,
                'gaps': gaps,
                'analysis': analysis
            }
            
        except Exception as e:
            print(f"Error analizando brechas: {e}")
            return {'error': str(e)}
    
    async def _analyze_trends(self, dolar_data: List[Dict]) -> Dict:
        """Analiza tendencias en las cotizaciones"""
        try:
            # Extraer precios para análisis
            prices = {}
            for cotization in dolar_data:
                casa = cotization.get('casa')
                compra = cotization.get('compra', 0)
                venta = cotization.get('venta', 0)
                prices[casa] = {
                    'compra': compra,
                    'venta': venta,
                    'spread': round(venta - compra, 2),
                    'spread_percentage': round(((venta - compra) / compra) * 100, 2) if compra > 0 else 0
                }
            
            analysis_prompt = f"""
            Analiza las tendencias del mercado cambiario argentino basándote en estos datos:
            
            Precios y spreads: {json.dumps(prices, indent=2, ensure_ascii=False)}
            
            Proporciona:
            1. Análisis de los spreads entre compra y venta
            2. Identificación de patrones en las cotizaciones
            3. Factores que influyen en las tendencias
            4. Perspectivas a corto y mediano plazo
            5. Recomendaciones estratégicas
            """
            
            result = await self.assistant_agent.run(task=analysis_prompt)
            analysis = result.messages[-1].content
            
            return {
                'prices_analysis': prices,
                'analysis': analysis
            }
            
        except Exception as e:
            print(f"Error analizando tendencias: {e}")
            return {'error': str(e)}
    
    async def _generate_executive_summary(self, dolar_data: List[Dict]) -> str:
        """Genera un resumen ejecutivo del análisis de DolarAPI"""
        try:
            summary_prompt = f"""
            Genera un resumen ejecutivo del análisis de cotizaciones del dólar en Argentina:
            
            Datos de DolarAPI:
            {json.dumps(dolar_data, indent=2, ensure_ascii=False)}
            
            El resumen debe incluir:
            1. Puntos clave del mercado cambiario argentino
            2. Conclusiones principales sobre las cotizaciones
            3. Recomendaciones para diferentes tipos de usuarios
            4. Perspectivas para el próximo período
            
            Formato: Máximo 3 párrafos, lenguaje claro y directo, enfocado en cotizaciones del dólar.
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
            filename = f"dolar_report_{timestamp}.json"
        
        # Asegurar que el directorio existe
        reports_dir = "reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir, exist_ok=True)
        
        filepath = os.path.join(reports_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"Reporte de DolarAPI guardado en: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error guardando reporte: {e}")
            return ""
    
    async def run(self, data_file_path: str) -> str:
        """Ejecuta el agente analista de DolarAPI"""
        print("Iniciando Dolar Analyst Agent...")
        
        # Analizar datos de DolarAPI
        report = await self.analyze_dolar_data(data_file_path)
        
        if report:
            # Guardar reporte
            filepath = await self.save_report(report)
            
            print("Analisis de DolarAPI completado exitosamente:")
            print(f"Reporte guardado en: {filepath}")
            print(f"Resumen ejecutivo: {report.get('summary', 'N/A')[:200]}...")
            
            return filepath
        else:
            print("No se pudo completar el analisis de DolarAPI")
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
    
    data_files = [f for f in os.listdir(data_dir) if f.startswith('dolar_data_') and f.endswith('.json')]
    if not data_files:
        print("No se encontraron archivos de datos de DolarAPI")
        return
    
    # Usar el archivo más reciente
    latest_file = sorted(data_files)[-1]
    data_file_path = os.path.join(data_dir, latest_file)
    
    # Crear y ejecutar el agente
    analyst = DolarAnalystAgent(api_key)
    result = await analyst.run(data_file_path)
    
    if result:
        print(f"Dolar Analyst Agent completado. Reporte guardado en: {result}")
    else:
        print("Dolar Analyst Agent fallo")


if __name__ == "__main__":
    asyncio.run(main())
