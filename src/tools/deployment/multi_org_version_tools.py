"""
Herramientas para gestión de versiones multi-organización.

Proporciona funcionalidades para crear y gestionar versiones
en el contexto de múltiples organizaciones.
"""

import json
import sqlite3
from datetime import datetime
from uuid import uuid4

from ...models.multi_org_models import Organization, Environment, EnvironmentUrl
from ...utils.logging import get_logger
from ..registry import ToolRegistry

logger = get_logger(__name__)

DATABASE_PATH = "data/deployments.db"


def get_db_connection():
    """Obtiene una conexión a la base de datos."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


async def create_version(
    application_id: int,
    version: str,
    release_date: str,
    release_notes: str = ""
) -> str:
    """
    Crea una nueva versión de una aplicación.
    
    Args:
        application_id: ID de la aplicación
        version: Nombre de la versión (ej: 1.2.3)
        release_date: Fecha de release (ISO format)
        release_notes: Notas de la versión
        
    Returns:
        JSON con información de la versión creada
    """
    try:
        with get_db_connection() as conn:
            # Verificar que la aplicación existe
            app_result = conn.execute(
                "SELECT name FROM applications WHERE id = ?", 
                (application_id,)
            ).fetchone()
            
            if not app_result:
                return json.dumps({
                    "success": False,
                    "error": f"Aplicación con ID {application_id} no encontrada"
                })
            
            # Verificar que la versión no existe ya
            existing_version = conn.execute(
                "SELECT id FROM versions WHERE application_id = ? AND version = ?", 
                (application_id, version)
            ).fetchone()
            
            if existing_version:
                return json.dumps({
                    "success": False,
                    "error": f"La versión {version} ya existe para esta aplicación"
                })
            
            # Crear la versión
            version_id = str(uuid4())
            created_date = datetime.now().isoformat()
            
            conn.execute("""
                INSERT INTO versions (
                    id, application_id, version, release_date, 
                    release_notes, created_date
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                version_id,
                application_id,
                version,
                release_date,
                release_notes,
                created_date
            ))
            
            conn.commit()
            
            return json.dumps({
                "success": True,
                "version_id": version_id,
                "application": app_result['name'],
                "version": version,
                "release_date": release_date,
                "release_notes": release_notes,
                "created_date": created_date
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Error creando versión: {e}")
        return json.dumps({
            "success": False,
            "error": f"Error interno: {str(e)}"
        })


async def get_versions_by_application(application_id: int) -> str:
    """
    Obtiene todas las versiones de una aplicación.
    
    Args:
        application_id: ID de la aplicación
        
    Returns:
        JSON con las versiones de la aplicación
    """
    try:
        with get_db_connection() as conn:
            # Verificar que la aplicación existe
            app_result = conn.execute(
                "SELECT name FROM applications WHERE id = ?", 
                (application_id,)
            ).fetchone()
            
            if not app_result:
                return json.dumps({
                    "success": False,
                    "error": f"Aplicación con ID {application_id} no encontrada"
                })
            
            # Obtener versiones
            versions = conn.execute("""
                SELECT 
                    v.id,
                    v.version,
                    v.release_date,
                    v.release_notes,
                    v.created_date,
                    COUNT(d.id) as deployment_count
                FROM versions v
                LEFT JOIN deployments d ON v.id = d.version_id
                WHERE v.application_id = ?
                GROUP BY v.id, v.version, v.release_date, v.release_notes, v.created_date
                ORDER BY v.release_date DESC
            """, (application_id,)).fetchall()
            
            version_list = []
            for row in versions:
                version_list.append({
                    "id": row['id'],
                    "version": row['version'],
                    "release_date": row['release_date'],
                    "release_notes": row['release_notes'],
                    "created_date": row['created_date'],
                    "deployment_count": row['deployment_count']
                })
            
            return json.dumps({
                "success": True,
                "application": app_result['name'],
                "versions": version_list,
                "total": len(version_list)
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Error obteniendo versiones: {e}")
        return json.dumps({
            "success": False,
            "error": f"Error interno: {str(e)}"
        })


async def get_applications() -> str:
    """
    Obtiene todas las aplicaciones disponibles.
    
    Returns:
        JSON con todas las aplicaciones
    """
    try:
        with get_db_connection() as conn:
            applications = conn.execute("""
                SELECT 
                    a.id,
                    a.name,
                    a.description,
                    COUNT(DISTINCT v.id) as version_count,
                    COUNT(DISTINCT d.id) as deployment_count,
                    MAX(v.created_at) as latest_version_date
                FROM applications a
                LEFT JOIN application_components ac ON a.id = ac.application_id
                LEFT JOIN versions v ON ac.id = v.component_id
                LEFT JOIN deployments d ON v.id = d.version_id
                GROUP BY a.id, a.name, a.description
                ORDER BY a.name
            """).fetchall()
            
            application_list = []
            for row in applications:
                application_list.append({
                    "id": row['id'],
                    "name": row['name'],
                    "description": row['description'],
                    "version_count": row['version_count'],
                    "deployment_count": row['deployment_count'],
                    "latest_version_date": row['latest_version_date']
                })
            
            return json.dumps({
                "success": True,
                "applications": application_list,
                "total": len(application_list)
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Error obteniendo aplicaciones: {e}")
        return json.dumps({
            "success": False,
            "error": f"Error interno: {str(e)}"
        })


async def get_deployment_history_by_version(version_id: str) -> str:
    """
    Obtiene el historial de despliegues de una versión específica.
    
    Args:
        version_id: ID de la versión
        
    Returns:
        JSON con el historial de despliegues
    """
    try:
        with get_db_connection() as conn:
            # Verificar que la versión existe
            version_result = conn.execute("""
                SELECT v.version, a.name as app_name 
                FROM versions v 
                JOIN applications a ON v.application_id = a.id 
                WHERE v.id = ?
            """, (version_id,)).fetchone()
            
            if not version_result:
                return json.dumps({
                    "success": False,
                    "error": f"Versión con ID {version_id} no encontrada"
                })
            
            # Obtener historial de despliegues
            deployments = conn.execute("""
                SELECT 
                    d.id,
                    d.status,
                    d.deployed_by,
                    d.deployed_at,
                    d.notes,
                    e.name as environment_name,
                    o.name as organization_name
                FROM deployments d
                JOIN environments e ON d.environment_id = e.id
                JOIN organizations o ON e.organization_id = o.id
                WHERE d.version_id = ?
                ORDER BY d.deployed_at DESC
            """, (version_id,)).fetchall()
            
            deployment_list = []
            for row in deployments:
                deployment_list.append({
                    "id": row['id'],
                    "organization": row['organization_name'],
                    "environment": row['environment_name'],
                    "status": row['status'],
                    "deployed_by": row['deployed_by'],
                    "deployment_date": row['deployed_at'],
                    "notes": row['notes']
                })
            
            return json.dumps({
                "success": True,
                "application": version_result['app_name'],
                "version": version_result['version'],
                "deployments": deployment_list,
                "total": len(deployment_list)
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Error obteniendo historial de despliegues: {e}")
        return json.dumps({
            "success": False,
            "error": f"Error interno: {str(e)}"
        })


async def get_latest_versions_by_environment(organization_id: int, environment_id: int) -> str:
    """
    Obtiene las últimas versiones desplegadas en un entorno específico.
    
    Args:
        organization_id: ID de la organización
        environment_id: ID del entorno
        
    Returns:
        JSON con las últimas versiones desplegadas
    """
    try:
        with get_db_connection() as conn:
            # Verificar que el entorno existe en la organización
            env_result = conn.execute("""
                SELECT e.name, o.name as org_name 
                FROM environments e 
                JOIN organizations o ON e.organization_id = o.id 
                WHERE e.id = ? AND o.id = ?
            """, (environment_id, organization_id)).fetchone()
            
            if not env_result:
                return json.dumps({
                    "success": False,
                    "error": f"Entorno con ID {environment_id} no encontrado en la organización {organization_id}"
                })
            
            # Obtener últimas versiones desplegadas
            latest_deployments = conn.execute("""
                WITH latest_deployments AS (
                    SELECT 
                        d.version_id,
                        a.id as application_id,
                        a.name as application_name,
                        v.version,
                        d.status,
                        d.deployed_by,
                        d.deployed_at,
                        d.notes,
                        ROW_NUMBER() OVER (PARTITION BY a.id ORDER BY d.deployed_at DESC) as rn
                    FROM deployments d
                    JOIN versions v ON d.version_id = v.id
                    JOIN applications a ON v.application_id = a.id
                    WHERE d.environment_id = ?
                )
                SELECT * FROM latest_deployments WHERE rn = 1
                ORDER BY application_name
            """, (environment_id,)).fetchall()
            
            deployment_list = []
            for row in latest_deployments:
                deployment_list.append({
                    "application_id": row['application_id'],
                    "application": row['application_name'],
                    "version": row['version'],
                    "status": row['status'],
                    "deployed_by": row['deployed_by'],
                    "deployment_date": row['deployed_at'],
                    "notes": row['notes']
                })
            
            return json.dumps({
                "success": True,
                "organization": env_result['org_name'],
                "environment": env_result['name'],
                "latest_deployments": deployment_list,
                "total": len(deployment_list)
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Error obteniendo últimas versiones: {e}")
        return json.dumps({
            "success": False,
            "error": f"Error interno: {str(e)}"
        })


# Las herramientas serán registradas por el servidor MCP
# cuando importe este módulo