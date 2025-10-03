# -*- coding: utf-8 -*-
"""
Generador de datos mock para testing del sistema multiagente
"""

import json
import os
from datetime import datetime
from typing import Dict, List
import random


class MockDataGenerator:
    """Generador de datos financieros mock para testing"""
    
    def __init__(self):
        """Inicializa el generador de datos mock"""
        self.argentine_stocks = ['GGAL', 'PAMP', 'TXAR', 'YPFD', 'MIRG', 'BBAR', 'CRES', 'EDN', 'HARG', 'LOMA']
        self.base_prices = {
            'GGAL': 1200.50,
            'PAMP': 850.25,
            'TXAR': 450.75,
            'YPFD': 6780.00,
            'MIRG': 320.80,
            'BBAR': 950.40,
            'CRES': 1250.60,
            'EDN': 780.30,
            'HARG': 560.90,
            'LOMA': 890.15
        }
    
    def generate_mock_data(self) -> Dict:
        """Genera datos financieros mock"""
        timestamp = datetime.now().isoformat()
        
        # Generar datos del MERVAL
        merval_base = 1200000.0
        merval_change = random.uniform(-3.0, 3.0)
        merval_price = merval_base * (1 + merval_change / 100)
        
        merval_data = {
            'index': 'MERVAL',
            'price': f"{merval_price:,.2f}",
            'change': f"{merval_change:+.2f}%",
            'timestamp': timestamp,
            'source': 'mock_data'
        }
        
        # Generar datos de acciones individuales
        stocks_data = []
        for symbol in self.argentine_stocks:
            base_price = self.base_prices[symbol]
            change_percent = random.uniform(-5.0, 5.0)
            new_price = base_price * (1 + change_percent / 100)
            
            stock_data = {
                'symbol': symbol,
                'price': f"{new_price:,.2f}",
                'change': f"{change_percent:+.2f}%",
                'timestamp': timestamp,
                'source': 'mock_data'
            }
            stocks_data.append(stock_data)
        
        # Generar datos de divisas
        usd_ars_base = 1200.0
        usd_ars_change = random.uniform(-2.0, 2.0)
        usd_ars_price = usd_ars_base * (1 + usd_ars_change / 100)
        
        currency_data = {
            'pair': 'USD/ARS',
            'price': f"{usd_ars_price:,.2f}",
            'timestamp': timestamp,
            'source': 'mock_data'
        }
        
        return {
            'merval': merval_data,
            'stocks': stocks_data,
            'currency': currency_data,
            'generated_at': timestamp,
            'data_type': 'mock_financial_data'
        }
    
    def save_mock_data(self, data: Dict, filename: str = None) -> str:
        """Guarda los datos mock en un archivo JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mock_stock_data_{timestamp}.json"
        
        # Asegurar que el directorio existe
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
        
        filepath = os.path.join(data_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"Datos mock guardados en: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error guardando datos mock: {e}")
            return ""


def main():
    """Función principal para generar datos mock"""
    print("Generando datos financieros mock...")
    
    generator = MockDataGenerator()
    data = generator.generate_mock_data()
    
    filepath = generator.save_mock_data(data)
    
    if filepath:
        print(f"Datos mock generados exitosamente: {filepath}")
        print(f"Total de acciones: {len(data['stocks'])}")
        print(f"MERVAL: {data['merval']['price']} ({data['merval']['change']})")
        print(f"USD/ARS: {data['currency']['price']}")
    else:
        print("Error generando datos mock")


if __name__ == "__main__":
    main()
