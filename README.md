# Agentes_Inteligentes

Este proyecto contiene agentes inteligentes desarrollados con autogen y modelos de IA como Gemini.

## Guía de Instalación

### Prerrequisitos
- Python 3.10 o superior
- pip (gestor de paquetes de Python)

### Dependencias Requeridas

Para ejecutar el script `gemini.py`, necesitas instalar las siguientes dependencias:

```bash
# Instalar autogen-ext (extensión de autogen)
pip install autogen-ext

# Instalar OpenAI (requerido por autogen-ext)
pip install openai

# Instalar tiktoken (tokenizador de texto)
pip install tiktoken

# Instalar python-dotenv (para variables de entorno)
pip install python-dotenv

# Instalar nest-asyncio (para manejo de asyncio)
pip install nest-asyncio
```

### Configuración

1. **Variables de entorno**: Crea un archivo `.env` en la raíz del proyecto con tu API key de Google:
   ```
   GOOGLE_API_KEY=tu_api_key_aqui
   ```

2. **Ubicación del archivo**: Asegúrate de que el archivo `.env` esté en el directorio raíz del proyecto.

### Ejecución

Para ejecutar el script `gemini.py`:

```bash
# Navegar al directorio del script
cd Agentes_Inteligentes/Models

# Ejecutar el script
python gemini.py
```

### Descripción del Script

El script `gemini.py` utiliza:
- **autogen-agentchat**: Para crear agentes conversacionales
- **autogen-ext**: Extensión que proporciona clientes para diferentes modelos
- **Gemini 2.5 Flash Lite**: Modelo de Google para generar respuestas
- **Funcionalidades**: Vision, function calling, JSON output y structured output

El script hace una pregunta simple ("¿Cuál es la capital de Argentina?") y muestra la respuesta del modelo Gemini.

### Solución de Problemas

Si encuentras errores de módulos no encontrados, asegúrate de instalar todas las dependencias listadas arriba. El orden de instalación puede ser importante debido a las dependencias entre paquetes.