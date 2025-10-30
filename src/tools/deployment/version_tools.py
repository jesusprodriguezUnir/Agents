"""
Herramientas para gestión de versiones.

Proporciona funcionalidades para listar, comparar y gestionar
versiones de aplicaciones .NET Core + Angular.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from uuid import uuid4

from ...models.deployment import Version, Environment, GitCommit, ChangeLog
from ...utils.logging import get_logger
from ..registry import ToolRegistry


logger = get_logger(__name__)


# Base de datos simulada en memoria (en producción usar SQLite/PostgreSQL)
VERSIONS_DB: Dict[str, List[Version]] = {
    "dev": [],
    "pre": [],
    "prod": []
}


async def list_versions_by_environment(environment: str) -> str:
    """
    Lista todas las versiones desplegadas en un entorno específico.
    
    Args:
        environment: Entorno (dev, pre, prod)
        
    Returns:
        JSON con la lista de versiones
    """
    try:
        env = Environment(environment.lower())
        versions = VERSIONS_DB.get(env.value, [])
        
        # Ordenar por fecha de creación (más reciente primero)
        versions_sorted = sorted(versions, key=lambda v: v.created_at, reverse=True)
        
        result = {
            "environment": env.value,
            "total_versions": len(versions_sorted),
            "versions": [
                {
                    "version": v.version,
                    "branch": v.branch,
                    "commit_hash": v.commit_hash[:8],
                    "build_number": v.build_number,
                    "created_at": v.created_at.isoformat(),
                    "features_count": len(v.features),
                    "bug_fixes_count": len(v.bug_fixes),
                    "commits_count": len(v.commits)
                }
                for v in versions_sorted[:10]  # Últimas 10 versiones
            ]
        }
        
        logger.info("Listed versions", environment=env.value, count=len(versions_sorted))
        return json.dumps(result, indent=2)
        
    except ValueError as e:
        error_msg = f"Entorno inválido: {environment}. Use: dev, pre, prod"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})
    except Exception as e:
        error_msg = f"Error listando versiones: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})


async def get_version_details(environment: str, version: str) -> str:
    """
    Obtiene detalles completos de una versión específica.
    
    Args:
        environment: Entorno donde buscar
        version: Número de versión
        
    Returns:
        JSON con detalles de la versión
    """
    try:
        env = Environment(environment.lower())
        versions = VERSIONS_DB.get(env.value, [])
        
        # Buscar la versión específica
        version_obj = next((v for v in versions if v.version == version), None)
        
        if not version_obj:
            error_msg = f"Versión {version} no encontrada en {env.value}"
            return json.dumps({"error": error_msg})
        
        result = {
            "version": version_obj.version,
            "branch": version_obj.branch,
            "commit_hash": version_obj.commit_hash,
            "build_number": version_obj.build_number,
            "created_at": version_obj.created_at.isoformat(),
            "features": version_obj.features,
            "bug_fixes": version_obj.bug_fixes,
            "breaking_changes": version_obj.breaking_changes,
            "commits": [
                {
                    "hash": c.hash[:8],
                    "author": c.author,
                    "date": c.date.isoformat(),
                    "message": c.message,
                    "files_changed": len(c.files_changed)
                }
                for c in version_obj.commits
            ]
        }
        
        logger.info("Retrieved version details", environment=env.value, version=version)
        return json.dumps(result, indent=2)
        
    except ValueError as e:
        error_msg = f"Entorno inválido: {environment}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})
    except Exception as e:
        error_msg = f"Error obteniendo detalles: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})


async def compare_versions(environment: str, version1: str, version2: str) -> str:
    """
    Compara dos versiones y muestra las diferencias.
    
    Args:
        environment: Entorno donde buscar
        version1: Primera versión
        version2: Segunda versión
        
    Returns:
        JSON con comparación de versiones
    """
    try:
        env = Environment(environment.lower())
        versions = VERSIONS_DB.get(env.value, [])
        
        # Buscar ambas versiones
        v1 = next((v for v in versions if v.version == version1), None)
        v2 = next((v for v in versions if v.version == version2), None)
        
        if not v1:
            return json.dumps({"error": f"Versión {version1} no encontrada"})
        if not v2:
            return json.dumps({"error": f"Versión {version2} no encontrada"})
        
        # Generar changelog
        changelog = ChangeLog(
            from_version=version1,
            to_version=version2,
            commits=[],  # En producción, obtener del repositorio Git
            features=list(set(v2.features) - set(v1.features)),
            bug_fixes=list(set(v2.bug_fixes) - set(v1.bug_fixes)),
            breaking_changes=list(set(v2.breaking_changes) - set(v1.breaking_changes))
        )
        
        result = {
            "comparison": {
                "from_version": version1,
                "to_version": version2,
                "environment": env.value
            },
            "differences": {
                "new_features": changelog.features,
                "new_bug_fixes": changelog.bug_fixes,
                "new_breaking_changes": changelog.breaking_changes,
                "commits_difference": len(v2.commits) - len(v1.commits)
            },
            "version_details": {
                version1: {
                    "created_at": v1.created_at.isoformat(),
                    "commit_hash": v1.commit_hash[:8],
                    "branch": v1.branch
                },
                version2: {
                    "created_at": v2.created_at.isoformat(),
                    "commit_hash": v2.commit_hash[:8],
                    "branch": v2.branch
                }
            }
        }
        
        logger.info("Compared versions", environment=env.value, v1=version1, v2=version2)
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_msg = f"Error comparando versiones: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})


async def create_sample_version(environment: str, version: str, branch: str = "main") -> str:
    """
    Crea una versión de ejemplo para testing.
    
    Args:
        environment: Entorno donde crear
        version: Número de versión
        branch: Rama de Git
        
    Returns:
        JSON con resultado
    """
    try:
        env = Environment(environment.lower())
        
        # Crear commits de ejemplo
        sample_commits = [
            GitCommit(
                hash=f"a1b2c3d{i}",
                author="Desarrollador",
                email="dev@empresa.com",
                date=datetime.now() - timedelta(days=i),
                message=f"Feature: Implementar funcionalidad {i+1}",
                files_changed=[f"src/component{i}.ts", f"src/service{i}.cs"]
            )
            for i in range(3)
        ]
        
        # Crear nueva versión
        new_version = Version(
            version=version,
            branch=branch,
            commit_hash=f"abc123def456_{uuid4().hex[:8]}",
            build_number=f"build-{datetime.now().strftime('%Y%m%d-%H%M')}",
            commits=sample_commits,
            features=[
                f"Nueva funcionalidad de {version}",
                f"Mejora en la interfaz de usuario",
                f"Optimización de rendimiento"
            ],
            bug_fixes=[
                f"Corrección de bug crítico en {version}",
                f"Fix en validación de formularios"
            ],
            breaking_changes=[] if "patch" in version else [f"Cambio de API en {version}"]
        )
        
        # Agregar a la base de datos
        if env.value not in VERSIONS_DB:
            VERSIONS_DB[env.value] = []
        
        # Verificar que no existe ya
        existing = next((v for v in VERSIONS_DB[env.value] if v.version == version), None)
        if existing:
            return json.dumps({"error": f"Versión {version} ya existe en {env.value}"})
        
        VERSIONS_DB[env.value].append(new_version)
        
        result = {
            "message": f"Versión {version} creada exitosamente en {env.value}",
            "version": {
                "version": new_version.version,
                "branch": new_version.branch,
                "commit_hash": new_version.commit_hash[:8],
                "build_number": new_version.build_number,
                "features_count": len(new_version.features),
                "commits_count": len(new_version.commits)
            }
        }
        
        logger.info("Created sample version", environment=env.value, version=version)
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_msg = f"Error creando versión: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})


async def register_version_tools(registry: ToolRegistry) -> None:
    """
    Registra todas las herramientas de gestión de versiones.
    
    Args:
        registry: Registro de herramientas MCP
    """
    
    # Herramienta para listar versiones por entorno
    await registry.register_tool(
        name="list_versions",
        description="Lista todas las versiones desplegadas en un entorno específico",
        input_schema={
            "type": "object",
            "properties": {
                "environment": {
                    "type": "string",
                    "enum": ["dev", "pre", "prod"],
                    "description": "Entorno de despliegue"
                }
            },
            "required": ["environment"]
        },
        handler=list_versions_by_environment
    )
    
    # Herramienta para obtener detalles de versión
    await registry.register_tool(
        name="get_version_details",
        description="Obtiene información detallada de una versión específica",
        input_schema={
            "type": "object",
            "properties": {
                "environment": {
                    "type": "string",
                    "enum": ["dev", "pre", "prod"],
                    "description": "Entorno donde buscar"
                },
                "version": {
                    "type": "string",
                    "description": "Número de versión (ej: 1.2.3)"
                }
            },
            "required": ["environment", "version"]
        },
        handler=get_version_details
    )
    
    # Herramienta para comparar versiones
    await registry.register_tool(
        name="compare_versions",
        description="Compara dos versiones y muestra las diferencias",
        input_schema={
            "type": "object",
            "properties": {
                "environment": {
                    "type": "string",
                    "enum": ["dev", "pre", "prod"],
                    "description": "Entorno donde buscar"
                },
                "version1": {
                    "type": "string",
                    "description": "Primera versión a comparar"
                },
                "version2": {
                    "type": "string",
                    "description": "Segunda versión a comparar"
                }
            },
            "required": ["environment", "version1", "version2"]
        },
        handler=compare_versions
    )
    
    # Herramienta para crear versiones de ejemplo
    await registry.register_tool(
        name="create_sample_version",
        description="Crea una versión de ejemplo para testing del sistema",
        input_schema={
            "type": "object",
            "properties": {
                "environment": {
                    "type": "string",
                    "enum": ["dev", "pre", "prod"],
                    "description": "Entorno donde crear la versión"
                },
                "version": {
                    "type": "string",
                    "description": "Número de versión (ej: 1.2.3)"
                },
                "branch": {
                    "type": "string",
                    "description": "Rama de Git (opcional, default: main)"
                }
            },
            "required": ["environment", "version"]
        },
        handler=create_sample_version
    )
    
    logger.info("Version management tools registered successfully")