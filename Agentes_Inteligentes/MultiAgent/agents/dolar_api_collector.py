# -*- coding: utf-8 -*-
"""
Recolector de datos de DolarAPI para obtener cotizaciones del dólar en Argentina
"""

import requests
import csv
import os
from datetime import datetime
from typing import List, Dict
import json


class DolarAPICollector:
    """Recolector de datos de la API de DolarAPI"""
    
    def __init__(self):
        """Inicializa el recolector"""
        self.api_url = "https://dolarapi.com/v1/dolares"
        self.csv_file = "dolar_historico.csv"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_dolar_data(self) -> List[Dict]:
        """Obtiene los datos de cotización del dólar desde la API"""
        try:
            print(f"Obteniendo datos de: {self.api_url}")
            response = self.session.get(self.api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            print(f"Datos obtenidos exitosamente: {len(data)} cotizaciones")
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"Error obteniendo datos de la API: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error decodificando JSON: {e}")
            return []
        except Exception as e:
            print(f"Error inesperado: {e}")
            return []
    
    def save_to_csv(self, data: List[Dict]) -> bool:
        """Guarda los datos en un archivo CSV"""
        if not data:
            print("No hay datos para guardar")
            return False
        
        try:
            # Verificar si el archivo existe para determinar si necesitamos headers
            file_exists = os.path.exists(self.csv_file)
            
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'fecha_consulta',
                    'moneda',
                    'casa',
                    'nombre',
                    'compra',
                    'venta',
                    'fecha_actualizacion'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Escribir headers solo si el archivo no existe
                if not file_exists:
                    writer.writeheader()
                    print(f"Archivo CSV creado: {self.csv_file}")
                
                # Agregar timestamp de consulta
                consulta_timestamp = datetime.now().isoformat()
                
                # Escribir cada registro
                for item in data:
                    row = {
                        'fecha_consulta': consulta_timestamp,
                        'moneda': item.get('moneda', ''),
                        'casa': item.get('casa', ''),
                        'nombre': item.get('nombre', ''),
                        'compra': item.get('compra', ''),
                        'venta': item.get('venta', ''),
                        'fecha_actualizacion': item.get('fechaActualizacion', '')
                    }
                    writer.writerow(row)
                
                print(f"Datos guardados en CSV: {len(data)} registros")
                return True
                
        except Exception as e:
            print(f"Error guardando datos en CSV: {e}")
            return False
    
    def save_to_json(self, data: List[Dict]) -> bool:
        """Guarda los datos en un archivo JSON con timestamp"""
        if not data:
            print("No hay datos para guardar")
            return False
        
        try:
            # Crear directorio data si no existe
            data_dir = "data"
            if not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_file = f"dolar_data_{timestamp}.json"
            json_path = os.path.join(data_dir, json_file)
            
            # Agregar metadata
            json_data = {
                'timestamp_consulta': datetime.now().isoformat(),
                'total_cotizaciones': len(data),
                'fuente': 'DolarAPI',
                'datos': data
            }
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            print(f"Datos guardados en JSON: {json_file}")
            return True
            
        except Exception as e:
            print(f"Error guardando datos en JSON: {e}")
            return False
    
    def display_data(self, data: List[Dict]):
        """Muestra los datos obtenidos de forma legible"""
        if not data:
            print("No hay datos para mostrar")
            return
        
        print("\n" + "="*80)
        print("COTIZACIONES DEL DOLAR - ARGENTINA")
        print("="*80)
        print(f"{'Casa':<20} {'Compra':<10} {'Venta':<10} {'Actualización'}")
        print("-"*80)
        
        for item in data:
            casa = item.get('nombre', 'N/A')
            compra = item.get('compra', 'N/A')
            venta = item.get('venta', 'N/A')
            fecha = item.get('fechaActualizacion', 'N/A')
            
            # Formatear fecha para mostrar solo la parte relevante
            if fecha != 'N/A':
                try:
                    fecha_obj = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
                    fecha_str = fecha_obj.strftime('%H:%M')
                except:
                    fecha_str = fecha
            else:
                fecha_str = 'N/A'
            
            print(f"{casa:<20} {compra:<10} {venta:<10} {fecha_str}")
        
        print("="*80)
    
    def run(self):
        """Ejecuta el proceso completo de recolección y almacenamiento"""
        print("Iniciando recolección de datos de DolarAPI...")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Obtener datos
        data = self.get_dolar_data()
        
        if data:
            # Mostrar datos
            self.display_data(data)
            
            # Guardar en CSV
            csv_success = self.save_to_csv(data)
            
            # Guardar en JSON
            json_success = self.save_to_json(data)
            
            if csv_success and json_success:
                print("\nProceso completado exitosamente!")
                print(f"Archivos generados:")
                print(f"  - CSV: {self.csv_file}")
                print(f"  - JSON: dolar_data_[timestamp].json")
            else:
                print("\nProceso completado con errores en el guardado")
        else:
            print("\nNo se pudieron obtener datos de la API")


def main():
    """Función principal"""
    collector = DolarAPICollector()
    collector.run()


if __name__ == "__main__":
    main()
