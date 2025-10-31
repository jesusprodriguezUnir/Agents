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

### Ejecución

#### Dashboard Principal (Recomendado)
```bash
streamlit run src/frontend/enhanced_dashboard.py --server.port 8501
```

#### Servidor MCP (Opcional)
```bash
python -m src.mcp_server.main
```

#### Dashboards Alternativos
```bash
# Dashboard jerárquico básico
streamlit run src/frontend/hierarchical_dashboard.py --server.port 8502

# Dashboard multi-aplicación (legacy)
streamlit run src/frontend/multi_app_dashboard.py --server.port 8503
```

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

- [Guía de Usuario](docs/user-guide.md)
- [API Reference](docs/api-reference.md)
- [Deployment Guide](docs/deployment.md)
- [Contributing Guidelines](docs/contributing.md)

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