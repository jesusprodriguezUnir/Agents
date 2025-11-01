"""
Herramientas para gestión de despliegues multi-organización.

Proporciona funcionalidades para registrar, consultar y gestionar
despliegues en diferentes organizaciones y entornos.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from uuid import uuid4

from ...models.multi_org_models import Organization, Environment, EnvironmentUrl
from ...utils.logging import get_logger

logger = get_logger(__name__)

DATABASE_PATH = "data/deployments.db"


def get_db_connection():
    """Obtiene una conexión a la base de datos."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


async def register_deployment(
    organization_id: int,
    environment_id: int, 
    version: str, 
    deployed_by: str,
    notes: str = ""
) -> str:
    """
    Registra un nuevo despliegue en el sistema multi-organización.
    
    Args:
        organization_id: ID de la organización
        environment_id: ID del entorno
        version: Versión a desplegar
        deployed_by: Usuario que realiza el despliegue
        notes: Notas adicionales
        
    Returns:
        JSON con información del despliegue registrado
    """
    try:
        with get_db_connection() as conn:
            # Verificar que la organización existe
            org_result = conn.execute(
                "SELECT name FROM organizations WHERE id = ?", 
                (organization_id,)
            ).fetchone()
            
            if not org_result:
                return json.dumps({
                    "success": False,
                    "error": f"Organización con ID {organization_id} no encontrada"
                })
            
            # Verificar que el entorno existe
            env_result = conn.execute(
                "SELECT name FROM environments WHERE id = ? AND organization_id = ?", 
                (environment_id, organization_id)
            ).fetchone()
            
            if not env_result:
                return json.dumps({
                    "success": False,
                    "error": f"Entorno con ID {environment_id} no encontrado para la organización"
                })
            
            # Buscar la versión
            version_result = conn.execute(
                "SELECT id, application_id FROM versions WHERE version = ?", 
                (version,)
            ).fetchone()
            
            if not version_result:
                return json.dumps({
                    "success": False,
                    "error": f"Versión {version} no encontrada"
                })
            
            # Registrar el despliegue
            deployment_id = str(uuid4())
            deployment_date = datetime.now().isoformat()
            
            conn.execute("""
                INSERT INTO deployments (
                    id, environment_id, version_id, status, deployed_by, 
                    deployed_at, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                deployment_id,
                environment_id,
                version_result['id'],
                'success',  # Por defecto exitoso
                deployed_by,
                deployment_date,
                notes
            ))
            
            conn.commit()
            
            return json.dumps({
                "success": True,
                "deployment_id": deployment_id,
                "organization": org_result['name'],
                "environment": env_result['name'],
                "version": version,
                "deployed_by": deployed_by,
                "deployment_date": deployment_date,
                "notes": notes
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Error registrando despliegue: {e}")
        return json.dumps({
            "success": False,
            "error": f"Error interno: {str(e)}"
        })


async def get_deployments_by_organization(
    organization_id: int,
    limit: int = 50
) -> str:
    """
    Obtiene los despliegues de una organización específica.
    
    Args:
        organization_id: ID de la organización
        limit: Número máximo de despliegues a devolver
        
    Returns:
        JSON con los despliegues de la organización
    """
    try:
        with get_db_connection() as conn:
            # Verificar que la organización existe
            org_result = conn.execute(
                "SELECT name FROM organizations WHERE id = ?", 
                (organization_id,)
            ).fetchone()
            
            if not org_result:
                return json.dumps({
                    "success": False,
                    "error": f"Organización con ID {organization_id} no encontrada"
                })
            
            # Obtener despliegues
            deployments = conn.execute("""
                SELECT 
                    d.id,
                    d.status,
                    d.deployed_by,
                    d.deployed_at,
                    d.notes,
                    v.version,
                    v.release_date,
                    a.name as application_name,
                    e.name as environment_name,
                    o.name as organization_name
                FROM deployments d
                JOIN versions v ON d.version_id = v.id
                JOIN applications a ON v.application_id = a.id
                JOIN environments e ON d.environment_id = e.id
                JOIN organizations o ON e.organization_id = o.id
                WHERE o.id = ?
                ORDER BY d.deployed_at DESC
                LIMIT ?
            """, (organization_id, limit)).fetchall()
            
            deployment_list = []
            for row in deployments:
                deployment_list.append({
                    "id": row['id'],
                    "organization": row['organization_name'],
                    "environment": row['environment_name'],
                    "application": row['application_name'],
                    "version": row['version'],
                    "status": row['status'],
                    "deployed_by": row['deployed_by'],
                    "deployment_date": row['deployed_at'],
                    "release_date": row['release_date'],
                    "notes": row['notes']
                })
            
            return json.dumps({
                "success": True,
                "organization": org_result['name'],
                "deployments": deployment_list,
                "total": len(deployment_list)
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Error obteniendo despliegues: {e}")
        return json.dumps({
            "success": False,
            "error": f"Error interno: {str(e)}"
        })


async def get_environments_by_organization(organization_id: int) -> str:
    """
    Obtiene todos los entornos de una organización.
    
    Args:
        organization_id: ID de la organización
        
    Returns:
        JSON con los entornos de la organización
    """
    try:
        with get_db_connection() as conn:
            # Verificar que la organización existe
            org_result = conn.execute(
                "SELECT name FROM organizations WHERE id = ?", 
                (organization_id,)
            ).fetchone()
            
            if not org_result:
                return json.dumps({
                    "success": False,
                    "error": f"Organización con ID {organization_id} no encontrada"
                })
            
            # Obtener entornos
            environments = conn.execute("""
                SELECT 
                    e.id,
                    e.name,
                    e.description,
                    COUNT(DISTINCT d.id) as deployment_count,
                    MAX(d.deployed_at) as last_deployment
                FROM environments e
                LEFT JOIN deployments d ON e.id = d.environment_id
                WHERE e.organization_id = ?
                GROUP BY e.id, e.name, e.description
                ORDER BY e.name
            """, (organization_id,)).fetchall()
            
            environment_list = []
            for row in environments:
                environment_list.append({
                    "id": row['id'],
                    "name": row['name'],
                    "description": row['description'],
                    "deployment_count": row['deployment_count'],
                    "last_deployment": row['last_deployment']
                })
            
            return json.dumps({
                "success": True,
                "organization": org_result['name'],
                "environments": environment_list,
                "total": len(environment_list)
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Error obteniendo entornos: {e}")
        return json.dumps({
            "success": False,
            "error": f"Error interno: {str(e)}"
        })


async def get_organizations() -> str:
    """
    Obtiene todas las organizaciones disponibles.
    
    Returns:
        JSON con todas las organizaciones
    """
    try:
        with get_db_connection() as conn:
            organizations = conn.execute("""
                SELECT 
                    o.id,
                    o.name,
                    o.description,
                    COUNT(DISTINCT e.id) as environment_count,
                    COUNT(DISTINCT d.id) as deployment_count
                FROM organizations o
                LEFT JOIN environments e ON o.id = e.organization_id
                LEFT JOIN deployments d ON e.id = d.environment_id
                GROUP BY o.id, o.name, o.description
                ORDER BY o.name
            """).fetchall()
            
            organization_list = []
            for row in organizations:
                organization_list.append({
                    "id": row['id'],
                    "name": row['name'],
                    "description": row['description'],
                    "environment_count": row['environment_count'],
                    "deployment_count": row['deployment_count']
                })
            
            return json.dumps({
                "success": True,
                "organizations": organization_list,
                "total": len(organization_list)
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Error obteniendo organizaciones: {e}")
        return json.dumps({
            "success": False,
            "error": f"Error interno: {str(e)}"
        })


async def get_environment_urls(environment_id: int) -> str:
    """
    Obtiene las URLs de un entorno específico.
    
    Args:
        environment_id: ID del entorno
        
    Returns:
        JSON con las URLs del entorno
    """
    try:
        with get_db_connection() as conn:
            # Verificar que el entorno existe
            env_result = conn.execute("""
                SELECT e.name, o.name as org_name 
                FROM environments e 
                JOIN organizations o ON e.organization_id = o.id 
                WHERE e.id = ?
            """, (environment_id,)).fetchone()
            
            if not env_result:
                return json.dumps({
                    "success": False,
                    "error": f"Entorno con ID {environment_id} no encontrado"
                })
            
            # Obtener URLs
            urls = conn.execute("""
                SELECT 
                    eu.id,
                    eu.url,
                    eu.url_type,
                    ac.name as component_name,
                    a.name as application_name
                FROM environment_urls eu
                JOIN application_components ac ON eu.component_id = ac.id
                JOIN applications a ON ac.application_id = a.id
                WHERE eu.environment_id = ?
                ORDER BY a.name, ac.name
            """, (environment_id,)).fetchall()
            
            url_list = []
            for row in urls:
                url_list.append({
                    "id": row['id'],
                    "application": row['application_name'],
                    "component": row['component_name'],
                    "url": row['url'],
                    "type": row['url_type']
                })
            
            return json.dumps({
                "success": True,
                "organization": env_result['org_name'],
                "environment": env_result['name'],
                "urls": url_list,
                "total": len(url_list)
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Error obteniendo URLs: {e}")
        return json.dumps({
            "success": False,
            "error": f"Error interno: {str(e)}"
        })


# Las herramientas serán registradas por el servidor MCP
# cuando importe este módulo