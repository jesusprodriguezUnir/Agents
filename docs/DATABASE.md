# 🗄️ Documentación de Base de Datos - MCP Deployment Manager

## 📋 Índice

- [Descripción General](#descripción-general)
- [Esquema de Base de Datos](#esquema-de-base-de-datos)
- [Tablas Principales](#tablas-principales)
- [Relaciones entre Tablas](#relaciones-entre-tablas)
- [Ejemplos de Datos](#ejemplos-de-datos)
- [Consultas SQL Útiles](#consultas-sql-útiles)
- [Mantenimiento](#mantenimiento)
- [Backup y Restauración](#backup-y-restauración)

## 📊 Descripción General

El sistema utiliza **SQLite** como base de datos embebida para almacenar toda la información relacionada con aplicaciones, componentes, versiones y despliegues del ecosistema académico de UNIR.

### Características

- **Motor**: SQLite 3
- **Ubicación**: `data/deployments.db`
- **Encoding**: UTF-8
- **Tamaño aproximado**: ~500KB con datos de ejemplo
- **Tablas**: 4 tablas principales + 1 tabla sistema

### Estadísticas Actuales

- **7 aplicaciones** académicas de UNIR
- **14 componentes** (frontend + backend)
- **42 versiones** distribuidas
- **111 despliegues** en entornos dev/pre/prod

## 🏗️ Esquema de Base de Datos

### Diagrama de Relaciones

```
┌─────────────────┐    1:N    ┌──────────────────────┐    1:N    ┌─────────────────┐
│   applications  │◄──────────┤ application_components│◄──────────┤   versions      │
│                 │           │                      │           │                 │
│ • id (PK)       │           │ • id (PK)            │           │ • id (PK)       │
│ • name          │           │ • application_id (FK)│           │ • version       │
│ • description   │           │ • name               │           │ • component_id  │
│ • owner_team    │           │ • type               │           │ • branch        │
│ • created_at    │           │ • repository_url     │           │ • commit_hash   │
└─────────────────┘           │ • tech_stack         │           │ • features      │
                              │ • health_check_url   │           │ • created_at    │
                              │ • created_at         │           └─────────────────┘
                              └──────────────────────┘                     │
                                        │                                  │ 1:N
                                        │ 1:N                              ▼
                              ┌─────────────────────────────────────────────────────┐
                              │                 deployments                        │
                              │                                                     │
                              │ • id (PK)                                          │
                              │ • component_id (FK) ──────────────────────────────►│
                              │ • version_id (FK) ─────────────────────────────────►│
                              │ • environment                                      │
                              │ • status                                           │
                              │ • deployed_by                                      │
                              │ • deployed_at                                      │
                              │ • notes                                            │
                              └─────────────────────────────────────────────────────┘
```

## 📋 Tablas Principales

### 1. **applications** - Aplicaciones Principales

Almacena información de las aplicaciones principales del ecosistema académico.

```sql
CREATE TABLE applications (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    owner_team TEXT,
    created_at TEXT
);
```

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `id` | TEXT (PK) | Identificador único de la aplicación | `expedientes` |
| `name` | TEXT NOT NULL | Nombre descriptivo de la aplicación | `Expedientes ERP` |
| `description` | TEXT | Descripción detallada de la aplicación | `Sistema de gestión de expedientes académicos` |
| `owner_team` | TEXT | Equipo responsable de la aplicación | `Equipo Académico` |
| `created_at` | TEXT | Fecha y hora de creación (ISO 8601) | `2025-10-31T05:20:08.187544` |

**Total registros**: 7

### 2. **application_components** - Componentes de Aplicaciones

Define los componentes (frontend/backend) de cada aplicación.

```sql
CREATE TABLE application_components (
    id TEXT PRIMARY KEY,
    application_id TEXT NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    repository_url TEXT,
    tech_stack TEXT,
    health_check_url TEXT,
    created_at TEXT,
    FOREIGN KEY (application_id) REFERENCES applications (id)
);
```

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `id` | TEXT (PK) | Identificador único del componente | `expedientes-frontend` |
| `application_id` | TEXT NOT NULL (FK) | ID de la aplicación padre | `expedientes` |
| `name` | TEXT NOT NULL | Nombre descriptivo del componente | `Expedientes ERP (Frontend)` |
| `type` | TEXT NOT NULL | Tipo de componente | `frontend` / `backend` |
| `repository_url` | TEXT | URL del repositorio en Azure DevOps | `https://dev.azure.com/unirnet/UNIR/_git/...` |
| `tech_stack` | TEXT | Stack tecnológico (separado por comas) | `Angular 18,TypeScript,Docker` |
| `health_check_url` | TEXT | URL para verificar salud del componente | `https://api.example.com/health` |
| `created_at` | TEXT | Fecha y hora de creación | `2025-10-31T05:20:08.187544` |

**Total registros**: 14 (7 frontend + 7 backend)

### 3. **versions** - Versiones de Componentes

Gestiona las versiones de cada componente con información de Git.

```sql
CREATE TABLE versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL,
    component_id TEXT NOT NULL,
    branch TEXT,
    commit_hash TEXT,
    build_number TEXT,
    created_at TEXT,
    features TEXT,
    bug_fixes TEXT,
    FOREIGN KEY (component_id) REFERENCES application_components (id)
);
```

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `id` | INTEGER (PK) | ID autoincremental único | `1` |
| `version` | TEXT NOT NULL | Versión semántica | `18.1.0` |
| `component_id` | TEXT NOT NULL (FK) | ID del componente | `expedientes-frontend` |
| `branch` | TEXT | Rama de Git | `main` / `develop` |
| `commit_hash` | TEXT | Hash del commit de Git | `8177b9bfe80dd8b74b29c97434432c6a7746744c` |
| `build_number` | TEXT | Número de build CI/CD | `BUILD-2025-123` |
| `created_at` | TEXT | Fecha y hora de creación | `2025-10-31T05:20:08.187544` |
| `features` | TEXT | Nuevas características (JSON/texto) | Lista de features añadidas |
| `bug_fixes` | TEXT | Correcciones de errores (JSON/texto) | Lista de bugs corregidos |

**Total registros**: 42

### 4. **deployments** - Despliegues

Registra todos los despliegues realizados en los diferentes entornos.

```sql
CREATE TABLE deployments (
    id TEXT PRIMARY KEY,
    component_id TEXT NOT NULL,
    version_id INTEGER NOT NULL,
    environment TEXT NOT NULL,
    status TEXT NOT NULL,
    deployed_by TEXT,
    deployed_at TEXT,
    notes TEXT,
    FOREIGN KEY (component_id) REFERENCES application_components (id),
    FOREIGN KEY (version_id) REFERENCES versions (id)
);
```

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `id` | TEXT (PK) | Identificador único del despliegue | `deploy-2e960a6d` |
| `component_id` | TEXT NOT NULL (FK) | ID del componente desplegado | `expedientes-frontend` |
| `version_id` | INTEGER NOT NULL (FK) | ID de la versión desplegada | `1` |
| `environment` | TEXT NOT NULL | Entorno de despliegue | `dev` / `pre` / `prod` |
| `status` | TEXT NOT NULL | Estado del despliegue | `success` / `failed` / `pending` / `rollback` |
| `deployed_by` | TEXT | Usuario que realizó el despliegue | `jesus.rodriguez` |
| `deployed_at` | TEXT | Fecha y hora del despliegue | `2025-10-31T05:20:08.187544` |
| `notes` | TEXT | Notas adicionales del despliegue | Información relevante |

**Total registros**: 111

## 🔗 Relaciones entre Tablas

### Jerarquía de Datos

```
Application (1)
    └── Components (N)
            └── Versions (N)
                    └── Deployments (N)
```

### Claves Foráneas

1. **application_components.application_id** → **applications.id**
2. **versions.component_id** → **application_components.id**
3. **deployments.component_id** → **application_components.id**
4. **deployments.version_id** → **versions.id**

### Integridad Referencial

- Eliminar una aplicación elimina todos sus componentes
- Eliminar un componente elimina todas sus versiones y despliegues
- Eliminar una versión elimina todos sus despliegues asociados

## 📝 Ejemplos de Datos

### Aplicación Completa: Expedientes ERP

```sql
-- Aplicación
INSERT INTO applications VALUES (
    'expedientes',
    'Expedientes ERP',
    'Sistema de gestión de expedientes académicos',
    'Equipo Académico',
    '2025-10-31T05:20:08.187544'
);

-- Componente Frontend
INSERT INTO application_components VALUES (
    'expedientes-frontend',
    'expedientes',
    'Expedientes ERP (Frontend)',
    'frontend',
    'https://dev.azure.com/unirnet/UNIR/_git/core-expedienteserp-spa',
    'Angular 18,TypeScript,Docker',
    'https://expedientes-spa.unir.net/health',
    '2025-10-31T05:20:08.187544'
);

-- Versión
INSERT INTO versions VALUES (
    1,
    '18.1.0',
    'expedientes-frontend',
    'main',
    '8177b9bfe80dd8b74b29c97434432c6a7746744c',
    'BUILD-2025-123',
    '2025-10-31T05:20:08.187544',
    'Nueva interfaz de búsqueda, Mejoras de rendimiento',
    'Fix: Error en validación de formularios'
);

-- Despliegue
INSERT INTO deployments VALUES (
    'deploy-2e960a6d',
    'expedientes-frontend',
    1,
    'dev',
    'success',
    'jesus.rodriguez',
    '2025-10-31T05:20:08.187544',
    'Despliegue automático desde pipeline'
);
```

## 🔍 Consultas SQL Útiles

### Consultas de Información General

#### 1. Resumen completo del sistema

```sql
SELECT 
    (SELECT COUNT(*) FROM applications) as total_aplicaciones,
    (SELECT COUNT(*) FROM application_components) as total_componentes,
    (SELECT COUNT(*) FROM versions) as total_versiones,
    (SELECT COUNT(*) FROM deployments) as total_despliegues;
```

#### 2. Estado de despliegues por entorno

```sql
SELECT 
    environment,
    status,
    COUNT(*) as cantidad
FROM deployments 
GROUP BY environment, status 
ORDER BY environment, status;
```

#### 3. Aplicaciones con más despliegues

```sql
SELECT 
    a.name as aplicacion,
    COUNT(d.id) as total_despliegues
FROM applications a
JOIN application_components ac ON a.id = ac.application_id
JOIN deployments d ON ac.id = d.component_id
GROUP BY a.id, a.name
ORDER BY total_despliegues DESC;
```

### Consultas de Despliegues

#### 4. Último despliegue por aplicación y entorno

```sql
SELECT 
    a.name as aplicacion,
    ac.name as componente,
    d.environment,
    v.version,
    d.status,
    d.deployed_at,
    d.deployed_by
FROM applications a
JOIN application_components ac ON a.id = ac.application_id
JOIN deployments d ON ac.id = d.component_id
JOIN versions v ON d.version_id = v.id
WHERE d.id IN (
    SELECT d2.id 
    FROM deployments d2 
    WHERE d2.component_id = d.component_id 
    AND d2.environment = d.environment
    ORDER BY d2.deployed_at DESC 
    LIMIT 1
)
ORDER BY a.name, d.environment;
```

#### 5. Historial de despliegues de una aplicación específica

```sql
SELECT 
    ac.name as componente,
    v.version,
    d.environment,
    d.status,
    d.deployed_by,
    d.deployed_at,
    d.notes
FROM applications a
JOIN application_components ac ON a.id = ac.application_id
JOIN deployments d ON ac.id = d.component_id
JOIN versions v ON d.version_id = v.id
WHERE a.id = 'expedientes'
ORDER BY d.deployed_at DESC;
```

### Consultas de Análisis

#### 6. Componentes sin despliegues

```sql
SELECT 
    a.name as aplicacion,
    ac.name as componente,
    ac.type
FROM applications a
JOIN application_components ac ON a.id = ac.application_id
LEFT JOIN deployments d ON ac.id = d.component_id
WHERE d.id IS NULL;
```

#### 7. Versiones más desplegadas

```sql
SELECT 
    v.version,
    ac.name as componente,
    COUNT(d.id) as total_despliegues
FROM versions v
JOIN application_components ac ON v.component_id = ac.id
JOIN deployments d ON v.id = d.version_id
GROUP BY v.id, v.version, ac.name
HAVING COUNT(d.id) > 1
ORDER BY total_despliegues DESC;
```

#### 8. Despliegues fallidos últimos 7 días

```sql
SELECT 
    a.name as aplicacion,
    ac.name as componente,
    d.environment,
    v.version,
    d.deployed_by,
    d.deployed_at,
    d.notes
FROM deployments d
JOIN application_components ac ON d.component_id = ac.id
JOIN applications a ON ac.application_id = a.id
JOIN versions v ON d.version_id = v.id
WHERE d.status = 'failed'
AND DATE(d.deployed_at) >= DATE('now', '-7 days')
ORDER BY d.deployed_at DESC;
```

### Consultas de Mantenimiento

#### 9. Verificar integridad referencial

```sql
-- Componentes huérfanos
SELECT ac.* 
FROM application_components ac 
LEFT JOIN applications a ON ac.application_id = a.id 
WHERE a.id IS NULL;

-- Versiones huérfanas
SELECT v.* 
FROM versions v 
LEFT JOIN application_components ac ON v.component_id = ac.id 
WHERE ac.id IS NULL;

-- Despliegues huérfanos
SELECT d.* 
FROM deployments d 
LEFT JOIN application_components ac ON d.component_id = ac.id 
LEFT JOIN versions v ON d.version_id = v.id 
WHERE ac.id IS NULL OR v.id IS NULL;
```

#### 10. Estadísticas por equipo

```sql
SELECT 
    a.owner_team as equipo,
    COUNT(DISTINCT a.id) as aplicaciones,
    COUNT(DISTINCT ac.id) as componentes,
    COUNT(DISTINCT v.id) as versiones,
    COUNT(d.id) as despliegues
FROM applications a
LEFT JOIN application_components ac ON a.id = ac.application_id
LEFT JOIN versions v ON ac.id = v.component_id
LEFT JOIN deployments d ON ac.id = d.component_id
GROUP BY a.owner_team
ORDER BY aplicaciones DESC;
```

## 🛠️ Mantenimiento

### Tareas Regulares

#### Limpieza de Datos Antiguos

```sql
-- Eliminar despliegues anteriores a 6 meses
DELETE FROM deployments 
WHERE DATE(deployed_at) < DATE('now', '-6 months');

-- Eliminar versiones sin despliegues asociados
DELETE FROM versions 
WHERE id NOT IN (SELECT DISTINCT version_id FROM deployments);
```

#### Optimización

```sql
-- Reindexar base de datos
REINDEX;

-- Limpiar espacio no utilizado
VACUUM;

-- Analizar estadísticas para optimizar consultas
ANALYZE;
```

#### Verificación de Integridad

```sql
-- Verificar integridad de la base de datos
PRAGMA integrity_check;

-- Verificar claves foráneas
PRAGMA foreign_key_check;
```

### Índices Recomendados

```sql
-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_deployments_environment ON deployments(environment);
CREATE INDEX IF NOT EXISTS idx_deployments_status ON deployments(status);
CREATE INDEX IF NOT EXISTS idx_deployments_deployed_at ON deployments(deployed_at);
CREATE INDEX IF NOT EXISTS idx_versions_component_id ON versions(component_id);
CREATE INDEX IF NOT EXISTS idx_components_application_id ON application_components(application_id);
```

## 💾 Backup y Restauración

### Backup Manual

```bash
# Backup completo de la base de datos
cp data/deployments.db data/backup/deployments_$(date +%Y%m%d_%H%M%S).db

# Backup en formato SQL
sqlite3 data/deployments.db .dump > data/backup/deployments_$(date +%Y%m%d_%H%M%S).sql
```

### Restauración

```bash
# Restaurar desde archivo .db
cp data/backup/deployments_20251031_143000.db data/deployments.db

# Restaurar desde archivo SQL
sqlite3 data/deployments_new.db < data/backup/deployments_20251031_143000.sql
```

### Script de Backup Automático

```python
#!/usr/bin/env python3
import sqlite3
import shutil
import os
from datetime import datetime

def backup_database():
    source = "data/deployments.db"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "data/backup"
    
    # Crear directorio de backup si no existe
    os.makedirs(backup_dir, exist_ok=True)
    
    # Backup binario
    binary_backup = f"{backup_dir}/deployments_{timestamp}.db"
    shutil.copy2(source, binary_backup)
    
    # Backup SQL
    sql_backup = f"{backup_dir}/deployments_{timestamp}.sql"
    with sqlite3.connect(source) as conn:
        with open(sql_backup, 'w') as f:
            for line in conn.iterdump():
                f.write('%s\n' % line)
    
    print(f"Backup completado: {binary_backup}, {sql_backup}")

if __name__ == "__main__":
    backup_database()
```

## 📊 Configuración de la Base de Datos

### Configuración SQLite Recomendada

```sql
-- Habilitar claves foráneas
PRAGMA foreign_keys = ON;

-- Configurar journal mode para mejor concurrencia
PRAGMA journal_mode = WAL;

-- Configurar sincronización para mejor rendimiento
PRAGMA synchronous = NORMAL;

-- Configurar timeout para evitar bloqueos
PRAGMA busy_timeout = 30000;
```

### Variables de Entorno

```bash
# Configuración de la base de datos
DB_PATH=data/deployments.db
DB_BACKUP_DIR=data/backup
DB_AUTO_BACKUP=true
DB_BACKUP_RETENTION_DAYS=30
```

---

## 📞 Soporte

Para dudas sobre la base de datos o problemas de integridad:

- **Email**: soporte@unir.net
- **Documentación**: [GitHub Wiki](https://github.com/jesusprodriguezUnir/Agents/wiki)
- **Issues**: [GitHub Issues](https://github.com/jesusprodriguezUnir/Agents/issues)

---

*Documentación actualizada: 31 de octubre de 2025*