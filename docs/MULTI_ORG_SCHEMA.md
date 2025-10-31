# 🏢 Esquema Multi-Organización - Base de Datos

## 📋 Resumen

La base de datos ha sido migrada exitosamente a un **esquema multi-organización** que soporta múltiples organizaciones con entornos flexibles y URLs específicas por componente y entorno.

## 🏗️ Arquitectura del Nuevo Esquema

### 🔗 Diagrama de Relaciones

```
organizations (1) ←→ (N) environments (1) ←→ (N) deployments
                                    ↓
                            environment_urls (N) ←→ (1) application_components
                                    ↓
                            application_components (N) ←→ (1) applications
                                    ↓
                            versions (N) ←→ (1) application_components
```

## 📊 Tablas del Sistema

### 🏢 organizations
Tabla principal que define las organizaciones del sistema.

```sql
CREATE TABLE organizations (
    id TEXT PRIMARY KEY,                    -- Identificador único (ej: 'proeduca', 'villanueva')
    name TEXT NOT NULL,                     -- Nombre de la organización
    description TEXT,                       -- Descripción detallada
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

**Datos actuales:**
- `proeduca`: Organización principal PROEDUCA
- `villanueva`: Organización VILLANUEVA

### 🌍 environments
Define los entornos específicos de cada organización.

```sql
CREATE TABLE environments (
    id TEXT PRIMARY KEY,                    -- Identificador único (ej: 'proeduca-des', 'villanueva-pre')
    organization_id TEXT NOT NULL,         -- FK a organizations
    name TEXT NOT NULL,                    -- Nombre del entorno (des, pre, test, pro)
    description TEXT,                      -- Descripción del entorno
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);
```

**Configuración actual:**
- **PROEDUCA**: 4 entornos (des, pre, test, pro)
- **VILLANUEVA**: 2 entornos (pre, pro)

### 🌐 environment_urls
URLs específicas por entorno y componente.

```sql
CREATE TABLE environment_urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    environment_id TEXT NOT NULL,          -- FK a environments
    component_id TEXT NOT NULL,            -- FK a application_components
    url_type TEXT NOT NULL,               -- Tipo: 'frontend', 'backend', 'api', 'admin'
    url TEXT NOT NULL,                    -- URL completa
    description TEXT,                     -- Descripción de la URL
    active BOOLEAN DEFAULT 1,            -- Si la URL está activa
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (environment_id) REFERENCES environments(id),
    FOREIGN KEY (component_id) REFERENCES application_components(id)
);
```

### 🚀 deployments (Actualizada)
Tabla de despliegues adaptada al nuevo esquema.

```sql
-- Columna añadida:
ALTER TABLE deployments ADD COLUMN environment_id TEXT;

-- Relación establecida:
FOREIGN KEY (environment_id) REFERENCES environments(id)
```

**Mapeo de entornos migrados:**
- `dev` → `proeduca-des`
- `pre` → `proeduca-pre` 
- `prod` → `proeduca-pro`

## 📈 Estadísticas Post-Migración

### 🏢 Por Organización

| Organización | Entornos | Despliegues | URLs |
|--------------|----------|-------------|------|
| **proeduca** | 4 | 111 | 24+ |
| **villanueva** | 2 | 0 | 30+ |

### 📊 Totales del Sistema

- **Organizaciones**: 2
- **Entornos**: 6
- **Despliegues**: 111
- **URLs configuradas**: 54+
- **Aplicaciones**: 7
- **Componentes**: 14
- **Versiones**: 42

## 🔧 Herramientas Actualizadas

### 📡 Herramientas MCP Multi-Organización

#### Deployment Tools (`multi_org_deployment_tools.py`)
- `get_organizations()`: Lista todas las organizaciones
- `get_environments_by_organization(org_id)`: Entornos por organización
- `get_deployments_by_organization(org_id)`: Despliegues por organización
- `register_deployment(org_id, env_id, version, user)`: Nuevo despliegue
- `get_environment_urls(env_id)`: URLs de un entorno

#### Version Tools (`multi_org_version_tools.py`)
- `get_applications()`: Lista aplicaciones con estadísticas
- `create_version(app_id, version, release_date)`: Nueva versión
- `get_versions_by_application(app_id)`: Versiones por aplicación
- `get_deployment_history_by_version(version_id)`: Historial de despliegues
- `get_latest_versions_by_environment(org_id, env_id)`: Últimas versiones por entorno

### 🎨 Frontend Multi-Organización

#### Nuevo Dashboard (`multi_org_dashboard.py`)
- **Vista de Organizaciones**: Métricas y distribución por organización
- **Filtros Dinámicos**: Selección de organización y entorno
- **Métricas de Despliegues**: Estadísticas en tiempo real
- **Estado de Entornos**: Visualización del estado por entorno
- **Despliegues Recientes**: Lista detallada con filtros

#### Características Principales:
- 📊 4 pestañas principales (Organizaciones, Métricas, Entornos, Despliegues)
- 🎯 Filtros por organización y entorno
- 📈 Gráficos interactivos con Plotly
- ⏱️ Datos en tiempo real
- 🎨 Interfaz responsiva

## 🚀 Scripts de Gestión

### Migración (`migrate_to_multi_org.py`)
- ✅ **Ejecutado exitosamente** el 31/10/2025 16:30:56
- 💾 Backup creado: `data/backup/deployments_pre_migration_20251031_163056.db`
- 📋 Reporte generado: `data/migration_report_20251031_163056.json`

### Generación de Datos (`generate_multi_org_data.py`)
- ✅ **Ejecutado exitosamente**
- 🌐 30 URLs adicionales creadas
- 📊 Datos de prueba listos para ambas organizaciones

### Ejecución del Dashboard (`run_multi_org_dashboard.py`)
- 🚀 Script para ejecutar el dashboard en puerto 8503
- 🌐 Acceso: `http://localhost:8503`

## 📋 Comandos Útiles

### Ejecutar el Dashboard
```bash
python run_multi_org_dashboard.py
```

### Generar Datos de Ejemplo
```bash
python generate_multi_org_data.py
```

### Información de la Base de Datos
```bash
python database_info.py summary
```

### Verificar Estado por Organización
```bash
python database_info.py environments
```

## 🔄 Próximos Pasos

### ✅ Completado
- [x] Diseño del nuevo esquema multi-organización
- [x] Script de migración con backup automático
- [x] Creación de nuevas tablas (organizations, environments, environment_urls)
- [x] Actualización de modelos Pydantic
- [x] Migración exitosa de datos existentes
- [x] Herramientas MCP actualizadas
- [x] Nuevo dashboard multi-organización
- [x] Scripts de generación de datos de ejemplo
- [x] Documentación completa del nuevo esquema

### 🔮 Futuras Mejoras
- [ ] Autenticación y autorización por organización
- [ ] API REST para gestión externa
- [ ] Notificaciones por organización/entorno
- [ ] Métricas avanzadas y alertas
- [ ] Integración con CI/CD por organización
- [ ] Gestión de secretos por entorno
- [ ] Auditoría detallada de cambios

## 🎯 Conclusión

La migración a esquema multi-organización ha sido **completamente exitosa**. El sistema ahora soporta:

- ✅ **Múltiples organizaciones** con configuración flexible
- ✅ **Entornos específicos** por organización (PROEDUCA: des/pre/test/pro, VILLANUEVA: pre/pro)
- ✅ **URLs gestionadas** por entorno y componente
- ✅ **Herramientas MCP** actualizadas para el nuevo esquema
- ✅ **Dashboard moderno** con filtros por organización
- ✅ **Compatibilidad total** con datos existentes
- ✅ **Backup completo** de datos originales

El sistema está **listo para producción** y puede escalar fácilmente para agregar más organizaciones y entornos según las necesidades futuras.

---

*📅 Documentación actualizada: 31 de octubre de 2025*  
*🚀 Sistema: MCP Deployment Manager Multi-Organización v2.0*