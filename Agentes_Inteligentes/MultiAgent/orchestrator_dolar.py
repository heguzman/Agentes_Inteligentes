# -*- coding: utf-8 -*-
"""
Orquestador Principal con DolarAPI Collector como primer agente
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
import json

# Agregar el directorio de agentes al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

from dolar_api_collector import DolarAPICollector
from dolar_analyst_agent import DolarAnalystAgent
from pdf_generator_agent import PDFGeneratorAgent


class MultiAgentOrchestratorDolar:
    """Orquestador principal que coordina todos los agentes del sistema con DolarAPI"""
    
    def __init__(self, api_key: str):
        """Inicializa el orquestador con la API key"""
        self.api_key = api_key
        self.agents = {}
        self.execution_log = []
        
        # Inicializar agentes
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Inicializa todos los agentes del sistema"""
        try:
            print("Inicializando agentes...")
            
            self.agents['dolar_collector'] = DolarAPICollector()
            self.agents['dolar_analyst'] = DolarAnalystAgent(self.api_key)
            self.agents['pdf_generator'] = PDFGeneratorAgent(self.api_key)
            
            print("Todos los agentes inicializados correctamente")
            
        except Exception as e:
            print(f"Error inicializando agentes: {e}")
            raise
    
    async def execute_full_analysis(self) -> Dict:
        """Ejecuta el análisis completo del mercado financiero argentino con datos de DolarAPI"""
        start_time = datetime.now()
        print(f"Iniciando analisis completo del mercado argentino con DolarAPI - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = {
            'start_time': start_time.isoformat(),
            'status': 'running',
            'steps': {},
            'errors': []
        }
        
        try:
            # Paso 1: DolarAPI Collector
            print("\n" + "="*60)
            print("PASO 1: RECOLECCION DE DATOS DE DOLARAPI")
            print("="*60)
            
            dolar_data = await self._execute_dolar_collector()
            if dolar_data:
                results['steps']['dolar_collection'] = {
                    'status': 'success',
                    'output_data': dolar_data,
                    'timestamp': datetime.now().isoformat()
                }
                self._log_step('dolar_collection', 'success', f'Datos obtenidos: {len(dolar_data)} cotizaciones')
            else:
                results['steps']['dolar_collection'] = {
                    'status': 'failed',
                    'error': 'No se pudieron obtener datos de DolarAPI'
                }
                results['errors'].append('Recoleccion de datos DolarAPI fallo')
                self._log_step('dolar_collection', 'failed', 'No se obtuvieron datos de DolarAPI')
                return results
            
            # Paso 2: Análisis de Datos de DolarAPI
            print("\n" + "="*60)
            print("PASO 2: ANALISIS DE DATOS DE DOLARAPI")
            print("="*60)
            
            report_file = await self._execute_dolar_analysis(dolar_data)
            if report_file:
                results['steps']['dolar_analysis'] = {
                    'status': 'success',
                    'output_file': report_file,
                    'timestamp': datetime.now().isoformat()
                }
                self._log_step('dolar_analysis', 'success', report_file)
            else:
                results['steps']['dolar_analysis'] = {
                    'status': 'failed',
                    'error': 'No se pudo completar el analisis de datos de DolarAPI'
                }
                results['errors'].append('Analisis de DolarAPI fallo')
                self._log_step('dolar_analysis', 'failed', 'Analisis incompleto')
                return results
            
            # Paso 3: Generación de PDF con Gráficos
            print("\n" + "="*60)
            print("PASO 3: GENERACION DE PDF CON GRAFICOS")
            print("="*60)
            
            pdf_file = await self._execute_pdf_generation(report_file)
            if pdf_file:
                results['steps']['pdf_generation'] = {
                    'status': 'success',
                    'output_file': pdf_file,
                    'timestamp': datetime.now().isoformat()
                }
                self._log_step('pdf_generation', 'success', pdf_file)
            else:
                results['steps']['pdf_generation'] = {
                    'status': 'failed',
                    'error': 'No se pudo generar el PDF'
                }
                results['errors'].append('Generacion de PDF fallo')
                self._log_step('pdf_generation', 'failed', 'PDF no generado')
            
            # Finalizar
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            results['end_time'] = end_time.isoformat()
            results['execution_time_seconds'] = execution_time
            results['status'] = 'completed' if not results['errors'] else 'completed_with_errors'
            
            print("\n" + "="*60)
            print("ANALISIS COMPLETADO")
            print("="*60)
            print(f"Tiempo total de ejecucion: {execution_time:.2f} segundos")
            print(f"Archivos generados:")
            for step, data in results['steps'].items():
                if data['status'] == 'success':
                    if step == 'dolar_collection':
                        print(f"   - {step}: {data['output_data']} cotizaciones")
                    else:
                        print(f"   - {step}: {data['output_file']}")
            
            if results['errors']:
                print(f"Errores encontrados: {len(results['errors'])}")
                for error in results['errors']:
                    print(f"   - {error}")
            
            return results
            
        except Exception as e:
            print(f"Error critico en el orquestador: {e}")
            results['status'] = 'failed'
            results['errors'].append(f'Error critico: {str(e)}')
            results['end_time'] = datetime.now().isoformat()
            return results
    
    async def _execute_dolar_collector(self) -> Optional[List[Dict]]:
        """Ejecuta el agente recolector de DolarAPI"""
        try:
            print("Ejecutando DolarAPI Collector...")
            collector = self.agents['dolar_collector']
            
            # Obtener datos
            data = collector.get_dolar_data()
            
            if data:
                # Guardar en CSV y JSON
                csv_success = collector.save_to_csv(data)
                json_success = collector.save_to_json(data)
                
                # Mostrar datos
                collector.display_data(data)
                
                if csv_success and json_success:
                    print(f"DolarAPI Collector completado: {len(data)} cotizaciones")
                    return data
                else:
                    print("DolarAPI Collector completado con errores en guardado")
                    return data
            else:
                print("DolarAPI Collector fallo")
                return None
                
        except Exception as e:
            print(f"Error en DolarAPI Collector: {e}")
            return None
    
    async def _execute_dolar_analysis(self, dolar_data: List[Dict]) -> Optional[str]:
        """Ejecuta el agente analista de DolarAPI"""
        try:
            print("Ejecutando Dolar Analyst Agent...")
            analyst = self.agents['dolar_analyst']
            
            # Crear un archivo temporal con los datos de DolarAPI
            temp_data_file = await self._create_temp_data_file(dolar_data)
            
            if temp_data_file:
                result = await analyst.run(temp_data_file)
                
                # Limpiar archivo temporal
                try:
                    os.remove(temp_data_file)
                except:
                    pass
                
                if result:
                    print(f"Dolar Analyst completado: {result}")
                    return result
                else:
                    print("Dolar Analyst fallo")
                    return None
            else:
                print("No se pudo crear archivo temporal de datos")
                return None
                
        except Exception as e:
            print(f"Error en Dolar Analyst: {e}")
            return None
    
    async def _create_temp_data_file(self, dolar_data: List[Dict]) -> Optional[str]:
        """Crea un archivo temporal con los datos de DolarAPI para el analista"""
        try:
            # Asegurar que el directorio data existe
            data_dir = "data"
            if not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
            
            # Crear estructura de datos SOLO con datos reales de DolarAPI
            formatted_data = {
                'currency': {
                    'pair': 'USD/ARS',
                    'price': str(dolar_data[0].get('venta', 1450)),  # Usar precio de venta del oficial
                    'timestamp': datetime.now().isoformat(),
                    'source': 'dolar_api'
                },
                'dolar_data': dolar_data,  # Incluir todos los datos de DolarAPI
                'data_type': 'dolar_cotizations_only',
                'note': 'Este analisis se basa unicamente en datos de cotizaciones del dolar de DolarAPI'
            }
            
            # Guardar archivo temporal
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_filename = f"dolar_data_{timestamp}.json"
            temp_filepath = os.path.join(data_dir, temp_filename)
            
            with open(temp_filepath, 'w', encoding='utf-8') as f:
                json.dump(formatted_data, f, indent=2, ensure_ascii=False)
            
            return temp_filepath
            
        except Exception as e:
            print(f"Error creando archivo temporal: {e}")
            return None
    
    async def _execute_pdf_generation(self, report_file: str) -> Optional[str]:
        """Ejecuta el agente de generación de PDF"""
        try:
            print("Ejecutando PDF Generator Agent...")
            pdf_agent = self.agents['pdf_generator']
            result = await pdf_agent.run(report_file)
            
            if result:
                print(f"PDF Generator Agent completado: {result}")
                return result
            else:
                print("PDF Generator Agent fallo")
                return None
                
        except Exception as e:
            print(f"Error en PDF Generator Agent: {e}")
            return None
    
    def _log_step(self, step: str, status: str, details: str):
        """Registra un paso en el log de ejecución"""
        log_entry = {
            'step': step,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.execution_log.append(log_entry)
    
    async def get_system_status(self) -> Dict:
        """Obtiene el estado actual del sistema"""
        return {
            'agents_initialized': len(self.agents),
            'available_agents': list(self.agents.keys()),
            'last_execution_log': self.execution_log[-5:] if self.execution_log else [],
            'system_ready': len(self.agents) == 3,
            'mode': 'dolar_api'
        }


async def main():
    """Función principal para ejecutar el sistema multiagente con DolarAPI"""
    print("Sistema Multiagente de Analisis Financiero Argentina (DolarAPI)")
    print("=" * 60)
    
    # Verificar API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY no encontrada en variables de entorno")
        print("Por favor, configura tu API key de Google en el archivo .env")
        return
    
    try:
        # Inicializar orquestador
        orchestrator = MultiAgentOrchestratorDolar(api_key)
        
        # Verificar estado del sistema
        status = await orchestrator.get_system_status()
        print(f"Estado del sistema: {status}")
        
        if not status['system_ready']:
            print("Sistema no esta listo. Verifica la inicializacion de agentes.")
            return
        
        # Ejecutar análisis completo
        results = await orchestrator.execute_full_analysis()
        
        # Mostrar resultados finales
        print("\n" + "="*60)
        print("RESUMEN FINAL")
        print("="*60)
        print(f"Estado: {results['status']}")
        print(f"Tiempo de ejecucion: {results.get('execution_time_seconds', 0):.2f} segundos")
        
        if results['steps']:
            print("\nPasos completados:")
            for step, data in results['steps'].items():
                status_icon = "OK" if data['status'] == 'success' else "ERROR"
                print(f"  {status_icon} {step}: {data['status']}")
                if data['status'] == 'success':
                    if step == 'dolar_collection':
                        print(f"     Datos: {data['output_data']} cotizaciones")
                    else:
                        print(f"     Archivo: {data['output_file']}")
        
        if results['errors']:
            print(f"\nErrores ({len(results['errors'])}):")
            for error in results['errors']:
                print(f"  - {error}")
        
        # Guardar log de ejecución
        log_file = f"execution_log_dolar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\nLog de ejecucion guardado en: {log_file}")
        
    except Exception as e:
        print(f"Error critico: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
