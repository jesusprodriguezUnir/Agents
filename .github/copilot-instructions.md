# Instrucciones para Copilot - MCP Deployment Manager

## Resumen del Proyecto
Este es un servidor Python basado en Model Context Protocol (MCP) especializado en gestión de despliegues y versiones para aplicaciones .NET Core + Angular. El proyecto proporciona un sistema completo para seguimiento de despliegues, gestión de versiones en múltiples entornos y automatización de documentación de despliegues en una arquitectura multi-organización.

## Patrones de Desarrollo

### Arquitectura Multi-Organización
- **Estructura Jerárquica**: Organizaciones → Aplicaciones → Componentes (frontend/backend) → Versiones → Despliegues
- **Tipos de Componentes**: Frontend (Angular), Backend (.NET Core), Microservicios, Scripts de base de datos, Infraestructura
- **Gestión de Entornos**: Definiciones flexibles de entornos por organización con múltiples tipos de URL (app principal, health check, swagger, admin)
- **Seguimiento de Despliegues**: Seguimiento de estados (pending/in_progress/success/failed/rollback) con metadatos de despliegue

### Organización del Código
```
src/
├── mcp_server/          # Implementación principal del servidor MCP (server.py, main.py)
├── tools/               # Herramientas MCP organizadas por dominio
│   ├── deployment/      # Herramientas de gestión de despliegues multi-org
│   │   ├── multi_org_deployment_tools.py  # Registro/consultas de despliegues
│   │   └── multi_org_version_tools.py     # Gestión de versiones
│   └── basic_tools.py   # Calculadora, procesamiento de texto, utilidades del sistema
├── models/             # Modelos de datos con validación Pydantic
│   ├── multi_org_models.py  # Modelos de Organización, Entorno, Despliegue
│   └── deployment.py        # Modelos legacy single-org
├── frontend/           # Dashboard Streamlit de despliegues
│   ├── app.py              # Aplicación principal del dashboard
│   ├── multi_org_dashboard.py  # Vistas específicas por organización
│   └── dashboard_tools.py  # Funciones utilitarias del dashboard
├── storage/            # Capa de persistencia de datos
│   └── database.py     # Gestor de base de datos SQLite con migraciones
├── schemas/            # Esquemas y validadores del protocolo MCP
└── utils/              # Utilidades compartidas (configuración de logging)
```

### Convenciones Clave
- **Async First**: Todas las operaciones del servidor usan patrones `async/await` con `asyncio`
- **Modelos Pydantic**: Validación estricta de datos usando Pydantic BaseModel con enums para valores controlados
- **Logging Estructurado**: `structlog` para logs formateados en JSON con contexto
- **Protocolo MCP**: Registro de herramientas vía `ToolRegistry` con validación de esquemas JSON
- **Almacenamiento SQLite**: Base de datos basada en archivos con restricciones de clave foránea y almacenamiento JSON
- **Patrón Factory**: Creación de servidor vía función factory `create_server()`

### Patrones de Desarrollo de Herramientas
- **Registro de Herramientas**: Registrar herramientas en `ToolRegistry` con nombre, descripción, input_schema y handler async
- **Validación de Esquemas**: Usar modelos Pydantic para validación de entrada/salida de herramientas
- **Manejo de Errores**: Retornar respuestas de error estructuradas con códigos de error compatibles con MCP
- **Integración con Base de Datos**: Consultas SQLite directas en handlers de herramientas (sin abstracción ORM)
- **Respuestas JSON**: Las herramientas retornan estructuras de datos serializables en JSON

### Estrategia de Testing
- **pytest-asyncio**: Todos los tests usan fixtures y funciones de test async
- **Estructura de Tests**: `tests/unit/` refleja la estructura `src/`, `tests/integration/` para tests del protocolo MCP
- **Testing de Base de Datos**: Bases de datos SQLite en memoria para ejecución de tests aislados
- **Integración Mock**: Clientes MCP mock usando fixtures de pytest
- **Datos de Test**: Generadores de datos de ejemplo en `scripts/` para escenarios realistas

### Flujo de Desarrollo
- **Configuración de Entorno**: `python -m venv venv && venv/Scripts/Activate.ps1 && pip install -r requirements.txt`
- **Servidor MCP**: `python -m src.mcp_server.main` (servidor MCP basado en stdio)
- **Dashboard Streamlit**: `streamlit run src/frontend/app.py` (corre en puerto 8501)
- **Testing**: `pytest tests/` con soporte async
- **Calidad de Código**: `black src/ tests/` para formateo, type checking con mypy
- **Gestión de Datos**: Generación de datos de ejemplo vía `scripts/generate_sample_data.py`

### Gestión de Configuración
- **Config YAML**: Configuración del servidor en `config/server.yaml`
- **Variables de Entorno**: Configuración en runtime vía archivo `.env` (no commiteado)
- **Ruta de Base de Datos**: Ruta configurable de base de datos SQLite (por defecto `data/deployments.db`)
- **Configuración de Herramientas**: Habilitar/deshabilitar herramientas vía configuración de archivos

### Patrones de Despliegue en la Nube
- **Containerización**: Dockerfile multi-servicio ejecutando tanto servidor MCP como Streamlit
- **Plataformas Cloud**: Railway, Render, Heroku con almacenamiento SQLite persistente
- **Variables de Entorno**: Gestión de variables de entorno específicas por plataforma para secrets
- **Health Checks**: App Streamlit proporciona monitoreo de interfaz web
- **Servicio Dual**: Contenedor único ejecuta tanto servidor MCP (stdio) como dashboard web

### Implementación del Protocolo MCP
- **Transporte Stdio**: Servidor MCP usa stdio para comunicación con clientes (sin HTTP)
- **Descubrimiento de Herramientas**: Listado dinámico de herramientas vía handler `list_tools()`
- **Ejecución Async**: Todas las llamadas a herramientas son async con propagación apropiada de errores
- **Sin Recursos/Prompts**: Implementación actual se enfoca solo en herramientas
- **Integración con Clientes**: Diseñado para integración con clientes compatibles con MCP (editores, agentes)

### Patrones de Modelos de Datos
- **Relaciones Jerárquicas**: Cadenas de clave foránea (org → env → deployment → incident)
- **Almacenamiento JSON**: Datos complejos almacenados como JSON en columnas TEXT de SQLite
- **Restricciones Enum**: Enums Pydantic aseguran integridad de datos a nivel de aplicación
- **Seguimiento de Timestamps**: Timestamps automáticos created_at/updated_at
- **Claves Primarias UUID**: UUIDs basados en strings para compatibilidad distribuida

### Patrones del Dashboard Streamlit
- **Layout Multi-Página**: Selección de organización impulsa vistas de entorno/despliegue
- **Visualizaciones Plotly**: Gráficos interactivos para estado de despliegues y timelines
- **Operaciones CRUD**: Formularios de edición inline para aplicaciones, versiones, despliegues
- **Exportación PDF**: Generación de reportes usando reportlab para resúmenes de despliegues
- **Actualizaciones en Tiempo Real**: Dashboard consulta base de datos directamente para estado actual

## Notas Importantes
- **Acceso Directo a Base de Datos**: Las herramientas consultan SQLite directamente en lugar de usar patrones repository
- **Sin Autenticación**: Implementación actual no tiene autenticación o autorización de usuarios
- **Almacenamiento Basado en Archivos**: Archivos de base de datos SQLite son el mecanismo principal de persistencia
- **Scripts de Migración**: Cambios de esquema de base de datos manejados vía scripts de migración en `scripts/`
- **Datos de Ejemplo**: Usar scripts `scripts/generate_*_data.py` para poblar entornos de test
- **Flexibilidad de Entornos**: Las organizaciones pueden definir entornos personalizados más allá de dev/pre/prod