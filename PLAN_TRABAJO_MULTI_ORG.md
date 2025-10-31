# 📋 Plan de Trabajo Completo: Sistema Multi-Organización

## ✅ **FASE 1: DISEÑO Y PREPARACIÓN** (Completada)

### 1.1 ✅ Diseño del Nuevo Esquema
- **Archivo**: `docs/NEW_SCHEMA_DESIGN.md`
- **Resultado**: Esquema multi-organización definido con:
  - Tabla `organizations` (proeduca, villanueva)
  - Tabla `environments` (entornos flexibles por organización)
  - Tabla `environment_urls` (URLs específicas por entorno/componente)
  - Modificaciones a tablas existentes

### 1.2 ✅ Script de Migración
- **Archivo**: `migrate_to_multi_org.py`
- **Funcionalidades**:
  - Backup automático antes de migración
  - Creación de nuevas tablas
  - Migración de datos existentes
  - Verificación de integridad
  - Reporte de migración

### 1.3 ✅ Modelos Actualizados
- **Archivo**: `src/models/multi_org_models.py`
- **Nuevos modelos**:
  - `Organization`, `Environment`, `EnvironmentUrl`
  - `ApplicationComponent` (separado de `Application`)
  - Modelos de agregación y consulta actualizados

## 🚀 **FASE 2: MIGRACIÓN** (Pendiente)

### 2.1 🔄 Ejecutar Migración de Base de Datos
```bash
# 1. Verificar backup actual
python database_info.py all

# 2. Ejecutar migración (con confirmación)
python migrate_to_multi_org.py

# 3. Verificar resultado
python database_info.py all
```

**Resultados esperados**:
- Base de datos migrada con nuevas tablas
- Datos existentes preservados y migrados
- Backup disponible para rollback
- Reporte de migración generado

## 🔧 **FASE 3: ACTUALIZACIÓN DE CÓDIGO** (Pendiente)

### 3.1 🛠️ Actualizar Herramientas MCP
**Archivos a modificar**:
- `src/tools/deployment/deployment_tools.py`
- `src/tools/deployment/version_tools.py`
- `src/storage/database.py`

**Cambios requeridos**:
- Usar `environment_id` en lugar de `environment` string
- Añadir filtros por `organization_id`
- Implementar consultas para URLs por entorno
- Actualizar funciones CRUD

### 3.2 📊 Actualizar Frontend Streamlit
**Archivos a modificar**:
- `src/frontend/enhanced_dashboard.py`
- `src/frontend/dashboard_tools.py`

**Nuevas funcionalidades**:
- Selector de organización en sidebar
- Vista por entorno específico de cada organización
- Gestión de URLs por entorno/componente
- Dashboard comparativo entre organizaciones

### 3.3 📝 Actualizar Scripts de Datos
**Archivos a crear/modificar**:
- `scripts/generate_multi_org_data.py`
- Actualizar scripts existentes

**Datos a generar**:
- Aplicaciones para proeduca y villanueva
- Versiones diferentes por organización
- URLs de ejemplo para cada entorno
- Despliegues en entornos específicos

## 📚 **FASE 4: DOCUMENTACIÓN** (Pendiente)

### 4.1 📖 Actualizar Documentación
**Archivos a actualizar**:
- `docs/DATABASE.md`
- `docs/SQL_QUERIES.md`
- `README.md`

**Contenido nuevo**:
- Esquema multi-organización
- Consultas para organizaciones y entornos
- Ejemplos de uso de URLs por entorno

## 🎯 **COMANDOS DE EJECUCIÓN**

### Paso 1: Migración de Base de Datos
```bash
# Ejecutar migración completa
python migrate_to_multi_org.py

# Verificar resultado
python database_info.py all
```

### Paso 2: Probar Modelos Nuevos
```python
# Importar nuevos modelos
from src.models.multi_org_models import Organization, Environment, EnvironmentUrl

# Crear instancias de ejemplo
org = Organization(id="proeduca", name="proeduca", display_name="PROEDUCA")
env = Environment(id="proeduca-des", organization_id="proeduca", name="des", display_name="Desarrollo")
```

### Paso 3: Actualizar y Probar Herramientas
```bash
# Después de actualizar herramientas MCP
python -m src.mcp_server.main

# Probar dashboard actualizado
streamlit run src/frontend/enhanced_dashboard.py
```

## 📋 **ESTRUCTURA FINAL ESPERADA**

### Base de Datos
```
organizations (2 registros)
├── proeduca
└── villanueva

environments (6 registros)
├── proeduca-des, proeduca-pre, proeduca-test, proeduca-pro
└── villanueva-pre, villanueva-pro

environment_urls (variable)
├── URLs por componente/entorno
└── Tipos: main_app, version_api, health_check

applications (modificada)
├── organization_id añadido
└── Vinculadas a organización

deployments (modificada)
├── environment_id (en lugar de environment string)
└── Vinculados a entorno específico
```

### URLs de Ejemplo
```
proeduca-des:
  expedientes-frontend:
    - main_app: https://expedientes-des.proeduca.es
    - version_api: https://expedientes-des.proeduca.es/api/version
  expedientes-backend:
    - health_check: https://api-expedientes-des.proeduca.es/health
    - version_api: https://api-expedientes-des.proeduca.es/api/version

villanueva-pre:
  expedientes-frontend:
    - main_app: https://expedientes-pre.villanueva.es
    - version_api: https://expedientes-pre.villanueva.es/api/version
```

## 🔍 **VERIFICACIONES POST-MIGRACIÓN**

### 1. Integridad de Datos
```sql
-- Verificar que no hay registros huérfanos
SELECT COUNT(*) FROM deployments WHERE environment_id IS NULL;
SELECT COUNT(*) FROM applications WHERE organization_id IS NULL;
```

### 2. Funcionalidad de URLs
```python
# Probar consulta de URLs por entorno
from src.storage.database import get_environment_urls
urls = get_environment_urls("proeduca-des", "expedientes-frontend")
```

### 3. Dashboard Multi-Organización
```bash
# Verificar que el dashboard muestra ambas organizaciones
streamlit run src/frontend/enhanced_dashboard.py
```

## ⚠️ **CONSIDERACIONES IMPORTANTES**

1. **Backup Obligatorio**: La migración crea backup automático, pero verificar manualmente
2. **Rollback**: Si hay problemas, restaurar desde backup
3. **Testing**: Probar exhaustivamente antes de usar en producción
4. **URLs**: Las URLs de ejemplo son templates, ajustar según URLs reales
5. **Gradual**: Implementar cambios de forma gradual para minimizar riesgos

## 📞 **Siguiente Paso Recomendado**

**¿Quieres proceder con la migración de la base de datos?**

```bash
# Ejecutar este comando para iniciar:
python migrate_to_multi_org.py
```

La migración es **reversible** mediante el backup automático que se crea.