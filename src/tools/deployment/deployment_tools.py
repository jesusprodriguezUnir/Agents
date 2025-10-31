"""
Herramientas para gestión de despliegues.

Proporciona funcionalidades para registrar, consultar y gestionar
despliegues en diferentes entornos.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from uuid import uuid4

from ...models.deployment import (
    Deployment, DeploymentStatus, Environment, Version, 
    DeploymentSummary, ApplicationEnvironmentStatus, EnvironmentOverview
)
from ...utils.logging import get_logger
from ..registry import ToolRegistry
from .version_tools import VERSIONS_DB


logger = get_logger(__name__)


# Base de datos de despliegues en memoria
DEPLOYMENTS_DB: List[Deployment] = []


async def register_deployment(
    environment: str, 
    version: str, 
    deployed_by: str,
    notes: str = ""
) -> str:
    """
    Registra un nuevo despliegue.
    
    Args:
        environment: Entorno de despliegue
        version: Versión a desplegar
        deployed_by: Usuario que realiza el despliegue
        notes: Notas adicionales
        
    Returns:
        JSON con información del despliegue registrado
    """
    try:
        env = Environment(environment.lower())
        
        # Buscar la versión en el entorno
        versions = VERSIONS_DB.get(env.value, [])
        version_obj = next((v for v in versions if v.version == version), None)
        
        if not version_obj:
            return json.dumps({
                "error": f"Versión {version} no encontrada en {env.value}. "
                        f"Use create_sample_version primero."
            })
        
        # Crear nuevo despliegue
        deployment = Deployment(
            id=str(uuid4()),
            environment=env,
            version=version_obj,
            status=DeploymentStatus.IN_PROGRESS,
            deployed_by=deployed_by,
            started_at=datetime.now(),
            notes=notes
        )
        
        DEPLOYMENTS_DB.append(deployment)
        
        result = {
            "deployment_id": deployment.id,
            "environment": env.value,
            "version": version,
            "status": deployment.status.value,
            "deployed_by": deployed_by,
            "started_at": deployment.started_at.isoformat(),
            "message": f"Despliegue iniciado exitosamente para {version} en {env.value}"
        }
        
        logger.info("Deployment registered", 
                   deployment_id=deployment.id, 
                   environment=env.value, 
                   version=version)
        
        return json.dumps(result, indent=2)
        
    except ValueError as e:
        error_msg = f"Entorno inválido: {environment}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})
    except Exception as e:
        error_msg = f"Error registrando despliegue: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})


async def update_deployment_status(deployment_id: str, status: str, notes: str = "") -> str:
    """
    Actualiza el estado de un despliegue.
    
    Args:
        deployment_id: ID del despliegue
        status: Nuevo estado (success, failed, rollback)
        notes: Notas adicionales
        
    Returns:
        JSON con resultado de la actualización
    """
    try:
        # Buscar el despliegue
        deployment = next((d for d in DEPLOYMENTS_DB if d.id == deployment_id), None)
        
        if not deployment:
            return json.dumps({"error": f"Despliegue {deployment_id} no encontrado"})
        
        # Validar estado
        try:
            new_status = DeploymentStatus(status.lower())
        except ValueError:
            return json.dumps({
                "error": f"Estado inválido: {status}. "
                        f"Use: {', '.join([s.value for s in DeploymentStatus])}"
            })
        
        # Actualizar estado
        old_status = deployment.status
        deployment.status = new_status
        deployment.notes = f"{deployment.notes}\n{notes}".strip()
        
        if new_status in [DeploymentStatus.SUCCESS, DeploymentStatus.FAILED]:
            deployment.completed_at = datetime.now()
        
        result = {
            "deployment_id": deployment_id,
            "environment": deployment.environment.value,
            "version": deployment.version.version,
            "old_status": old_status.value,
            "new_status": new_status.value,
            "updated_at": datetime.now().isoformat(),
            "message": f"Estado actualizado de {old_status.value} a {new_status.value}"
        }
        
        logger.info("Deployment status updated", 
                   deployment_id=deployment_id,
                   old_status=old_status.value,
                   new_status=new_status.value)
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_msg = f"Error actualizando estado: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})


async def get_deployment_history(environment: str = None, limit: int = 10) -> str:
    """
    Obtiene el historial de despliegues.
    
    Args:
        environment: Filtrar por entorno (opcional)
        limit: Número máximo de despliegues a retornar
        
    Returns:
        JSON con historial de despliegues
    """
    try:
        deployments = DEPLOYMENTS_DB.copy()
        
        # Filtrar por entorno si se especifica
        if environment:
            env = Environment(environment.lower())
            deployments = [d for d in deployments if d.environment == env]
        
        # Ordenar por fecha (más reciente primero)
        deployments_sorted = sorted(deployments, key=lambda d: d.deployed_at, reverse=True)
        
        # Limitar resultados
        deployments_limited = deployments_sorted[:limit]
        
        result = {
            "total_deployments": len(deployments_sorted),
            "showing": len(deployments_limited),
            "filter": {"environment": environment} if environment else None,
            "deployments": [
                {
                    "deployment_id": d.id,
                    "environment": d.environment.value,
                    "version": d.version.version,
                    "status": d.status.value,
                    "deployed_by": d.deployed_by,
                    "deployed_at": d.deployed_at.isoformat(),
                    "completed_at": d.completed_at.isoformat() if d.completed_at else None,
                    "duration_minutes": (
                        (d.completed_at - d.started_at).total_seconds() / 60
                        if d.completed_at and d.started_at else None
                    ),
                    "notes": d.notes or "Sin notas"
                }
                for d in deployments_limited
            ]
        }
        
        logger.info("Retrieved deployment history", 
                   environment=environment, 
                   count=len(deployments_limited))
        
        return json.dumps(result, indent=2)
        
    except ValueError as e:
        error_msg = f"Entorno inválido: {environment}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})
    except Exception as e:
        error_msg = f"Error obteniendo historial: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})


async def get_environment_status(environment: str) -> str:
    """
    Obtiene el estado actual de un entorno.
    
    Args:
        environment: Entorno a consultar
        
    Returns:
        JSON con estado del entorno
    """
    try:
        env = Environment(environment.lower())
        
        # Obtener despliegues del entorno
        env_deployments = [d for d in DEPLOYMENTS_DB if d.environment == env]
        
        # Despliegue más reciente
        current_deployment = None
        if env_deployments:
            env_deployments_sorted = sorted(env_deployments, key=lambda d: d.deployed_at, reverse=True)
            current_deployment = env_deployments_sorted[0]
        
        # Calcular métricas
        successful_deployments = len([d for d in env_deployments if d.status == DeploymentStatus.SUCCESS])
        total_deployments = len(env_deployments)
        success_rate = (successful_deployments / total_deployments * 100) if total_deployments > 0 else 0
        
        result = {
            "environment": env.value,
            "current_deployment": {
                "deployment_id": current_deployment.id,
                "version": current_deployment.version.version,
                "status": current_deployment.status.value,
                "deployed_by": current_deployment.deployed_by,
                "deployed_at": current_deployment.deployed_at.isoformat(),
                "duration_minutes": (
                    (current_deployment.completed_at - current_deployment.started_at).total_seconds() / 60
                    if current_deployment.completed_at and current_deployment.started_at else None
                )
            } if current_deployment else None,
            "metrics": {
                "total_deployments": total_deployments,
                "successful_deployments": successful_deployments,
                "success_rate_percentage": round(success_rate, 2),
                "health_status": "healthy" if success_rate >= 80 else "warning" if success_rate >= 60 else "critical"
            },
            "recent_activity": [
                {
                    "deployment_id": d.id,
                    "version": d.version.version,
                    "status": d.status.value,
                    "deployed_at": d.deployed_at.isoformat()
                }
                for d in sorted(env_deployments, key=lambda d: d.deployed_at, reverse=True)[:5]
            ]
        }
        
        logger.info("Retrieved environment status", environment=env.value)
        return json.dumps(result, indent=2)
        
    except ValueError as e:
        error_msg = f"Entorno inválido: {environment}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})
    except Exception as e:
        error_msg = f"Error obteniendo estado del entorno: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})


async def register_deployment_tools(registry: ToolRegistry) -> None:
    """
    Registra todas las herramientas de gestión de despliegues.
    
    Args:
        registry: Registro de herramientas MCP
    """
    
    # Herramienta para registrar despliegue
    await registry.register_tool(
        name="register_deployment",
        description="Registra un nuevo despliegue en un entorno específico",
        input_schema={
            "type": "object",
            "properties": {
                "environment": {
                    "type": "string",
                    "enum": ["dev", "pre", "prod"],
                    "description": "Entorno de despliegue"
                },
                "version": {
                    "type": "string",
                    "description": "Versión a desplegar"
                },
                "deployed_by": {
                    "type": "string",
                    "description": "Usuario que realiza el despliegue"
                },
                "notes": {
                    "type": "string",
                    "description": "Notas adicionales del despliegue"
                }
            },
            "required": ["environment", "version", "deployed_by"]
        },
        handler=register_deployment
    )
    
    # Herramienta para actualizar estado de despliegue
    await registry.register_tool(
        name="update_deployment_status",
        description="Actualiza el estado de un despliegue existente",
        input_schema={
            "type": "object",
            "properties": {
                "deployment_id": {
                    "type": "string",
                    "description": "ID del despliegue a actualizar"
                },
                "status": {
                    "type": "string",
                    "enum": ["pending", "in_progress", "success", "failed", "rollback"],
                    "description": "Nuevo estado del despliegue"
                },
                "notes": {
                    "type": "string",
                    "description": "Notas adicionales"
                }
            },
            "required": ["deployment_id", "status"]
        },
        handler=update_deployment_status
    )
    
    # Herramienta para obtener historial
    await registry.register_tool(
        name="get_deployment_history",
        description="Obtiene el historial de despliegues con filtros opcionales",
        input_schema={
            "type": "object",
            "properties": {
                "environment": {
                    "type": "string",
                    "enum": ["dev", "pre", "prod"],
                    "description": "Filtrar por entorno (opcional)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Número máximo de resultados (default: 10)"
                }
            },
            "required": []
        },
        handler=get_deployment_history
    )
    
    # Herramienta para estado del entorno
    await registry.register_tool(
        name="get_environment_status",
        description="Obtiene el estado actual y métricas de un entorno",
        input_schema={
            "type": "object",
            "properties": {
                "environment": {
                    "type": "string",
                    "enum": ["dev", "pre", "prod"],
                    "description": "Entorno a consultar"
                }
            },
            "required": ["environment"]
        },
        handler=get_environment_status
    )
    
    logger.info("Deployment management tools registered successfully")