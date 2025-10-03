# 🤖 Sistema Multiagente de Análisis Financiero Argentina

Un sistema inteligente que utiliza múltiples agentes especializados para obtener, analizar y presentar datos financieros del mercado argentino en tiempo real.

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ DolarAPI        │───▶│   Dolar         │───▶│   PDF           │
│ Collector       │    │   Analyst       │    │   Generator     │
│ Agent           │    │   Agent         │    │   Agent         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Dolar Data      │    │ Analysis Report │    │ PDF Report      │
│ (JSON/CSV)      │    │ (JSON)          │    │ (PDF + Charts)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🎯 Agentes Especializados

### 1. 💰 DolarAPI Collector Agent
- **Función**: Obtiene cotizaciones del dólar en tiempo real
- **Fuente**: DolarAPI (https://dolarapi.com/v1/dolares)
- **Datos**: 7 tipos de cotizaciones (oficial, blue, bolsa, CCL, etc.)
- **Output**: Archivos CSV históricos y JSON con datos estructurados

### 2. 📊 Dolar Analyst Agent
- **Función**: Analiza cotizaciones del dólar y genera insights
- **Capacidades**: Análisis de brechas cambiarias, spreads, tendencias
- **IA**: Utiliza Gemini para análisis inteligente del mercado cambiario
- **Output**: Reportes detallados en JSON con análisis especializado

### 3. 📄 PDF Generator Agent
- **Función**: Crea reportes PDF profesionales con gráficos
- **Gráficos**: Matplotlib + Seaborn + ReportLab
- **Output**: Archivos PDF con visualizaciones y análisis completo
- **Características**: Gráficos de cotizaciones, brechas, spreads, comparaciones

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.10+
- API Key de Google (para Gemini)

### Dependencias
```bash
# Dependencias principales
pip install autogen-ext openai tiktoken python-dotenv nest-asyncio

# Dependencias para web scraping
pip install requests beautifulsoup4 pandas

# Dependencias para gráficos y PDF
pip install matplotlib seaborn reportlab
```

### Configuración
1. **Variables de entorno**: Crea un archivo `.env` en la raíz del proyecto:
   ```
   GOOGLE_API_KEY=tu_api_key_de_google_aqui
   ```

2. **Estructura de directorios**: El sistema creará automáticamente:
   ```
   MultiAgent/
   ├── agents/          # Agentes especializados
   ├── data/           # Datos financieros (JSON)
   ├── reports/        # Reportes de análisis (JSON)
   ├── presentations/  # Presentaciones HTML
   └── config.py       # Configuración centralizada
   ```

## 🎮 Uso del Sistema

### Ejecución Completa
```bash
cd Agentes_Inteligentes/MultiAgent
python run_dolar.py
```

### Opciones Disponibles
1. **🚀 Análisis completo con DolarAPI**: Ejecuta todo el pipeline
2. **💰 Solo DolarAPI Collector**: Obtiene cotizaciones del dólar
3. **📊 Solo Dolar Analyst**: Analiza datos de cotizaciones
4. **📄 Solo PDF Generator**: Crea reporte PDF con gráficos
5. **📊 Estado del sistema**: Verifica configuración

### Ejecución Individual de Agentes
```python
# DolarAPI Collector
python agents/dolar_api_collector.py

# Dolar Analyst
python agents/dolar_analyst_agent.py

# PDF Generator
python agents/pdf_generator_agent.py

# Orquestador completo con DolarAPI
python orchestrator_dolar.py
```

## 📊 Datos y Fuentes

### Fuentes de Datos
- **DolarAPI**: https://dolarapi.com/v1/dolares
- **Cotizaciones**: Oficial, Blue, Bolsa, CCL, Mayorista, Cripto, Tarjeta
- **Actualización**: Tiempo real cada 15-30 minutos

### Estructura de Datos
```json
{
  "cotizations": [
    {
      "moneda": "USD",
      "casa": "oficial",
      "nombre": "Oficial",
      "compra": 1400,
      "venta": 1450,
      "fechaActualizacion": "2025-10-03T17:01:00.000Z"
    },
    {
      "moneda": "USD",
      "casa": "blue",
      "nombre": "Blue",
      "compra": 1420,
      "venta": 1440,
      "fechaActualizacion": "2025-10-03T21:00:00.000Z"
    }
  ]
}
```

## 🎨 Características de las Presentaciones

### Gráficos Incluidos
- **Cotizaciones del Dólar**: Comparación de precios de compra y venta
- **Brechas Cambiarias**: Diferencias porcentuales vs dólar oficial
- **Spreads de Compra-Venta**: Análisis de liquidez por tipo de cotización
- **Comparación Visual**: Ranking de todas las cotizaciones
- **Análisis Profesional**: Insights generados por IA con Gemini

### Formato de Salida
- **PDF Profesional**: Reportes con diseño corporativo
- **Gráficos de Alta Calidad**: Imágenes PNG de 300 DPI
- **Tablas de Datos**: Información estructurada y legible
- **Análisis Detallado**: Texto generado por IA con insights

## 🔧 Configuración Avanzada

### Personalización de Fuentes
Edita `config.py` para agregar nuevas fuentes:
```python
DATA_SOURCES = {
    'nueva_fuente': 'https://ejemplo.com/datos',
    # ... más fuentes
}
```

### Acciones Personalizadas
Modifica la lista de acciones en `config.py`:
```python
ARGENTINE_STOCKS = ['NUEVA', 'ACCION', 'AQUI']
```

### Configuración de Gráficos
Personaliza el estilo de los gráficos:
```python
CHART_CONFIG = {
    'figure_size': (20, 12),
    'dpi': 300,
    'style': 'seaborn-v0_8',
    'color_palette': 'viridis'
}
```

## 🐛 Solución de Problemas

### Errores Comunes

1. **"GOOGLE_API_KEY no encontrada"**
   - Verifica que el archivo `.env` existe
   - Confirma que la variable está correctamente configurada

2. **"No se pudieron obtener datos financieros"**
   - Verifica conexión a internet
   - Algunos sitios pueden bloquear requests automatizados

3. **"Error en matplotlib"**
   - Instala dependencias: `pip install matplotlib seaborn`
   - En algunos sistemas: `pip install tkinter`

4. **"Módulo no encontrado"**
   - Instala todas las dependencias: `pip install -r requirements.txt`
   - Verifica que estás en el directorio correcto

### Logs y Debugging
- Los logs se guardan automáticamente en archivos JSON
- Usa `python run_analysis.py` para modo interactivo
- Cada agente tiene su propio sistema de logging

## 🔮 Próximas Mejoras

### Funcionalidades Planificadas
- [ ] **MCP Integration**: Integración con Model Context Protocol
- [ ] **Más fuentes de datos**: APIs financieras oficiales
- [ ] **Análisis histórico**: Tendencias a largo plazo
- [ ] **Alertas automáticas**: Notificaciones de cambios importantes
- [ ] **Dashboard web**: Interfaz web interactiva
- [ ] **Exportación PDF**: Presentaciones en formato PDF
- [ ] **Análisis sectorial**: Análisis por sectores económicos

### Integración MCP
El sistema está preparado para integrar MCP (Model Context Protocol) para:
- Acceso a herramientas externas
- Integración con bases de datos
- Comunicación entre sistemas
- Funcionalidades avanzadas de IA

## 📝 Licencia

Este proyecto es parte del repositorio Agentes_Inteligentes y está disponible bajo la misma licencia.

## 🤝 Contribuciones

Para contribuir al proyecto:
1. Fork el repositorio
2. Crea una rama para tu feature
3. Implementa tus cambios
4. Envía un pull request

## 📞 Soporte

Para soporte técnico o preguntas:
- Revisa la sección de solución de problemas
- Verifica los logs de ejecución
- Consulta la documentación de autogen y Gemini

---

**Desarrollado con ❤️ usando autogen, Gemini y Python**
