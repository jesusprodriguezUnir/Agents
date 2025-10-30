# Servidor MCP de Gestión de Despliegues

## Descripción

Servidor Model Context Protocol (MCP) especializado en gestión de despliegues y versiones para aplicaciones .NET Core + Angular. Proporciona control y documentación automatizada de despliegues en múltiples entornos.

## Características

- � Gestión de despliegues en entornos Dev/Pre/Prod
- 📊 Seguimiento de versiones y cambios entre releases
- 📝 Generación automática de documentación de despliegue
- 🔍 Comparación de versiones y análisis de cambios
- � Control de incidencias post-despliegue
- � Métricas y dashboard de estado por entorno
- 🌐 Interfaz web Streamlit para gestión visual
- ☁️ Listo para despliegue en la nube

## Instalación

### Requisitos
- Python 3.9+
- pip

### Configuración del Entorno
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Para desarrollo
pip install -r requirements-dev.txt
```

## Uso

### Desarrollo Local
```bash
# Ejecutar servidor MCP
python -m src.mcp_server.main

# Ejecutar interfaz Streamlit
streamlit run src/frontend/app.py
```

### Testing
```bash
# Ejecutar tests
pytest tests/

# Con cobertura
pytest --cov=src tests/
```

### Despliegue
```bash
# Construir imagen Docker
docker build -t mcp-server .

# Ejecutar contenedor
docker run -p 8000:8000 -p 8501:8501 mcp-server
```

## Estructura del Proyecto
```
src/
├── mcp_server/      # Implementación del servidor MCP
├── tools/           # Herramientas MCP con esquemas
├── frontend/        # Interfaz web Streamlit
├── schemas/         # Validadores de protocolo MCP
└── utils/           # Utilidades compartidas

config/              # Configuraciones del servidor
tests/               # Tests unitarios e integración
```

## Contribuir
1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## Licencia
MIT License