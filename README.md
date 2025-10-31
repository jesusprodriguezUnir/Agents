# 🚀 MCP Deployment Manager

## Descripción

Sistema avanzado de gestión de despliegues basado en Model Context Protocol (MCP) especializado en aplicaciones .NET Core + Angular. Proporciona una solución completa para el seguimiento, gestión y documentación de despliegues en múltiples entornos con arquitectura jerárquica.

## 🌟 Características Principales

### 🏗️ Arquitectura Jerárquica
- **Aplicaciones**: Contenedores principales (ej: "Expedientes ERP")
- **Componentes**: Frontend y Backend por aplicación
- **Versiones**: Versionado independiente por componente
- **Despliegues**: Seguimiento por entorno (dev, pre, prod)

### 📊 Dashboard Interactivo
- **Resumen Ejecutivo**: Estado actual de todos los entornos
- **Gestión CRUD**: Crear, leer, actualizar aplicaciones/componentes/versiones
- **Visualizaciones**: Gráficos interactivos con Plotly
- **Exportación PDF**: Reportes imprimibles del estado de entornos
- **Edición en línea**: Formularios de edición integrados

### 🛠️ Tecnologías Utilizadas
- **Backend**: Python 3.9+, MCP Protocol, SQLite
- **Frontend**: Streamlit, Plotly, HTML/CSS
- **Base de Datos**: SQLite con estructura normalizada
- **Deployment**: Docker ready, Railway/Render compatible

## 📋 Estructura del Proyecto

```
src/
├── mcp_server/          # Servidor MCP principal
│   ├── main.py          # Punto de entrada del servidor
│   └── server.py        # Implementación del protocolo MCP
├── tools/               # Herramientas MCP organizadas por dominio
│   ├── deployment/      # Gestión de despliegues
│   ├── git/            # Integración con Git
│   ├── documentation/  # Generación de documentación
│   └── incidents/      # Gestión de incidencias
├── models/             # Modelos de datos Pydantic
│   └── deployment.py   # Modelos de aplicaciones, versiones, despliegues
├── frontend/           # Dashboards Streamlit
│   ├── enhanced_dashboard.py      # Dashboard principal con edición
│   ├── hierarchical_dashboard.py  # Dashboard estructura jerárquica
│   └── dashboard_tools.py         # Herramientas de integración BD
├── storage/            # Gestión de persistencia
│   └── database.py     # Gestor SQLite
└── utils/              # Utilidades compartidas
    └── logging.py      # Logging estructurado

scripts/                # Scripts de generación de datos
├── generate_hierarchical_apps.py  # Datos con estructura jerárquica
└── generate_unir_apps.py          # Datos aplicaciones UNIR

data/                   # Base de datos SQLite
└── deployments.db     # BD con aplicaciones reales UNIR

config/                 # Configuraciones
├── server.yaml        # Config servidor MCP
└── tools/             # Configuraciones herramientas

.github/
└── copilot-instructions.md  # Instrucciones para Copilot
```

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.9 o superior
- Git
- Entorno virtual (recomendado)

### Instalación

1. **Clonar el repositorio**:
```bash
git clone https://github.com/jesusprodriguezUnir/Agents.git
cd Agents
```

2. **Crear y activar entorno virtual**:
```bash
python -m venv venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

4. **Generar datos de aplicaciones**:
```bash
python scripts/generate_hierarchical_apps.py
```

## ✅ Verificación del Proyecto

### Lista de Verificación Pre-Ejecución

Antes de ejecutar el proyecto, sigue estos pasos para asegurar que todo esté configurado correctamente:

#### 1. **Verificar Estructura del Proyecto**

```bash
# Verificar que todos los archivos clave están presentes
ls -la src/
ls -la config/
ls -la data/
```

#### 2. **Revisar Dependencias**

```bash
# Verificar requirements.txt
cat requirements.txt
# Verificar instalación de dependencias
pip list | grep -E "(streamlit|mcp|pydantic|plotly)"
```

#### 3. **Configurar Entorno Python**

```bash
# Crear entorno virtual si no existe
python -m venv .venv

# Activar entorno virtual
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

#### 4. **Verificar Configuración MCP**

```bash
# Revisar configuración del servidor
cat config/server.yaml
```

#### 5. **Verificar Base de Datos**

```bash
# Generar datos si no existen
python scripts/generate_hierarchical_apps.py
# Verificar que la BD se creó correctamente
ls -la data/deployments.db
```

### Proceso de Ejecución

#### 🎯 Opción 1: Ejecución Automática (Recomendada)

```bash
# Script launcher que verifica todo automáticamente
python run_enhanced_dashboard.py
```

**Salida esperada:**

```console
🔧 MCP Deployment Manager - Launcher
==================================================
✅ Todas las dependencias están instaladas
✅ Base de datos encontrada:
   - 7 aplicaciones
   - 14 componentes  
   - 42 versiones
   - 111 despliegues
✅ Dashboard mejorado encontrado

🚀 Lanzando Dashboard Mejorado...
📊 URL: http://localhost:8501
⏹️  Para detener: Ctrl+C
```

#### 🎯 Opción 2: Ejecución Manual

##### Dashboard Principal (Recomendado)

```bash
streamlit run src/frontend/enhanced_dashboard.py --server.port 8501
```

##### Servidor MCP (Desarrollo)

```bash
python -m src.mcp_server.main
```

**Salida esperada:**

```console
2025-10-31T14:56:33.808815Z [info] Starting MCP Server application
2025-10-31T14:56:33.808815Z [info] MCP server created successfully
2025-10-31T14:56:33.914961Z [info] Tool registered successfully tool_name=list_versions
2025-10-31T14:56:33.914961Z [info] Tool registered successfully tool_name=get_version_details
...
2025-10-31T14:56:33.914961Z [info] Default tools registered count=12
2025-10-31T14:56:33.914961Z [info] MCP Server ready to accept connections
```

##### Dashboards Alternativos

```bash
# Dashboard jerárquico básico
streamlit run src/frontend/hierarchical_dashboard.py --server.port 8502

# Dashboard multi-aplicación (legacy)
streamlit run src/frontend/multi_app_dashboard.py --server.port 8503
```

### 🔍 Verificación de Funcionamiento

#### Servidor MCP

1. **Importación correcta de módulos:**

```bash
python -c "import src.mcp_server.server; print('✅ MCP server import successful')"
```

2. **Registro de herramientas:**
   - Debe registrar **12 herramientas** exitosamente
   - Herramientas de versiones: `list_versions`, `get_version_details`, `compare_versions`, `create_sample_version`
   - Herramientas de despliegue: `register_deployment`, `update_deployment_status`, `get_deployment_history`, `get_environment_status`
   - Herramientas básicas: `calculator`, `text_processor`, `system_info`, `echo`

#### Dashboard Streamlit

1. **URL de acceso:** `http://localhost:8501`
2. **Funcionalidades a verificar:**
   - ✅ Carga de datos desde BD
   - ✅ Visualización de aplicaciones
   - ✅ Gráficos interactivos
   - ✅ Exportación PDF
   - ✅ Formularios de edición

### 🚨 Solución de Problemas Comunes

#### Error: "ModuleNotFoundError"

```bash
# Verificar que el entorno virtual está activado
which python  # Linux/Mac
where python   # Windows

# Reinstalar dependencias
pip install -r requirements.txt
```

#### Error: "Database not found"

```bash
# Generar base de datos
python scripts/generate_hierarchical_apps.py
```

#### Error: "Port already in use"

```bash
# Verificar procesos en puerto 8501
lsof -i :8501  # Linux/Mac
netstat -ano | findstr :8501  # Windows

# Usar puerto alternativo
streamlit run src/frontend/enhanced_dashboard.py --server.port 8502
```

#### Error en servidor MCP: "AsyncExitStack"

- Este error es **normal** al interrumpir el servidor con Ctrl+C
- El servidor se ejecuta correctamente antes de la interrupción
- No afecta la funcionalidad

### 📊 Estado Esperado del Sistema

Una vez verificado, el sistema debe mostrar:

**Base de Datos:**
- 7 aplicaciones académicas de UNIR
- 14 componentes (frontend + backend)
- 42 versiones distribuidas
- 111 despliegues en dev/pre/prod

**Servicios:**
- Dashboard Streamlit: `http://localhost:8501`
- Servidor MCP: Puerto 8000 (opcional)
- Base de datos SQLite: `data/deployments.db`

## 📱 Aplicaciones Incluidas

El sistema incluye las siguientes aplicaciones reales de UNIR:

### 🏢 Aplicaciones Académicas

1. **Expedientes ERP**
   - Frontend: Angular 18 + TypeScript
   - Backend: .NET Core 8
   - Repositorio: [core-expedienteserp-spa](https://dev.azure.com/unirnet/UNIR/_git/core-expedienteserp-spa)

2. **Expedición de Títulos**
   - Frontend: Angular 18 + TypeScript
   - Backend: .NET Core 8
   - Repositorios: Frontend/Backend separados

3. **Cargos Funcionales**
   - Frontend: Angular 18 + TypeScript
   - Backend: .NET Core 8
   - Gestión de roles académicos

4. **Segmentación Académica**
   - Frontend: Angular 18 + TypeScript
   - Backend: .NET Core 8
   - Análisis y segmentación

5. **Convenios e Integraciones**
   - Frontend: Angular 18 + TypeScript
   - Backend: .NET Core 8
   - Gestión BO convenios

6. **Trabajadores ERP**
   - Frontend: Angular 18 + TypeScript
   - Backend: .NET Core 8 (BFF)
   - Gestión usuarios ERP

7. **Credenciales Académicas**
   - Frontend: Angular 18 + TypeScript
   - Backend: .NET Core 8
   - Sistema credenciales

## 🎯 Funcionalidades del Dashboard

### 📊 Resumen Ejecutivo
- **Métricas Globales**: Aplicaciones, componentes, versiones, despliegues
- **Estado por Entorno**: Vista en tiempo real de dev, pre, prod
- **Exportación PDF**: Reportes imprimibles
- **Gráficos Interactivos**: Visualizaciones con Plotly

### 🏢 Gestión de Aplicaciones
- **Vista Jerárquica**: Aplicaciones → Componentes → Versiones
- **Edición en Línea**: Formularios integrados
- **Información Completa**: Repositorios, tecnologías, equipos
- **CRUD Completo**: Crear, leer, actualizar, eliminar

### 📦 Gestión de Componentes
- **Separación Frontend/Backend**: Gestión independiente
- **Tecnologías**: Stack tecnológico por componente
- **Repositorios**: Enlaces directos a Azure DevOps
- **Health Checks**: URLs de verificación

### 🔖 Gestión de Versiones
- **Versionado Semántico**: Soporte v.major.minor.patch
- **Información Git**: Branch, commit hash, build number
- **Características**: Features y bug fixes por versión
- **Trazabilidad**: Historial completo

### 🚀 Gestión de Despliegues
- **Multi-entorno**: dev, pre, prod
- **Estados**: pending, in_progress, success, failed, rollback
- **Trazabilidad**: Quién, cuándo, qué versión
- **Notas**: Información adicional por despliegue

## 🗄️ Estructura de Base de Datos

### Tablas Principales

```sql
-- Aplicaciones principales
applications (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    owner_team TEXT,
    created_at TEXT
)

-- Componentes (frontend/backend)
application_components (
    id TEXT PRIMARY KEY,
    application_id TEXT NOT NULL,
    name TEXT NOT NULL,
    type TEXT CHECK(type IN ('frontend', 'backend')),
    repository_url TEXT,
    tech_stack TEXT,
    health_check_url TEXT,
    created_at TEXT
)

-- Versiones por componente
versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL,
    component_id TEXT NOT NULL,
    branch TEXT,
    commit_hash TEXT,
    build_number TEXT,
    created_at TEXT,
    features TEXT,
    bug_fixes TEXT
)

-- Despliegues
deployments (
    id TEXT PRIMARY KEY,
    component_id TEXT NOT NULL,
    version_id INTEGER NOT NULL,
    environment TEXT NOT NULL,
    status TEXT NOT NULL,
    deployed_by TEXT,
    deployed_at TEXT,
    notes TEXT
)
```

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Configuración base de datos
DB_PATH=data/deployments.db

# Configuración servidor MCP
MCP_SERVER_PORT=8000
MCP_SERVER_HOST=localhost

# Configuración Streamlit
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
```

### Archivos de Configuración

#### `.env` (crear)
```env
# Base de datos
DATABASE_URL=sqlite:///data/deployments.db

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Servidor MCP
MCP_SERVER_NAME=deployment-manager
MCP_SERVER_VERSION=2.0.0
```

## 📈 Roadmap

### 🎯 Próximas Funcionalidades

- [ ] **Generador de Documentación**: Wiki automático de despliegues
- [ ] **Sistema de Incidencias**: Gestión post-despliegue
- [ ] **Integración Git**: Obtención automática de commits
- [ ] **Notificaciones**: Slack/Teams para despliegues
- [ ] **API REST**: Endpoints para integración externa
- [ ] **Métricas Avanzadas**: Tiempo de despliegue, frecuencia
- [ ] **Rollback Automático**: Reversión en caso de fallo
- [ ] **Multi-tenant**: Soporte para múltiples organizaciones

### 🔄 Mejoras Continuas

- [ ] **Performance**: Optimización consultas BD
- [ ] **UI/UX**: Mejoras interfaz usuario
- [ ] **Testing**: Cobertura pruebas unitarias/integración
- [ ] **Documentation**: Guías detalladas
- [ ] **Security**: Autenticación y autorización
- [ ] **Monitoring**: Métricas y alertas

## 🤝 Contribución

### Desarrollo Local

1. **Fork del repositorio**
2. **Crear rama feature**: `git checkout -b feature/nueva-funcionalidad`
3. **Desarrollar y testear**
4. **Commit y push**: Seguir [Conventional Commits](https://www.conventionalcommits.org/)
5. **Pull Request**: Descripción detallada de cambios

### Estándares de Código

- **Python**: PEP 8, type hints obligatorios
- **Docstrings**: Google style
- **Testing**: pytest, cobertura >80%
- **Commits**: Conventional Commits format

## 📚 Documentación Adicional

### 📋 Documentación Principal
- **[🗄️ Base de Datos](docs/DATABASE.md)** - Documentación completa del esquema, tablas y relaciones
- **[🔍 Consultas SQL](docs/SQL_QUERIES.md)** - Consultas avanzadas, vistas y scripts de mantenimiento
- [Guía de Usuario](docs/user-guide.md)
- [API Reference](docs/api-reference.md)
- [Deployment Guide](docs/deployment.md)
- [Contributing Guidelines](docs/contributing.md)

### 🗄️ Base de Datos
El sistema utiliza **SQLite** con la siguiente estructura:

| Tabla | Registros | Descripción |
|-------|-----------|-------------|
| `applications` | 7 | Aplicaciones principales de UNIR |
| `application_components` | 14 | Componentes frontend/backend |
| `versions` | 42 | Versiones con información Git |
| `deployments` | 111 | Historial de despliegues |

📖 **Documentación completa**: [docs/DATABASE.md](docs/DATABASE.md)

#### 🔍 Script de Información de BD
```bash
# Resumen general de la base de datos
python database_info.py summary

# Estado detallado por entorno
python database_info.py environments

# Actividad reciente
python database_info.py recent

# Información completa
python database_info.py all
```

### 🔍 Consultas SQL Útiles
- **Dashboard Ejecutivo**: Métricas principales del sistema
- **Análisis de Rendimiento**: Tiempo entre despliegues y frecuencia
- **Auditoría**: Rastreo de cambios y actividad por usuario
- **Mantenimiento**: Scripts de limpieza y optimización

📖 **Consultas completas**: [docs/SQL_QUERIES.md](docs/SQL_QUERIES.md)

## 📞 Soporte

- **Email**: soporte@unir.net
- **Issues**: [GitHub Issues](https://github.com/jesusprodriguezUnir/Agents/issues)
- **Documentación**: [Wiki del Proyecto](https://github.com/jesusprodriguezUnir/Agents/wiki)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 🎖️ Reconocimientos

Desarrollado con ❤️ por el equipo de UNIR para optimizar la gestión de despliegues académicos.

**Tecnologías principales utilizadas:**
- [Streamlit](https://streamlit.io/) - Framework web interactivo
- [Plotly](https://plotly.com/python/) - Visualizaciones interactivas
- [SQLite](https://sqlite.org/) - Base de datos embebida
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Validación de datos
- [MCP Protocol](https://github.com/modelcontextprotocol/python-sdk) - Protocolo de contexto