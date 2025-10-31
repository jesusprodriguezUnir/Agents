# 🎮 MCP Deployment Manager - Configuración del Proyecto

## 📋 Estado Actual del Sistema

**Versión**: 2.0.0 - Arquitectura Jerárquica  
**Estado**: ✅ Operativo y Funcional  
**Dashboard Principal**: http://localhost:8501  
**Fecha**: $(Get-Date -Format "yyyy-MM-dd")

## 🗄️ Base de Datos

### Ubicación
```
data/deployments.db
```

### Estructura Poblada
- **Aplicaciones**: 7 (aplicaciones reales UNIR)
- **Componentes**: 14 (frontend + backend por app)
- **Versiones**: 42 (versionado semántico)
- **Despliegues**: 111 (distribuidos en dev/pre/prod)

## 🖥️ Dashboards Disponibles

### 1. Dashboard Principal (Recomendado)
- **Archivo**: `src/frontend/enhanced_dashboard.py`
- **Puerto**: 8501
- **Funciones**: CRUD completo, visualizaciones, PDF export
- **Estado**: ✅ Operativo

### 2. Dashboard Jerárquico
- **Archivo**: `src/frontend/hierarchical_dashboard.py`
- **Puerto**: 8502
- **Funciones**: Vista básica jerárquica
- **Estado**: ✅ Funcional

### 3. Dashboard Multi-App (Legacy)
- **Archivo**: `src/frontend/multi_app_dashboard.py`
- **Puerto**: 8503
- **Funciones**: Vista anterior plana
- **Estado**: ⚠️ Deprecado

## 🛠️ Scripts de Ejecución

### Windows (Recomendado)
```bash
run_enhanced_dashboard.bat
```

### Multiplataforma
```bash
python run_enhanced_dashboard.py
```

### Manual
```bash
# Activar entorno
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Lanzar dashboard
streamlit run src/frontend/enhanced_dashboard.py --server.port 8501
```

## 📦 Dependencias Críticas

### Python Packages (Instaladas)
- **streamlit**: Framework web dashboard
- **plotly**: Visualizaciones interactivas
- **pandas**: Manipulación de datos
- **pydantic**: Validación de modelos
- **sqlite3**: Base de datos (built-in)

### Archivos de Configuración
- **requirements.txt**: Dependencias Python
- **.venv/**: Entorno virtual configurado
- **data/**: Directorio base de datos

## 🎯 Funcionalidades Implementadas

### ✅ Gestión de Aplicaciones
- Crear, leer, actualizar, eliminar aplicaciones
- Información completa: nombre, descripción, equipo, repositorios
- Vista jerárquica de componentes

### ✅ Gestión de Componentes
- Separación frontend/backend
- Stack tecnológico por componente
- URLs de health check
- Enlaces a repositorios Azure DevOps

### ✅ Gestión de Versiones
- Versionado semántico independiente
- Información Git: branch, commit, build
- Features y bug fixes por versión
- Historial completo

### ✅ Gestión de Despliegues
- Multi-entorno: dev, pre, prod
- Estados: pending, in_progress, success, failed, rollback
- Trazabilidad: usuario, fecha, notas
- Métricas de estado

### ✅ Visualizaciones
- Distribución de despliegues por entorno
- Estado de aplicaciones
- Timeline de versiones
- Métricas consolidadas

### ✅ Exportación
- Reportes PDF ejecutivos
- Resumen de entornos
- Datos estructurados

## 🔧 Configuración de Desarrollo

### Entorno Python
- **Versión**: Python 3.12.10
- **Tipo**: VirtualEnvironment
- **Ubicación**: `.venv/`
- **Activación**: `.venv/Scripts/activate` (Windows)

### Base de Datos SQLite
- **Versión**: SQLite 3.x
- **Archivo**: `data/deployments.db`
- **Esquema**: Jerárquico normalizado
- **Backup**: Automático en scripts

## 📊 Aplicaciones UNIR Incluidas

### 1. Expedientes ERP
- **Frontend**: Angular 18 + TypeScript
- **Backend**: .NET Core 8
- **Repo**: core-expedienteserp-spa

### 2. Expedición de Títulos
- **Frontend**: Angular 18 + TypeScript
- **Backend**: .NET Core 8
- **Repos**: Separados frontend/backend

### 3. Cargos Funcionales
- **Frontend**: Angular 18 + TypeScript
- **Backend**: .NET Core 8
- **Función**: Gestión roles académicos

### 4. Segmentación Académica
- **Frontend**: Angular 18 + TypeScript
- **Backend**: .NET Core 8
- **Función**: Análisis y segmentación

### 5. Convenios e Integraciones
- **Frontend**: Angular 18 + TypeScript
- **Backend**: .NET Core 8
- **Función**: Gestión BO convenios

### 6. Trabajadores ERP
- **Frontend**: Angular 18 + TypeScript
- **Backend**: .NET Core 8 (BFF)
- **Función**: Gestión usuarios ERP

### 7. Credenciales Académicas
- **Frontend**: Angular 18 + TypeScript
- **Backend**: .NET Core 8
- **Función**: Sistema credenciales

## 🚀 Comandos Útiles

### Regenerar Base de Datos
```bash
python scripts/generate_hierarchical_apps.py
```

### Verificar Dependencias
```bash
pip list | grep -E "(streamlit|plotly|pandas)"
```

### Lanzar Dashboard en Puerto Específico
```bash
streamlit run src/frontend/enhanced_dashboard.py --server.port 8502
```

### Ver Logs del Dashboard
```bash
# Los logs aparecen en la terminal donde se ejecuta streamlit
```

## 🧪 Testing y Debugging

### Verificación de Funcionalidad
- [ ] Dashboard se abre en http://localhost:8501
- [ ] Base de datos contiene 7 aplicaciones
- [ ] Funciones CRUD operativas
- [ ] Visualizaciones se cargan correctamente
- [ ] Exportación PDF funciona

### Troubleshooting Común
- **Puerto ocupado**: Cambiar con `--server.port`
- **Módulos faltantes**: `pip install -r requirements.txt`
- **BD vacía**: Ejecutar script de generación
- **Errores Python**: Verificar entorno virtual activado

## 🎖️ Logros del Proyecto

1. ✅ **Arquitectura Jerárquica**: Sistema escalable implementado
2. ✅ **Datos Reales**: Aplicaciones UNIR con información completa
3. ✅ **Dashboard Completo**: Interface moderna y funcional
4. ✅ **CRUD Operativo**: Todas las operaciones funcionando
5. ✅ **Visualizaciones**: Gráficos interactivos implementados
6. ✅ **Exportación**: Reportes PDF funcionando
7. ✅ **Automatización**: Scripts de setup y ejecución
8. ✅ **Documentación**: README y guías completas

---

**🎯 Sistema Completamente Operativo**  
**📊 Dashboard funcionando en: http://localhost:8501**  
**🗄️ Base de datos poblada con datos reales de UNIR**  
**🔧 Todas las funcionalidades CRUD implementadas**