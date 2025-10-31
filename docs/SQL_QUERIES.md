# 🔍 Consultas SQL Avanzadas - MCP Deployment Manager

## 📋 Índice

- [Consultas de Análisis](#consultas-de-análisis)
- [Consultas de Rendimiento](#consultas-de-rendimiento)
- [Consultas de Auditoría](#consultas-de-auditoría)
- [Vistas Útiles](#vistas-útiles)
- [Procedimientos de Mantenimiento](#procedimientos-de-mantenimiento)
- [Scripts de Migración](#scripts-de-migración)

## 📊 Consultas de Análisis

### 1. Dashboard Ejecutivo - Métricas Principales

```sql
-- Resumen completo para dashboard ejecutivo
SELECT 
    'Aplicaciones Totales' as metrica,
    COUNT(*) as valor,
    'aplicaciones' as unidad
FROM applications

UNION ALL

SELECT 
    'Componentes Activos' as metrica,
    COUNT(*) as valor,
    'componentes' as unidad
FROM application_components

UNION ALL

SELECT 
    'Versiones Disponibles' as metrica,
    COUNT(*) as valor,
    'versiones' as unidad
FROM versions

UNION ALL

SELECT 
    'Despliegues Este Mes' as metrica,
    COUNT(*) as valor,
    'despliegues' as unidad
FROM deployments 
WHERE DATE(deployed_at) >= DATE('now', 'start of month')

UNION ALL

SELECT 
    'Tasa de Éxito (%)' as metrica,
    ROUND(
        (COUNT(CASE WHEN status = 'success' THEN 1 END) * 100.0) / COUNT(*), 
        2
    ) as valor,
    '%' as unidad
FROM deployments 
WHERE DATE(deployed_at) >= DATE('now', '-30 days');
```

### 2. Estado de Entornos por Aplicación

```sql
-- Vista completa del estado de cada entorno por aplicación
SELECT 
    a.name as aplicacion,
    a.owner_team as equipo,
    COUNT(DISTINCT ac.id) as total_componentes,
    
    -- Estado DEV
    COUNT(DISTINCT CASE 
        WHEN d_dev.environment = 'dev' AND d_dev.status = 'success' 
        THEN ac.id END) as dev_ok,
    COUNT(DISTINCT CASE 
        WHEN d_dev.environment = 'dev' AND d_dev.status = 'failed' 
        THEN ac.id END) as dev_failed,
    
    -- Estado PRE
    COUNT(DISTINCT CASE 
        WHEN d_pre.environment = 'pre' AND d_pre.status = 'success' 
        THEN ac.id END) as pre_ok,
    COUNT(DISTINCT CASE 
        WHEN d_pre.environment = 'pre' AND d_pre.status = 'failed' 
        THEN ac.id END) as pre_failed,
    
    -- Estado PROD
    COUNT(DISTINCT CASE 
        WHEN d_prod.environment = 'prod' AND d_prod.status = 'success' 
        THEN ac.id END) as prod_ok,
    COUNT(DISTINCT CASE 
        WHEN d_prod.environment = 'prod' AND d_prod.status = 'failed' 
        THEN ac.id END) as prod_failed

FROM applications a
LEFT JOIN application_components ac ON a.id = ac.application_id
LEFT JOIN deployments d_dev ON ac.id = d_dev.component_id 
    AND d_dev.environment = 'dev'
    AND d_dev.id = (
        SELECT d2.id FROM deployments d2 
        WHERE d2.component_id = ac.id AND d2.environment = 'dev'
        ORDER BY d2.deployed_at DESC LIMIT 1
    )
LEFT JOIN deployments d_pre ON ac.id = d_pre.component_id 
    AND d_pre.environment = 'pre'
    AND d_pre.id = (
        SELECT d2.id FROM deployments d2 
        WHERE d2.component_id = ac.id AND d2.environment = 'pre'
        ORDER BY d2.deployed_at DESC LIMIT 1
    )
LEFT JOIN deployments d_prod ON ac.id = d_prod.component_id 
    AND d_prod.environment = 'prod'
    AND d_prod.id = (
        SELECT d2.id FROM deployments d2 
        WHERE d2.component_id = ac.id AND d2.environment = 'prod'
        ORDER BY d2.deployed_at DESC LIMIT 1
    )
GROUP BY a.id, a.name, a.owner_team
ORDER BY a.name;
```

### 3. Análisis de Frecuencia de Despliegues

```sql
-- Frecuencia de despliegues por aplicación y período
SELECT 
    a.name as aplicacion,
    ac.type as tipo_componente,
    COUNT(d.id) as total_despliegues,
    
    -- Por período
    COUNT(CASE WHEN DATE(d.deployed_at) >= DATE('now', '-7 days') 
          THEN 1 END) as ultima_semana,
    COUNT(CASE WHEN DATE(d.deployed_at) >= DATE('now', '-30 days') 
          THEN 1 END) as ultimo_mes,
    COUNT(CASE WHEN DATE(d.deployed_at) >= DATE('now', '-90 days') 
          THEN 1 END) as ultimo_trimestre,
    
    -- Promedio por día (últimos 30 días)
    ROUND(
        COUNT(CASE WHEN DATE(d.deployed_at) >= DATE('now', '-30 days') 
              THEN 1 END) / 30.0, 
        2
    ) as promedio_diario_30d,
    
    -- Último despliegue
    MAX(d.deployed_at) as ultimo_despliegue

FROM applications a
JOIN application_components ac ON a.id = ac.application_id
LEFT JOIN deployments d ON ac.id = d.component_id
GROUP BY a.id, a.name, ac.id, ac.type
HAVING COUNT(d.id) > 0
ORDER BY total_despliegues DESC;
```

### 4. Análisis de Versiones y Promoción

```sql
-- Análisis de promoción de versiones entre entornos
WITH version_promotions AS (
    SELECT 
        a.name as aplicacion,
        ac.name as componente,
        v.version,
        
        -- Verificar si existe en cada entorno
        MAX(CASE WHEN d.environment = 'dev' AND d.status = 'success' 
            THEN 1 ELSE 0 END) as en_dev,
        MAX(CASE WHEN d.environment = 'pre' AND d.status = 'success' 
            THEN 1 ELSE 0 END) as en_pre,
        MAX(CASE WHEN d.environment = 'prod' AND d.status = 'success' 
            THEN 1 ELSE 0 END) as en_prod,
            
        -- Fechas de promoción
        MIN(CASE WHEN d.environment = 'dev' AND d.status = 'success' 
            THEN d.deployed_at END) as fecha_dev,
        MIN(CASE WHEN d.environment = 'pre' AND d.status = 'success' 
            THEN d.deployed_at END) as fecha_pre,
        MIN(CASE WHEN d.environment = 'prod' AND d.status = 'success' 
            THEN d.deployed_at END) as fecha_prod
            
    FROM applications a
    JOIN application_components ac ON a.id = ac.application_id
    JOIN versions v ON ac.id = v.component_id
    LEFT JOIN deployments d ON v.id = d.version_id
    GROUP BY a.id, ac.id, v.id
)
SELECT 
    aplicacion,
    componente,
    version,
    
    -- Estado de promoción
    CASE 
        WHEN en_prod = 1 THEN 'En Producción'
        WHEN en_pre = 1 THEN 'En Preproducción'
        WHEN en_dev = 1 THEN 'Solo en Desarrollo'
        ELSE 'Sin Desplegar'
    END as estado_promocion,
    
    -- Tiempo de promoción (dev a prod)
    CASE 
        WHEN fecha_dev IS NOT NULL AND fecha_prod IS NOT NULL 
        THEN ROUND(
            (JULIANDAY(fecha_prod) - JULIANDAY(fecha_dev)) * 24, 
            2
        ) 
    END as horas_dev_a_prod,
    
    fecha_dev,
    fecha_pre,
    fecha_prod
    
FROM version_promotions
WHERE en_dev = 1 OR en_pre = 1 OR en_prod = 1
ORDER BY aplicacion, componente, version DESC;
```

## ⚡ Consultas de Rendimiento

### 5. Tiempo de Despliegue por Aplicación

```sql
-- Análisis de tiempo entre despliegues
WITH deployment_times AS (
    SELECT 
        a.name as aplicacion,
        ac.name as componente,
        d.environment,
        d.deployed_at,
        d.status,
        LAG(d.deployed_at) OVER (
            PARTITION BY ac.id, d.environment 
            ORDER BY d.deployed_at
        ) as prev_deployment
    FROM applications a
    JOIN application_components ac ON a.id = ac.application_id
    JOIN deployments d ON ac.id = d.component_id
    WHERE d.status = 'success'
)
SELECT 
    aplicacion,
    environment,
    COUNT(*) as total_despliegues,
    
    -- Tiempo promedio entre despliegues
    ROUND(
        AVG(
            CASE WHEN prev_deployment IS NOT NULL 
            THEN (JULIANDAY(deployed_at) - JULIANDAY(prev_deployment)) * 24 
            END
        ), 
        2
    ) as horas_promedio_entre_despliegues,
    
    -- Tiempo mínimo y máximo
    ROUND(
        MIN(
            CASE WHEN prev_deployment IS NOT NULL 
            THEN (JULIANDAY(deployed_at) - JULIANDAY(prev_deployment)) * 24 
            END
        ), 
        2
    ) as horas_minimas,
    
    ROUND(
        MAX(
            CASE WHEN prev_deployment IS NOT NULL 
            THEN (JULIANDAY(deployed_at) - JULIANDAY(prev_deployment)) * 24 
            END
        ), 
        2
    ) as horas_maximas

FROM deployment_times
WHERE prev_deployment IS NOT NULL
GROUP BY aplicacion, environment
ORDER BY aplicacion, environment;
```

### 6. Componentes Más Problemáticos

```sql
-- Identificar componentes con más fallos
SELECT 
    a.name as aplicacion,
    ac.name as componente,
    ac.type,
    
    -- Estadísticas de despliegues
    COUNT(d.id) as total_despliegues,
    COUNT(CASE WHEN d.status = 'success' THEN 1 END) as exitosos,
    COUNT(CASE WHEN d.status = 'failed' THEN 1 END) as fallidos,
    COUNT(CASE WHEN d.status = 'rollback' THEN 1 END) as rollbacks,
    
    -- Tasa de éxito
    ROUND(
        (COUNT(CASE WHEN d.status = 'success' THEN 1 END) * 100.0) / COUNT(d.id), 
        2
    ) as tasa_exito_pct,
    
    -- Tiempo promedio hasta fallo
    ROUND(
        AVG(
            CASE WHEN d.status = 'failed' 
            THEN (JULIANDAY(d.deployed_at) - JULIANDAY(v.created_at)) * 24 
            END
        ), 
        2
    ) as horas_promedio_hasta_fallo,
    
    -- Último despliegue fallido
    MAX(CASE WHEN d.status = 'failed' THEN d.deployed_at END) as ultimo_fallo

FROM applications a
JOIN application_components ac ON a.id = ac.application_id
LEFT JOIN deployments d ON ac.id = d.component_id
LEFT JOIN versions v ON d.version_id = v.id
GROUP BY a.id, ac.id
HAVING COUNT(d.id) > 0
ORDER BY 
    tasa_exito_pct ASC, 
    fallidos DESC;
```

## 🔍 Consultas de Auditoría

### 7. Auditoría de Cambios de Estado

```sql
-- Rastrear cambios de estado en despliegues
WITH deployment_changes AS (
    SELECT 
        d.id,
        d.component_id,
        d.environment,
        d.status,
        d.deployed_by,
        d.deployed_at,
        LAG(d.status) OVER (
            PARTITION BY d.component_id, d.environment 
            ORDER BY d.deployed_at
        ) as previous_status,
        LAG(d.deployed_by) OVER (
            PARTITION BY d.component_id, d.environment 
            ORDER BY d.deployed_at
        ) as previous_deployed_by
    FROM deployments d
)
SELECT 
    a.name as aplicacion,
    ac.name as componente,
    dc.environment,
    dc.previous_status,
    dc.status as current_status,
    dc.previous_deployed_by,
    dc.deployed_by as current_deployed_by,
    dc.deployed_at,
    
    -- Identificar cambios problemáticos
    CASE 
        WHEN dc.previous_status = 'success' AND dc.status = 'failed'
        THEN 'Regresión'
        WHEN dc.previous_status = 'failed' AND dc.status = 'success'
        THEN 'Recuperación'
        WHEN dc.status = 'rollback'
        THEN 'Rollback'
        ELSE 'Normal'
    END as tipo_cambio

FROM deployment_changes dc
JOIN application_components ac ON dc.component_id = ac.id
JOIN applications a ON ac.application_id = a.id
WHERE dc.previous_status IS NOT NULL
    AND dc.previous_status != dc.status
ORDER BY dc.deployed_at DESC;
```

### 8. Actividad por Usuario

```sql
-- Análisis de actividad de despliegue por usuario
SELECT 
    d.deployed_by as usuario,
    COUNT(d.id) as total_despliegues,
    COUNT(DISTINCT ac.application_id) as aplicaciones_diferentes,
    COUNT(DISTINCT d.environment) as entornos_diferentes,
    
    -- Por estado
    COUNT(CASE WHEN d.status = 'success' THEN 1 END) as exitosos,
    COUNT(CASE WHEN d.status = 'failed' THEN 1 END) as fallidos,
    
    -- Tasa de éxito
    ROUND(
        (COUNT(CASE WHEN d.status = 'success' THEN 1 END) * 100.0) / COUNT(d.id), 
        2
    ) as tasa_exito_pct,
    
    -- Actividad temporal
    MIN(d.deployed_at) as primer_despliegue,
    MAX(d.deployed_at) as ultimo_despliegue,
    
    -- Promedio por día (últimos 30 días)
    ROUND(
        COUNT(CASE WHEN DATE(d.deployed_at) >= DATE('now', '-30 days') 
              THEN 1 END) / 30.0, 
        2
    ) as promedio_diario_30d

FROM deployments d
JOIN application_components ac ON d.component_id = ac.id
WHERE d.deployed_by IS NOT NULL
GROUP BY d.deployed_by
HAVING COUNT(d.id) > 0
ORDER BY total_despliegues DESC;
```

## 📊 Vistas Útiles

### 9. Vista: Estado Actual de Componentes

```sql
-- Crear vista para estado actual de todos los componentes
CREATE VIEW IF NOT EXISTS current_component_status AS
SELECT 
    a.id as app_id,
    a.name as app_name,
    a.owner_team,
    ac.id as component_id,
    ac.name as component_name,
    ac.type as component_type,
    ac.repository_url,
    ac.tech_stack,
    
    -- Último despliegue en DEV
    (SELECT v.version FROM deployments d 
     JOIN versions v ON d.version_id = v.id
     WHERE d.component_id = ac.id AND d.environment = 'dev' 
     AND d.status = 'success'
     ORDER BY d.deployed_at DESC LIMIT 1) as current_dev_version,
     
    (SELECT d.deployed_at FROM deployments d 
     WHERE d.component_id = ac.id AND d.environment = 'dev' 
     AND d.status = 'success'
     ORDER BY d.deployed_at DESC LIMIT 1) as dev_deployed_at,
    
    -- Último despliegue en PRE
    (SELECT v.version FROM deployments d 
     JOIN versions v ON d.version_id = v.id
     WHERE d.component_id = ac.id AND d.environment = 'pre' 
     AND d.status = 'success'
     ORDER BY d.deployed_at DESC LIMIT 1) as current_pre_version,
     
    (SELECT d.deployed_at FROM deployments d 
     WHERE d.component_id = ac.id AND d.environment = 'pre' 
     AND d.status = 'success'
     ORDER BY d.deployed_at DESC LIMIT 1) as pre_deployed_at,
    
    -- Último despliegue en PROD
    (SELECT v.version FROM deployments d 
     JOIN versions v ON d.version_id = v.id
     WHERE d.component_id = ac.id AND d.environment = 'prod' 
     AND d.status = 'success'
     ORDER BY d.deployed_at DESC LIMIT 1) as current_prod_version,
     
    (SELECT d.deployed_at FROM deployments d 
     WHERE d.component_id = ac.id AND d.environment = 'prod' 
     AND d.status = 'success'
     ORDER BY d.deployed_at DESC LIMIT 1) as prod_deployed_at

FROM applications a
JOIN application_components ac ON a.id = ac.application_id;
```

### 10. Vista: Métricas de Rendimiento

```sql
-- Crear vista para métricas de rendimiento por aplicación
CREATE VIEW IF NOT EXISTS app_performance_metrics AS
SELECT 
    a.id as app_id,
    a.name as app_name,
    a.owner_team,
    
    -- Métricas generales
    COUNT(DISTINCT ac.id) as total_components,
    COUNT(DISTINCT v.id) as total_versions,
    COUNT(d.id) as total_deployments,
    
    -- Métricas de éxito
    COUNT(CASE WHEN d.status = 'success' THEN 1 END) as successful_deployments,
    COUNT(CASE WHEN d.status = 'failed' THEN 1 END) as failed_deployments,
    COUNT(CASE WHEN d.status = 'rollback' THEN 1 END) as rollback_deployments,
    
    -- Tasa de éxito
    ROUND(
        (COUNT(CASE WHEN d.status = 'success' THEN 1 END) * 100.0) / 
        NULLIF(COUNT(d.id), 0), 
        2
    ) as success_rate_pct,
    
    -- Actividad reciente
    COUNT(CASE WHEN DATE(d.deployed_at) >= DATE('now', '-7 days') 
          THEN 1 END) as deployments_last_7_days,
    COUNT(CASE WHEN DATE(d.deployed_at) >= DATE('now', '-30 days') 
          THEN 1 END) as deployments_last_30_days,
    
    -- Fechas importantes
    MIN(d.deployed_at) as first_deployment,
    MAX(d.deployed_at) as last_deployment

FROM applications a
LEFT JOIN application_components ac ON a.id = ac.application_id
LEFT JOIN versions v ON ac.id = v.component_id
LEFT JOIN deployments d ON ac.id = d.component_id
GROUP BY a.id, a.name, a.owner_team;
```

## 🛠️ Procedimientos de Mantenimiento

### 11. Limpieza de Datos Antiguos

```sql
-- Script de limpieza de datos antiguos (ejecutar mensualmente)
BEGIN TRANSACTION;

-- 1. Eliminar despliegues fallidos anteriores a 6 meses
DELETE FROM deployments 
WHERE status = 'failed' 
AND DATE(deployed_at) < DATE('now', '-6 months');

-- 2. Eliminar versiones sin despliegues asociados y anteriores a 1 año
DELETE FROM versions 
WHERE id NOT IN (SELECT DISTINCT version_id FROM deployments WHERE version_id IS NOT NULL)
AND DATE(created_at) < DATE('now', '-1 year');

-- 3. Verificar que no hay registros huérfanos
SELECT 'Componentes huérfanos' as check_type, COUNT(*) as count
FROM application_components ac 
LEFT JOIN applications a ON ac.application_id = a.id 
WHERE a.id IS NULL

UNION ALL

SELECT 'Versiones huérfanas' as check_type, COUNT(*) as count
FROM versions v 
LEFT JOIN application_components ac ON v.component_id = ac.id 
WHERE ac.id IS NULL

UNION ALL

SELECT 'Despliegues huérfanos (componente)' as check_type, COUNT(*) as count
FROM deployments d 
LEFT JOIN application_components ac ON d.component_id = ac.id 
WHERE ac.id IS NULL

UNION ALL

SELECT 'Despliegues huérfanos (versión)' as check_type, COUNT(*) as count
FROM deployments d 
LEFT JOIN versions v ON d.version_id = v.id 
WHERE d.version_id IS NOT NULL AND v.id IS NULL;

COMMIT;
```

### 12. Reindexación y Optimización

```sql
-- Script de optimización (ejecutar semanalmente)
-- Reindexar todas las tablas
REINDEX;

-- Actualizar estadísticas de consulta
ANALYZE;

-- Limpiar espacio no utilizado
VACUUM;

-- Verificar integridad
PRAGMA integrity_check;

-- Estadísticas de la base de datos
SELECT 
    'Total pages' as metric,
    page_count as value 
FROM pragma_page_count()

UNION ALL

SELECT 
    'Page size' as metric,
    page_size as value 
FROM pragma_page_size()

UNION ALL

SELECT 
    'Database size (KB)' as metric,
    (page_count * page_size) / 1024 as value 
FROM pragma_page_count(), pragma_page_size();
```

## 🔄 Scripts de Migración

### 13. Migración: Añadir Campo de Prioridad

```sql
-- Migración para añadir campo de prioridad a aplicaciones
BEGIN TRANSACTION;

-- Verificar si la columna ya existe
SELECT sql FROM sqlite_master 
WHERE type='table' AND name='applications';

-- Añadir nueva columna (si no existe)
ALTER TABLE applications 
ADD COLUMN priority INTEGER DEFAULT 1 
CHECK (priority IN (1, 2, 3, 4, 5));

-- Actualizar prioridades basadas en equipo
UPDATE applications 
SET priority = CASE 
    WHEN owner_team = 'Equipo Académico' THEN 1
    WHEN owner_team = 'Equipo Técnico' THEN 2
    WHEN owner_team = 'Equipo DevOps' THEN 3
    ELSE 4
END;

-- Verificar cambios
SELECT name, owner_team, priority FROM applications;

COMMIT;
```

### 14. Migración: Índices de Rendimiento

```sql
-- Crear índices para mejorar rendimiento
BEGIN TRANSACTION;

-- Índices para deployments (tabla más consultada)
CREATE INDEX IF NOT EXISTS idx_deployments_component_env 
ON deployments(component_id, environment);

CREATE INDEX IF NOT EXISTS idx_deployments_env_status 
ON deployments(environment, status);

CREATE INDEX IF NOT EXISTS idx_deployments_deployed_at_desc 
ON deployments(deployed_at DESC);

CREATE INDEX IF NOT EXISTS idx_deployments_status_date 
ON deployments(status, deployed_at);

-- Índices para versions
CREATE INDEX IF NOT EXISTS idx_versions_component_created 
ON versions(component_id, created_at DESC);

-- Índices para application_components
CREATE INDEX IF NOT EXISTS idx_components_app_type 
ON application_components(application_id, type);

-- Verificar índices creados
SELECT name, sql FROM sqlite_master 
WHERE type='index' AND name LIKE 'idx_%';

COMMIT;
```

### 15. Script de Validación Post-Migración

```sql
-- Validar integridad después de migraciones
SELECT 
    'applications' as tabla,
    COUNT(*) as registros,
    COUNT(DISTINCT id) as ids_unicos,
    CASE 
        WHEN COUNT(*) = COUNT(DISTINCT id) THEN 'OK' 
        ELSE 'ERROR: IDs duplicados' 
    END as estado
FROM applications

UNION ALL

SELECT 
    'application_components' as tabla,
    COUNT(*) as registros,
    COUNT(DISTINCT id) as ids_unicos,
    CASE 
        WHEN COUNT(*) = COUNT(DISTINCT id) THEN 'OK' 
        ELSE 'ERROR: IDs duplicados' 
    END as estado
FROM application_components

UNION ALL

SELECT 
    'versions' as tabla,
    COUNT(*) as registros,
    COUNT(DISTINCT id) as ids_unicos,
    CASE 
        WHEN COUNT(*) = COUNT(DISTINCT id) THEN 'OK' 
        ELSE 'ERROR: IDs duplicados' 
    END as estado
FROM versions

UNION ALL

SELECT 
    'deployments' as tabla,
    COUNT(*) as registros,
    COUNT(DISTINCT id) as ids_unicos,
    CASE 
        WHEN COUNT(*) = COUNT(DISTINCT id) THEN 'OK' 
        ELSE 'ERROR: IDs duplicados' 
    END as estado
FROM deployments;

-- Verificar integridad referencial
PRAGMA foreign_key_check;
```

---

## 📞 Soporte Técnico

Para consultas sobre estas consultas SQL o problemas de rendimiento:

- **Documentación Principal**: [DATABASE.md](DATABASE.md)
- **Issues**: [GitHub Issues](https://github.com/jesusprodriguezUnir/Agents/issues)
- **Wiki**: [Database Troubleshooting](https://github.com/jesusprodriguezUnir/Agents/wiki/Database-Troubleshooting)

---

*Consultas SQL avanzadas - Actualizado: 31 de octubre de 2025*