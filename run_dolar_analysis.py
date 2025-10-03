#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de ejecución para el Sistema Multiagente con DolarAPI
Ejecutar desde la raíz del proyecto: python run_dolar_analysis.py
"""

import asyncio
import sys
import os
from datetime import datetime

# Agregar el directorio MultiAgent al path
multiagent_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Agentes_Inteligentes', 'MultiAgent')
sys.path.append(multiagent_path)

from config import Config
from orchestrator_dolar import MultiAgentOrchestratorDolar


def print_banner():
    """Imprime el banner del sistema"""
    print("=" * 60)
    print("SISTEMA MULTIAGENTE DE ANALISIS FINANCIERO ARGENTINA")
    print("MODO: DOLARAPI - DATOS REALES")
    print("=" * 60)
    print("- DolarAPI Collector    -> Obtiene cotizaciones reales del dolar")
    print("- Dolar Analyst Agent   -> Analiza y genera reportes")
    print("- PDF Generator Agent   -> Crea presentaciones con graficos")
    print("Desarrollado con autogen + Gemini + DolarAPI")
    print("=" * 60)


async def run_complete_analysis():
    """Ejecuta el análisis completo con datos reales de DolarAPI"""
    print("Iniciando analisis completo con datos reales de DolarAPI...")
    
    try:
        orchestrator = MultiAgentOrchestratorDolar(Config.GOOGLE_API_KEY)
        results = await orchestrator.execute_full_analysis()
        
        if results['status'] == 'completed':
            print("\nAnalisis completado exitosamente!")
            print("Archivos generados:")
            for step, data in results['steps'].items():
                if data['status'] == 'success':
                    if step == 'dolar_collection':
                        print(f"   OK {step}: {data['output_data']} cotizaciones")
                    else:
                        print(f"   OK {step}: {data['output_file']}")
        else:
            print(f"\nAnalisis completado con errores: {results['status']}")
            if results['errors']:
                print("Errores encontrados:")
                for error in results['errors']:
                    print(f"   ERROR: {error}")
        
        return results
        
    except Exception as e:
        print(f"Error ejecutando analisis completo: {e}")
        return None


async def main():
    """Función principal del script"""
    print_banner()
    
    # Validar configuración
    print("Validando configuracion...")
    config_errors = Config.validate_config()
    
    if config_errors:
        print("Errores de configuracion:")
        for error in config_errors:
            print(f"   - {error}")
        print("\nPor favor, corrige estos errores antes de continuar.")
        return
    
    print("Configuracion validada correctamente")
    
    # Ejecutar análisis completo
    print("\nEjecutando analisis completo del mercado argentino (DolarAPI)...")
    results = await run_complete_analysis()
    
    if results:
        print("\n" + "=" * 60)
        print("RESUMEN FINAL")
        print("=" * 60)
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
        
        # Mostrar archivos generados
        print("\n" + "=" * 60)
        print("ARCHIVOS GENERADOS")
        print("=" * 60)
        
        # Verificar directorios en MultiAgent
        multiagent_dirs = ['data', 'reports', 'presentations']
        for directory in multiagent_dirs:
            dir_path = os.path.join(multiagent_path, directory)
            if os.path.exists(dir_path):
                files = [f for f in os.listdir(dir_path) if f.endswith(('.json', '.pdf', '.csv'))]
                if files:
                    print(f"\n{directory.upper()}:")
                    for file in sorted(files)[-3:]:  # Mostrar los últimos 3 archivos
                        filepath = os.path.join(dir_path, file)
                        size = os.path.getsize(filepath)
                        print(f"  - {file} ({size} bytes)")
        
        # Verificar archivos CSV en MultiAgent
        csv_path = os.path.join(multiagent_path, 'dolar_historico.csv')
        if os.path.exists(csv_path):
            size = os.path.getsize(csv_path)
            print(f"\nCSV FILES:")
            print(f"  - dolar_historico.csv ({size} bytes)")
    
    print("\nProceso completado.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProceso interrumpido por el usuario.")
    except Exception as e:
        print(f"Error critico: {e}")
        import traceback
        traceback.print_exc()
