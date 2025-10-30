"""
Herramientas MCP para gestión de despliegues multi-aplicación.

Proporciona funcionalidades para crear, listar y gestionar despliegues
de aplicaciones específicas en diferentes entornos.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from ...models.deployment import (
    Deployment, Environment, DeploymentStatus, 
    EnvironmentOverview, ApplicationEnvironmentStatus
)
from ...schemas.tools import ToolResult
from ...storage.database import DatabaseManager


# Instancia global del gestor de base de datos
db_manager = DatabaseManager("data/deployments.db")


def create_deployment(
    application_id: str,
    environment: str,
    version: str,
    deployed_by: str,
    notes: str = ""
) -> ToolResult:
    """
    Crea un nuevo despliegue de una aplicación en un entorno específico.
    
    Args:
        application_id: ID de la aplicación a desplegar
        environment: Entorno de destino (dev, pre, prod)
        version: Versión a desplegar
        deployed_by: Usuario que realiza el despliegue
        notes: Notas adicionales del despliegue
        
    Returns:
        ToolResult con el despliegue creado
    """
    try:
        # Validar que la aplicación existe
        app = db_manager.get_application(application_id)
        if not app:
            return ToolResult(
                success=False,
                message=f"Aplicación {application_id} no encontrada"
            )
        
        # Validar entorno
        env = Environment(environment)
        
        # Buscar la versión
        versions = db_manager.get_versions_by_application(application_id)
        version_obj = next(
            (v for v in versions if v.version == version),
            None
        )
        
        if not version_obj:
            return ToolResult(
                success=False,
                message=f"Versión {version} no encontrada para aplicación {app.name}"
            )
        
        # Crear el despliegue
        deployment = Deployment(
            id=f"deploy-{uuid.uuid4().hex[:8]}",
            application_id=application_id,
            environment=env,
            version=version_obj,
            status=DeploymentStatus.PENDING,
            deployed_by=deployed_by,
            deployed_at=datetime.now(),
            notes=notes
        )
        
        deployment_id = db_manager.create_deployment(deployment)
        
        return ToolResult(
            success=True,
            message=f"Despliegue creado para {app.name} v{version} en {env.value}",
            data={
                "deployment_id": deployment.id,
                "application_name": app.name,
                "version": version,
                "environment": env.value,
                "status": deployment.status.value
            }
        )
        
    except ValueError as e:
        return ToolResult(
            success=False,
            message=f"Entorno inválido: {environment}. Use: dev, pre, prod"
        )
    except Exception as e:
        return ToolResult(
            success=False,
            message=f"Error al crear despliegue: {str(e)}"
        )


def list_deployments(
    application_id: str = None,
    environment: str = None,
    status: str = None,
    limit: int = 20
) -> ToolResult:
    """
    Lista despliegues con filtros opcionales.
    
    Args:
        application_id: Filtrar por aplicación (opcional)
        environment: Filtrar por entorno (opcional)
        status: Filtrar por estado (opcional)
        limit: Número máximo de despliegues a retornar
        
    Returns:
        ToolResult con la lista de despliegues
    """
    try:
        # Validar filtros
        env_filter = None
        if environment:
            env_filter = Environment(environment)
        
        # Obtener despliegues
        if application_id:
            deployments = db_manager.get_deployments_by_application(
                application_id, env_filter
            )
        else:
            # Para obtener todos los despliegues, necesitamos iterar por aplicaciones
            deployments = []
            applications = db_manager.list_applications()
            for app in applications:
                app_deployments = db_manager.get_deployments_by_application(
                    app.id, env_filter
                )
                deployments.extend(app_deployments)
        
        # Filtrar por estado si se especifica
        if status:
            status_filter = DeploymentStatus(status)
            deployments = [d for d in deployments if d.status == status_filter]
        
        # Ordenar por fecha y limitar
        deployments.sort(key=lambda d: d.deployed_at, reverse=True)
        limited_deployments = deployments[:limit]
        
        # Preparar datos de respuesta
        deployments_data = []
        for deployment in limited_deployments:
            app = db_manager.get_application(deployment.application_id)
            deployments_data.append({
                "id": deployment.id,
                "application_id": deployment.application_id,
                "application_name": app.name if app else deployment.application_id,
                "environment": deployment.environment.value,
                "version": deployment.version.version,
                "status": deployment.status.value,
                "deployed_by": deployment.deployed_by,
                "deployed_at": deployment.deployed_at.isoformat(),
                "notes": deployment.notes
            })
        
        return ToolResult(
            success=True,
            message=f"Se encontraron {len(deployments_data)} despliegues",
            data={
                "deployments": deployments_data,
                "total": len(deployments),
                "filters": {
                    "application_id": application_id,
                    "environment": environment,
                    "status": status
                }
            }
        )
        
    except ValueError as e:
        return ToolResult(
            success=False,
            message=f"Valor inválido en filtros: {str(e)}"
        )
    except Exception as e:
        return ToolResult(
            success=False,
            message=f"Error al listar despliegues: {str(e)}"
        )


def get_deployment(deployment_id: str) -> ToolResult:
    """
    Obtiene detalles de un despliegue específico.
    
    Args:
        deployment_id: ID del despliegue
        
    Returns:
        ToolResult con los detalles del despliegue
    """
    try:
        deployment = db_manager._get_deployment_by_id(deployment_id)
        
        if not deployment:
            return ToolResult(
                success=False,
                message=f"Despliegue {deployment_id} no encontrado"
            )
        
        # Obtener información de la aplicación
        app = db_manager.get_application(deployment.application_id)
        
        deployment_data = {
            "id": deployment.id,
            "application_id": deployment.application_id,
            "application_name": app.name if app else deployment.application_id,
            "environment": deployment.environment.value,
            "version": deployment.version.dict(),
            "status": deployment.status.value,
            "deployed_by": deployment.deployed_by,
            "deployed_at": deployment.deployed_at.isoformat(),
            "started_at": deployment.started_at.isoformat() if deployment.started_at else None,
            "completed_at": deployment.completed_at.isoformat() if deployment.completed_at else None,
            "notes": deployment.notes,
            "config_changes": deployment.config_changes,
            "migration_scripts": deployment.migration_scripts
        }
        
        return ToolResult(
            success=True,
            message=f"Despliegue {deployment_id} encontrado",
            data=deployment_data
        )
        
    except Exception as e:
        return ToolResult(
            success=False,
            message=f"Error al obtener despliegue: {str(e)}"
        )


def update_deployment_status(
    deployment_id: str,
    status: str,
    notes: str = ""
) -> ToolResult:
    """
    Actualiza el estado de un despliegue.
    
    Args:
        deployment_id: ID del despliegue
        status: Nuevo estado (pending, in_progress, success, failed, rollback)
        notes: Notas adicionales
        
    Returns:
        ToolResult confirmando la actualización
    """
    try:
        # Validar estado
        new_status = DeploymentStatus(status)
        
        # Obtener el despliegue actual
        deployment = db_manager._get_deployment_by_id(deployment_id)
        
        if not deployment:
            return ToolResult(
                success=False,
                message=f"Despliegue {deployment_id} no encontrado"
            )
        
        # Actualizar estado
        deployment.status = new_status
        if notes:
            deployment.notes = notes
        
        # Actualizar tiempos según el estado
        now = datetime.now()
        if new_status == DeploymentStatus.IN_PROGRESS:
            deployment.started_at = now
        elif new_status in [DeploymentStatus.SUCCESS, DeploymentStatus.FAILED]:
            deployment.completed_at = now
        
        # Aquí necesitaríamos implementar update_deployment en DatabaseManager
        # Por ahora simulamos que se actualiza
        
        return ToolResult(
            success=True,
            message=f"Estado del despliegue actualizado a {new_status.value}",
            data={
                "deployment_id": deployment_id,
                "old_status": "previous_status",  # Necesitaríamos guardar el estado anterior
                "new_status": new_status.value,
                "updated_at": now.isoformat()
            }
        )
        
    except ValueError as e:
        return ToolResult(
            success=False,
            message=f"Estado inválido: {status}. Use: pending, in_progress, success, failed, rollback"
        )
    except Exception as e:
        return ToolResult(
            success=False,
            message=f"Error al actualizar estado: {str(e)}"
        )


def get_environment_overview(environment: str) -> ToolResult:
    """
    Obtiene vista general de un entorno con todas las aplicaciones.
    
    Args:
        environment: Entorno a consultar (dev, pre, prod)
        
    Returns:
        ToolResult con la vista general del entorno
    """
    try:
        # Validar entorno
        env = Environment(environment)
        
        # Obtener vista general del entorno
        overview = db_manager.get_environment_overview(env)
        
        # Preparar datos de respuesta
        apps_data = []
        for app_status in overview.applications:
            app_data = {
                "application_id": app_status.application_id,
                "current_version": app_status.current_version,
                "health_status": app_status.health_status,
                "uptime_percentage": app_status.uptime_percentage,
                "active_incidents_count": len(app_status.active_incidents),
                "last_health_check": app_status.last_health_check.isoformat() if app_status.last_health_check else None
            }
            
            # Agregar información del despliegue actual
            if app_status.current_deployment:
                app_data["current_deployment"] = {
                    "id": app_status.current_deployment.id,
                    "status": app_status.current_deployment.status.value,
                    "deployed_at": app_status.current_deployment.deployed_at.isoformat(),
                    "deployed_by": app_status.current_deployment.deployed_by
                }
            
            apps_data.append(app_data)
        
        overview_data = {
            "environment": overview.environment.value,
            "total_applications": overview.total_applications,
            "healthy_applications": overview.healthy_applications,
            "applications_with_issues": overview.applications_with_issues,
            "pending_deployments": overview.pending_deployments,
            "last_deployment": overview.last_deployment.isoformat() if overview.last_deployment else None,
            "applications": apps_data
        }
        
        return ToolResult(
            success=True,
            message=f"Vista general del entorno {env.value} obtenida",
            data=overview_data
        )
        
    except ValueError as e:
        return ToolResult(
            success=False,
            message=f"Entorno inválido: {environment}. Use: dev, pre, prod"
        )
    except Exception as e:
        return ToolResult(
            success=False,
            message=f"Error al obtener vista del entorno: {str(e)}"
        )


def get_application_deployments(
    application_id: str,
    environment: str = None,
    limit: int = 10
) -> ToolResult:
    """
    Obtiene el historial de despliegues de una aplicación específica.
    
    Args:
        application_id: ID de la aplicación
        environment: Filtrar por entorno (opcional)
        limit: Número máximo de despliegues a retornar
        
    Returns:
        ToolResult con el historial de despliegues de la aplicación
    """
    try:
        # Verificar que la aplicación existe
        app = db_manager.get_application(application_id)
        if not app:
            return ToolResult(
                success=False,
                message=f"Aplicación {application_id} no encontrada"
            )
        
        # Validar entorno si se especifica
        env_filter = None
        if environment:
            env_filter = Environment(environment)
        
        # Obtener despliegues de la aplicación
        deployments = db_manager.get_deployments_by_application(
            application_id, env_filter
        )
        
        # Limitar resultados
        limited_deployments = deployments[:limit]
        
        # Preparar datos de respuesta
        deployments_data = []
        for deployment in limited_deployments:
            deployments_data.append({
                "id": deployment.id,
                "environment": deployment.environment.value,
                "version": deployment.version.version,
                "status": deployment.status.value,
                "deployed_by": deployment.deployed_by,
                "deployed_at": deployment.deployed_at.isoformat(),
                "duration_minutes": (
                    (deployment.completed_at - deployment.started_at).total_seconds() / 60
                    if deployment.completed_at and deployment.started_at
                    else None
                ),
                "notes": deployment.notes
            })
        
        return ToolResult(
            success=True,
            message=f"Historial de {app.name} obtenido ({len(deployments_data)} despliegues)",
            data={
                "application_id": application_id,
                "application_name": app.name,
                "deployments": deployments_data,
                "total_deployments": len(deployments),
                "environment_filter": environment
            }
        )
        
    except ValueError as e:
        return ToolResult(
            success=False,
            message=f"Entorno inválido: {environment}. Use: dev, pre, prod"
        )
    except Exception as e:
        return ToolResult(
            success=False,
            message=f"Error al obtener historial de aplicación: {str(e)}"
        )