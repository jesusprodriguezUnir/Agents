# 🏗️ Diseño del Nuevo Esquema Multi-Organización

## 📊 Esquema Propuesto

### Diagrama de Relaciones

```
┌─────────────────┐    1:N    ┌──────────────────────┐    1:N    ┌─────────────────┐
│  organizations  │◄──────────┤    environments      │◄──────────┤ environment_urls│
│                 │           │                      │           │                 │
│ • id (PK)       │           │ • id (PK)            │           │ • id (PK)       │
│ • name          │           │ • organization_id    │           │ • environment_id│
│ • description   │           │ • name               │           │ • component_id  │
│ • active        │           │ • display_name       │           │ • url_type      │
│ • created_at    │           │ • order_priority     │           │ • url           │
└─────────────────┘           │ • active             │           │ • description   │
        │                     │ • created_at         │           └─────────────────┘
        │ 1:N                 └──────────────────────┘
        ▼                               │ 1:N
┌─────────────────┐                     ▼
│   applications  │           ┌─────────────────────────────────┐
│                 │           │         deployments            │
│ • id (PK)       │           │                                 │
│ • organization_id (FK)      │ • id (PK)                      │
│ • name          │           │ • component_id (FK)             │
│ • description   │           │ • version_id (FK)              │
│ • owner_team    │           │ • environment_id (FK) ────────►│
│ • created_at    │           │ • status                       │
└─────────────────┘           │ • deployed_by                  │
        │ 1:N                 │ • deployed_at                  │
        ▼                     │ • notes                        │
┌─────────────────┐           └─────────────────────────────────┘
│app_components   │                     ▲
│                 │                     │ N:1
│ • id (PK)       │           ┌─────────────────┐
│ • application_id│           │    versions     │
│ • name          │           │                 │
│ • type          │           │ • id (PK)       │
│ • repository_url│           │ • component_id  │
│ • tech_stack    │           │ • version       │
│ • created_at    │──────────►│ • branch        │
└─────────────────┘   1:N     │ • commit_hash   │
                              │ • features      │
                              │ • created_at    │
                              └─────────────────┘
```

### Cambios Principales

1. **Nueva tabla `organizations`**: Define proeduca y villanueva
2. **Nueva tabla `environments`**: Entornos flexibles por organización
3. **Nueva tabla `environment_urls`**: URLs específicas por entorno/componente
4. **Modificación `applications`**: Vinculada a organización
5. **Modificación `deployments`**: Usa environment_id en lugar de campo texto

## 🗄️ Definición de Tablas

### 1. organizations
```sql
CREATE TABLE organizations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    description TEXT,
    active BOOLEAN NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT
);
```

### 2. environments
```sql
CREATE TABLE environments (
    id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL,
    name TEXT NOT NULL,           -- des, pre, test, pro
    display_name TEXT NOT NULL,   -- Desarrollo, Preproducción, Test, Producción
    description TEXT,
    order_priority INTEGER DEFAULT 1,
    active BOOLEAN NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations (id),
    UNIQUE(organization_id, name)
);
```

### 3. environment_urls
```sql
CREATE TABLE environment_urls (
    id TEXT PRIMARY KEY,
    environment_id TEXT NOT NULL,
    component_id TEXT NOT NULL,
    url_type TEXT NOT NULL,       -- health_check, version_api, main_app
    url TEXT NOT NULL,
    description TEXT,
    active BOOLEAN NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    FOREIGN KEY (environment_id) REFERENCES environments (id),
    FOREIGN KEY (component_id) REFERENCES application_components (id),
    UNIQUE(environment_id, component_id, url_type)
);
```

### 4. applications (modificada)
```sql
ALTER TABLE applications ADD COLUMN organization_id TEXT;
-- Migración: UPDATE applications SET organization_id = 'proeduca' WHERE organization_id IS NULL;
ALTER TABLE applications ADD FOREIGN KEY (organization_id) REFERENCES organizations (id);
```

### 5. deployments (modificada)
```sql
ALTER TABLE deployments ADD COLUMN environment_id TEXT;
-- Migración compleja para mapear environment + organization
ALTER TABLE deployments ADD FOREIGN KEY (environment_id) REFERENCES environments (id);
-- Después de migración: ALTER TABLE deployments DROP COLUMN environment;
```

## 📋 Datos Iniciales

### Organizaciones
```sql
INSERT INTO organizations VALUES 
('proeduca', 'proeduca', 'PROEDUCA', 'Organización principal PROEDUCA', 1, datetime('now'), NULL),
('villanueva', 'villanueva', 'VILLANUEVA', 'Organización VILLANUEVA', 1, datetime('now'), NULL);
```

### Entornos PROEDUCA
```sql
INSERT INTO environments VALUES 
('proeduca-des', 'proeduca', 'des', 'Desarrollo', 'Entorno de desarrollo PROEDUCA', 1, 1, datetime('now')),
('proeduca-pre', 'proeduca', 'pre', 'Preproducción', 'Entorno de preproducción PROEDUCA', 2, 1, datetime('now')),
('proeduca-test', 'proeduca', 'test', 'Test', 'Entorno de testing PROEDUCA', 3, 1, datetime('now')),
('proeduca-pro', 'proeduca', 'pro', 'Producción', 'Entorno de producción PROEDUCA', 4, 1, datetime('now'));
```

### Entornos VILLANUEVA
```sql
INSERT INTO environments VALUES 
('villanueva-pre', 'villanueva', 'pre', 'Preproducción', 'Entorno de preproducción VILLANUEVA', 1, 1, datetime('now')),
('villanueva-pro', 'villanueva', 'pro', 'Producción', 'Entorno de producción VILLANUEVA', 2, 1, datetime('now'));
```

### URLs de Ejemplo
```sql
INSERT INTO environment_urls VALUES 
('url-1', 'proeduca-des', 'expedientes-frontend', 'main_app', 'https://expedientes-des.proeduca.es', 'App principal', 1, datetime('now')),
('url-2', 'proeduca-des', 'expedientes-frontend', 'version_api', 'https://expedientes-des.proeduca.es/api/version', 'API versión', 1, datetime('now')),
('url-3', 'proeduca-des', 'expedientes-backend', 'health_check', 'https://api-expedientes-des.proeduca.es/health', 'Health check', 1, datetime('now'));
```

## 🔄 Impacto en Consultas

### Consulta Estado por Organización
```sql
SELECT 
    o.display_name as organizacion,
    e.display_name as entorno,
    a.name as aplicacion,
    ac.name as componente,
    COUNT(d.id) as despliegues,
    MAX(d.deployed_at) as ultimo_despliegue
FROM organizations o
JOIN environments e ON o.id = e.organization_id
JOIN applications a ON o.id = a.organization_id
JOIN application_components ac ON a.id = ac.application_id
LEFT JOIN deployments d ON ac.id = d.component_id AND e.id = d.environment_id
GROUP BY o.id, e.id, a.id, ac.id
ORDER BY o.name, e.order_priority, a.name;
```

### URLs por Entorno
```sql
SELECT 
    o.name as org,
    e.name as env,
    a.name as app,
    ac.name as component,
    eu.url_type,
    eu.url
FROM organizations o
JOIN environments e ON o.id = e.organization_id
JOIN applications a ON o.id = a.organization_id
JOIN application_components ac ON a.id = ac.application_id
JOIN environment_urls eu ON e.id = eu.environment_id AND ac.id = eu.component_id
WHERE o.name = 'proeduca' AND e.name = 'des';
```

## 🎯 Beneficios del Nuevo Esquema

✅ **Flexibilidad**: Entornos diferentes por organización  
✅ **Escalabilidad**: Fácil agregar nuevas organizaciones  
✅ **URLs Estructuradas**: Múltiples URLs por componente/entorno  
✅ **Mantenimiento**: Activar/desactivar entornos u organizaciones  
✅ **Orden**: Prioridad de entornos configurable  
✅ **Trazabilidad**: Despliegues vinculados a entorno específico  

## ⚠️ Consideraciones de Migración

1. **Backup obligatorio** antes de migración
2. **Mapeo de datos existentes** environment → environment_id
3. **Verificación de integridad** post-migración
4. **Actualización de herramientas** MCP y frontend
5. **Regeneración de datos** de ejemplo si es necesario