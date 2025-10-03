# -*- coding: utf-8 -*-
"""
PDF Generator Agent para crear reportes PDF con gráficos de cotizaciones del dólar
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
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
import base64

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo


class PDFGeneratorAgent:
    """Agente especializado en generar reportes PDF con gráficos de cotizaciones"""
    
    def __init__(self, api_key: str):
        """Inicializa el agente generador de PDF"""
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
            name="pdf_generator",
            model_client=model_client
        )
    
    async def create_pdf_report(self, report_file_path: str) -> str:
        """Crea un reporte PDF con gráficos de cotizaciones"""
        try:
            # Cargar reporte de análisis
            with open(report_file_path, 'r', encoding='utf-8') as f:
                report = json.load(f)
            
            # Crear gráficos
            charts = await self._create_charts(report)
            
            # Generar PDF
            pdf_file = await self._generate_pdf(report, charts)
            
            return pdf_file
            
        except Exception as e:
            print(f"Error creando reporte PDF: {e}")
            return ""
    
    async def _create_charts(self, report: Dict) -> List[Dict]:
        """Crea gráficos basados en los datos del reporte"""
        charts = []
        
        try:
            # Gráfico 1: Cotizaciones del dólar
            cotizations_chart = await self._create_cotizations_chart(report)
            if cotizations_chart:
                charts.append(cotizations_chart)
            
            # Gráfico 2: Brechas cambiarias
            gaps_chart = await self._create_gaps_chart(report)
            if gaps_chart:
                charts.append(gaps_chart)
            
            # Gráfico 3: Spreads de compra-venta
            spreads_chart = await self._create_spreads_chart(report)
            if spreads_chart:
                charts.append(spreads_chart)
            
            # Gráfico 4: Comparación de precios
            comparison_chart = await self._create_comparison_chart(report)
            if comparison_chart:
                charts.append(comparison_chart)
            
        except Exception as e:
            print(f"Error creando gráficos: {e}")
        
        return charts
    
    async def _create_cotizations_chart(self, report: Dict) -> Optional[Dict]:
        """Crea gráfico de cotizaciones del dólar"""
        try:
            cotizations_data = report.get('cotizations_analysis', {}).get('cotizations', [])
            if not cotizations_data:
                return None
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # Preparar datos
            nombres = [c.get('nombre', 'N/A') for c in cotizations_data]
            compras = [c.get('compra', 0) for c in cotizations_data]
            ventas = [c.get('venta', 0) for c in cotizations_data]
            
            # Gráfico de precios de compra
            bars1 = ax1.bar(nombres, compras, color='lightblue', alpha=0.7, label='Compra')
            ax1.set_title('Cotizaciones del Dólar - Precios de Compra', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Precio (ARS)')
            ax1.tick_params(axis='x', rotation=45)
            ax1.grid(True, alpha=0.3)
            
            # Agregar valores en las barras
            for bar, price in zip(bars1, compras):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{price}', ha='center', va='bottom', fontsize=10)
            
            # Gráfico de precios de venta
            bars2 = ax2.bar(nombres, ventas, color='lightcoral', alpha=0.7, label='Venta')
            ax2.set_title('Cotizaciones del Dólar - Precios de Venta', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Precio (ARS)')
            ax2.tick_params(axis='x', rotation=45)
            ax2.grid(True, alpha=0.3)
            
            # Agregar valores en las barras
            for bar, price in zip(bars2, ventas):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{price}', ha='center', va='bottom', fontsize=10)
            
            plt.tight_layout()
            
            # Convertir a base64
            chart_data = await self._chart_to_base64(fig)
            plt.close(fig)
            
            return {
                'type': 'cotizations',
                'title': 'Cotizaciones del Dólar',
                'data': chart_data,
                'description': 'Comparación de precios de compra y venta por tipo de cotización'
            }
            
        except Exception as e:
            print(f"Error creando gráfico de cotizaciones: {e}")
            return None
    
    async def _create_gaps_chart(self, report: Dict) -> Optional[Dict]:
        """Crea gráfico de brechas cambiarias"""
        try:
            gaps_data = report.get('gaps_analysis', {}).get('gaps', {})
            if not gaps_data:
                return None
            
            fig, ax = plt.subplots(1, 1, figsize=(12, 6))
            
            # Preparar datos
            casas = list(gaps_data.keys())
            gaps = [gaps_data[casa]['gap_percentage'] for casa in casas]
            colors_list = ['red' if gap > 0 else 'green' for gap in gaps]
            
            # Gráfico de brechas
            bars = ax.bar(casas, gaps, color=colors_list, alpha=0.7)
            ax.set_title('Brechas Cambiarias vs Dólar Oficial', fontsize=14, fontweight='bold')
            ax.set_ylabel('Brecha (%)')
            ax.tick_params(axis='x', rotation=45)
            ax.grid(True, alpha=0.3)
            ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            # Agregar valores en las barras
            for bar, gap in zip(bars, gaps):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{gap:.2f}%', ha='center', va='bottom' if height > 0 else 'top', fontsize=10)
            
            plt.tight_layout()
            
            # Convertir a base64
            chart_data = await self._chart_to_base64(fig)
            plt.close(fig)
            
            return {
                'type': 'gaps',
                'title': 'Brechas Cambiarias',
                'data': chart_data,
                'description': 'Diferencias porcentuales respecto al dólar oficial'
            }
            
        except Exception as e:
            print(f"Error creando gráfico de brechas: {e}")
            return None
    
    async def _create_spreads_chart(self, report: Dict) -> Optional[Dict]:
        """Crea gráfico de spreads de compra-venta"""
        try:
            trends_data = report.get('trends_analysis', {}).get('prices_analysis', {})
            if not trends_data:
                return None
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Preparar datos
            casas = list(trends_data.keys())
            spreads = [trends_data[casa]['spread'] for casa in casas]
            spreads_pct = [trends_data[casa]['spread_percentage'] for casa in casas]
            
            # Gráfico de spreads absolutos
            bars1 = ax1.bar(casas, spreads, color='orange', alpha=0.7)
            ax1.set_title('Spreads Absolutos (ARS)', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Spread (ARS)')
            ax1.tick_params(axis='x', rotation=45)
            ax1.grid(True, alpha=0.3)
            
            # Agregar valores
            for bar, spread in zip(bars1, spreads):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{spread:.1f}', ha='center', va='bottom', fontsize=9)
            
            # Gráfico de spreads porcentuales
            bars2 = ax2.bar(casas, spreads_pct, color='purple', alpha=0.7)
            ax2.set_title('Spreads Porcentuales (%)', fontsize=12, fontweight='bold')
            ax2.set_ylabel('Spread (%)')
            ax2.tick_params(axis='x', rotation=45)
            ax2.grid(True, alpha=0.3)
            
            # Agregar valores
            for bar, spread_pct in zip(bars2, spreads_pct):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{spread_pct:.2f}%', ha='center', va='bottom', fontsize=9)
            
            plt.tight_layout()
            
            # Convertir a base64
            chart_data = await self._chart_to_base64(fig)
            plt.close(fig)
            
            return {
                'type': 'spreads',
                'title': 'Spreads de Compra-Venta',
                'data': chart_data,
                'description': 'Diferencias entre precios de compra y venta'
            }
            
        except Exception as e:
            print(f"Error creando gráfico de spreads: {e}")
            return None
    
    async def _create_comparison_chart(self, report: Dict) -> Optional[Dict]:
        """Crea gráfico de comparación de precios"""
        try:
            cotizations_data = report.get('cotizations_analysis', {}).get('cotizations', [])
            if not cotizations_data:
                return None
            
            fig, ax = plt.subplots(1, 1, figsize=(14, 8))
            
            # Preparar datos
            nombres = [c.get('nombre', 'N/A') for c in cotizations_data]
            ventas = [c.get('venta', 0) for c in cotizations_data]
            
            # Crear gráfico de barras horizontales
            bars = ax.barh(nombres, ventas, color='steelblue', alpha=0.7)
            ax.set_title('Comparación de Precios de Venta - Dólar Argentino', fontsize=14, fontweight='bold')
            ax.set_xlabel('Precio de Venta (ARS)')
            ax.grid(True, alpha=0.3, axis='x')
            
            # Agregar valores en las barras
            for i, (bar, price) in enumerate(zip(bars, ventas)):
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2.,
                        f'${price:,.0f}', ha='left', va='center', fontsize=10, fontweight='bold')
            
            # Destacar el dólar oficial
            oficial_idx = next((i for i, n in enumerate(nombres) if 'Oficial' in n), None)
            if oficial_idx is not None:
                bars[oficial_idx].set_color('red')
                bars[oficial_idx].set_alpha(0.8)
            
            plt.tight_layout()
            
            # Convertir a base64
            chart_data = await self._chart_to_base64(fig)
            plt.close(fig)
            
            return {
                'type': 'comparison',
                'title': 'Comparación de Precios',
                'data': chart_data,
                'description': 'Comparación visual de todas las cotizaciones del dólar'
            }
            
        except Exception as e:
            print(f"Error creando gráfico de comparación: {e}")
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
    
    async def _generate_pdf(self, report: Dict, charts: List[Dict]) -> str:
        """Genera el archivo PDF con los gráficos y análisis"""
        try:
            # Crear nombre de archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dolar_report_{timestamp}.pdf"
            
            # Asegurar que el directorio existe
            pdf_dir = "presentations"
            if not os.path.exists(pdf_dir):
                os.makedirs(pdf_dir, exist_ok=True)
            
            filepath = os.path.join(pdf_dir, filename)
            
            # Crear documento PDF
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            story = []
            
            # Estilos
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                textColor=colors.darkblue
            )
            
            # Título principal
            story.append(Paragraph("Reporte de Cotizaciones del Dólar", title_style))
            story.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Resumen ejecutivo
            story.append(Paragraph("Resumen Ejecutivo", heading_style))
            summary = report.get('summary', 'No hay resumen disponible.')
            story.append(Paragraph(summary, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Datos de cotizaciones
            cotizations_data = report.get('cotizations_analysis', {}).get('cotizations', [])
            if cotizations_data:
                story.append(Paragraph("Datos de Cotizaciones", heading_style))
                
                # Crear tabla de datos
                table_data = [['Tipo', 'Compra (ARS)', 'Venta (ARS)', 'Actualización']]
                for cot in cotizations_data:
                    table_data.append([
                        cot.get('nombre', 'N/A'),
                        f"${cot.get('compra', 0):,.0f}",
                        f"${cot.get('venta', 0):,.0f}",
                        cot.get('fechaActualizacion', 'N/A')[:16]
                    ])
                
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(table)
                story.append(Spacer(1, 20))
            
            # Agregar gráficos
            for chart in charts:
                story.append(Paragraph(chart['title'], heading_style))
                story.append(Paragraph(chart['description'], styles['Normal']))
                story.append(Spacer(1, 10))
                
                # Convertir base64 a imagen
                try:
                    image_data = base64.b64decode(chart['data'])
                    img_buffer = BytesIO(image_data)
                    
                    # Crear imagen para PDF
                    img = Image(img_buffer, width=6*inch, height=4*inch)
                    story.append(img)
                    story.append(Spacer(1, 20))
                    
                except Exception as e:
                    print(f"Error agregando gráfico al PDF: {e}")
                    story.append(Paragraph("Error al cargar gráfico", styles['Normal']))
            
            # Análisis detallado
            story.append(Paragraph("Análisis Detallado", heading_style))
            
            # Análisis de cotizaciones
            cot_analysis = report.get('cotizations_analysis', {}).get('analysis', '')
            if cot_analysis:
                story.append(Paragraph("Análisis de Cotizaciones", styles['Heading3']))
                story.append(Paragraph(cot_analysis[:1000] + "...", styles['Normal']))
                story.append(Spacer(1, 10))
            
            # Análisis de brechas
            gaps_analysis = report.get('gaps_analysis', {}).get('analysis', '')
            if gaps_analysis:
                story.append(Paragraph("Análisis de Brechas Cambiarias", styles['Heading3']))
                story.append(Paragraph(gaps_analysis[:1000] + "...", styles['Normal']))
                story.append(Spacer(1, 10))
            
            # Análisis de tendencias
            trends_analysis = report.get('trends_analysis', {}).get('analysis', '')
            if trends_analysis:
                story.append(Paragraph("Análisis de Tendencias", styles['Heading3']))
                story.append(Paragraph(trends_analysis[:1000] + "...", styles['Normal']))
            
            # Pie de página
            story.append(Spacer(1, 30))
            story.append(Paragraph("Reporte generado automáticamente por el Sistema Multiagente de Análisis Financiero", 
                                 styles['Normal']))
            story.append(Paragraph(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                                 styles['Normal']))
            
            # Construir PDF
            doc.build(story)
            
            print(f"Reporte PDF generado: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error generando PDF: {e}")
            return ""
    
    async def run(self, report_file_path: str) -> str:
        """Ejecuta el agente generador de PDF"""
        print("Iniciando PDF Generator Agent...")
        
        # Crear reporte PDF
        pdf_file = await self.create_pdf_report(report_file_path)
        
        if pdf_file:
            print("Reporte PDF creado exitosamente:")
            print(f"Archivo PDF: {pdf_file}")
            return pdf_file
        else:
            print("No se pudo crear el reporte PDF")
            return ""


async def main():
    """Función principal para probar el agente"""
    # Cargar API key desde variables de entorno
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY no encontrada en variables de entorno")
        return
    
    # Buscar el archivo de reporte más reciente
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        print("No se encontro el directorio de reportes")
        return
    
    report_files = [f for f in os.listdir(reports_dir) if f.startswith('dolar_report_') and f.endswith('.json')]
    if not report_files:
        print("No se encontraron archivos de reporte de DolarAPI")
        return
    
    # Usar el archivo más reciente
    latest_file = sorted(report_files)[-1]
    report_file_path = os.path.join(reports_dir, latest_file)
    
    # Crear y ejecutar el agente
    pdf_generator = PDFGeneratorAgent(api_key)
    result = await pdf_generator.run(report_file_path)
    
    if result:
        print(f"PDF Generator Agent completado. Reporte guardado en: {result}")
    else:
        print("PDF Generator Agent fallo")


if __name__ == "__main__":
    asyncio.run(main())
