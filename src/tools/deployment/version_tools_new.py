"""
Herramientas MCP para gestión de versiones en el sistema de despliegues multi-aplicación.

Proporciona funcionalidades para crear, listar y comparar versiones
de aplicaciones específicas en diferentes entornos.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from ...models.deployment import Version, GitCommit, ChangeLog, Application
from ...schemas.tools import ToolResult
from ...storage.database import DatabaseManager


# Instancia global del gestor de base de datos
db_manager = DatabaseManager("data/deployments.db")


def create_application(
    app_id: str,
    name: str,
    app_type: str,
    description: str = "",
    repository_url: str = "",
    tech_stack: Optional[List[str]] = None,
    owner_team: str = "",
    dependencies: Optional[List[str]] = None,
    health_check_url: str = ""
) -> ToolResult:
    """
    Crea una nueva aplicación en el sistema.
    
    Args:
        app_id: ID único de la aplicación
        name: Nombre de la aplicación
        app_type: Tipo de aplicación (frontend, backend, microservice, etc.)
        description: Descripción de la aplicación
        repository_url: URL del repositorio Git
        tech_stack: Stack tecnológico
        owner_team: Equipo responsable
        dependencies: IDs de aplicaciones dependientes
        health_check_url: URL de health check
        
    Returns:
        ToolResult con la aplicación creada
    """
    try:
        from ...models.deployment import ApplicationType
        
        # Validar tipo de aplicación
        app_type_enum = ApplicationType(app_type)
        
        application = Application(
            id=app_id,
            name=name,
            type=app_type_enum,
            description=description,
            repository_url=repository_url,
            tech_stack=tech_stack or [],
            owner_team=owner_team,
            dependencies=dependencies or [],
            health_check_url=health_check_url,
            created_at=datetime.now()
        )
        
        created_id = db_manager.create_application(application)
        
        return ToolResult(
            success=True,
            message=f"Aplicación '{name}' creada exitosamente",
            data=application.dict(),
            error_code=None,
            metadata=None
        )
        
    except Exception as e:
        return ToolResult(
            success=False,
            message=f"Error al crear aplicación: {str(e)}",
            data=None,
            error_code="APPLICATION_CREATION_ERROR",
            metadata=None
        )


def list_applications() -> ToolResult:
    """
    Lista todas las aplicaciones registradas.
    
    Returns:
        ToolResult con la lista de aplicaciones
    """
    try:
        applications = db_manager.list_applications()
        
        return ToolResult(
            success=True,
            message=f"Se encontraron {len(applications)} aplicaciones",
            data={
                "applications": [app.dict() for app in applications],
                "total": len(applications)
            }
        )
        
    except Exception as e:
        return ToolResult(
            success=False,
            message=f"Error al listar aplicaciones: {str(e)}"
        )


def get_application(app_id: str) -> ToolResult:
    """
    Obtiene los detalles de una aplicación específica.
    
    Args:
        app_id: ID de la aplicación
        
    Returns:
        ToolResult con los detalles de la aplicación
    """
    try:
        application = db_manager.get_application(app_id)
        
        if not application:
            return ToolResult(
                success=False,
                message=f"Aplicación {app_id} no encontrada"
            )
        
        return ToolResult(
            success=True,
            message=f"Aplicación {app_id} encontrada",
            data=application.dict()
        )
        
    except Exception as e:
        return ToolResult(
            success=False,
            message=f"Error al obtener aplicación: {str(e)}"
        )


def create_version(
    application_id: str,
    version: str,
    branch: str,
    commit_hash: str,
    build_number: str,
    features: List[str] = None,
    bug_fixes: List[str] = None,
    breaking_changes: List[str] = None,
    artifacts: Dict[str, str] = None
) -> ToolResult:
    """
    Crea una nueva versión para una aplicación específica.
    
    Args:
        application_id: ID de la aplicación
        version: Número de versión (ej: 2.1.0)
        branch: Rama de Git de la versión
        commit_hash: Hash del commit de la versión
        build_number: Número de build
        features: Lista de nuevas funcionalidades
        bug_fixes: Lista de correcciones de errores
        breaking_changes: Lista de cambios que rompen compatibilidad
        artifacts: URLs de artefactos de build
        
    Returns:
        ToolResult con la versión creada
    """
    try:
        # Verificar que la aplicación existe
        app = db_manager.get_application(application_id)
        if not app:
            return ToolResult(
                success=False,
                message=f"Aplicación {application_id} no encontrada"
            )
        
        new_version = Version(
            version=version,
            application_id=application_id,
            branch=branch,
            commit_hash=commit_hash,
            build_number=build_number,
            created_at=datetime.now(),
            features=features or [],
            bug_fixes=bug_fixes or [],
            breaking_changes=breaking_changes or [],
            artifacts=artifacts or {}
        )
        
        version_id = db_manager.create_version(new_version)
        
        return ToolResult(
            success=True,
            message=f"Versión {version} creada exitosamente para aplicación {app.name}",
            data=new_version.dict()
        )
        
    except Exception as e:
        return ToolResult(
            success=False,
            message=f"Error al crear versión: {str(e)}"
        )


def list_versions(application_id: str = None, limit: int = 10) -> ToolResult:
    """
    Lista las versiones de una aplicación o todas las versiones.
    
    Args:
        application_id: ID de la aplicación (opcional)
        limit: Número máximo de versiones a retornar
        
    Returns:
        ToolResult con la lista de versiones
    """
    try:
        if application_id:
            # Versiones de una aplicación específica
            versions = db_manager.get_versions_by_application(application_id)
            app = db_manager.get_application(application_id)
            app_name = app.name if app else application_id
            
            limited_versions = versions[:limit]
            
            return ToolResult(
                success=True,
                message=f"Se encontraron {len(limited_versions)} versiones para {app_name}",
                data={
                    "application_id": application_id,
                    "application_name": app_name,
                    "versions": [v.dict() for v in limited_versions],
                    "total": len(versions)
                }
            )
        else:
            # Todas las versiones de todas las aplicaciones
            all_versions = []
            applications = db_manager.list_applications()
            
            for app in applications:
                app_versions = db_manager.get_versions_by_application(app.id)
                for version in app_versions:
                    version_dict = version.dict()
                    version_dict['application_name'] = app.name
                    all_versions.append(version_dict)
            
            # Ordenar por fecha de creación
            all_versions.sort(key=lambda v: v['created_at'], reverse=True)
            limited_versions = all_versions[:limit]
            
            return ToolResult(
                success=True,
                message=f"Se encontraron {len(limited_versions)} versiones en total",
                data={
                    "versions": limited_versions,
                    "total": len(all_versions)
                }
            )
        
    except Exception as e:
        return ToolResult(
            success=False,
            message=f"Error al listar versiones: {str(e)}"
        )


def get_version(application_id: str, version: str) -> ToolResult:
    """
    Obtiene los detalles de una versión específica de una aplicación.
    
    Args:
        application_id: ID de la aplicación
        version: Número de versión a buscar
        
    Returns:
        ToolResult con los detalles de la versión
    """
    try:
        versions = db_manager.get_versions_by_application(application_id)
        found_version = next(
            (v for v in versions if v.version == version),
            None
        )
        
        if not found_version:
            return ToolResult(
                success=False,
                message=f"Versión {version} no encontrada para aplicación {application_id}"
            )
        
        # Obtener información de la aplicación
        app = db_manager.get_application(application_id)
        version_dict = found_version.dict()
        version_dict['application_name'] = app.name if app else application_id
        
        return ToolResult(
            success=True,
            message=f"Versión {version} encontrada",
            data=version_dict
        )
        
    except Exception as e:
        return ToolResult(
            success=False,
            message=f"Error al obtener versión: {str(e)}"
        )


def compare_versions(application_id: str, from_version: str, to_version: str) -> ToolResult:
    """
    Compara dos versiones de una aplicación y genera un changelog.
    
    Args:
        application_id: ID de la aplicación
        from_version: Versión origen
        to_version: Versión destino
        
    Returns:
        ToolResult con el changelog entre versiones
    """
    try:
        # Buscar las versiones
        versions = db_manager.get_versions_by_application(application_id)
        
        version_from = next(
            (v for v in versions if v.version == from_version),
            None
        )
        version_to = next(
            (v for v in versions if v.version == to_version),
            None
        )
        
        if not version_from:
            return ToolResult(
                success=False,
                message=f"Versión origen {from_version} no encontrada"
            )
        
        if not version_to:
            return ToolResult(
                success=False,
                message=f"Versión destino {to_version} no encontrada"
            )
        
        # Generar changelog
        changelog = ChangeLog(
            application_id=application_id,
            from_version=from_version,
            to_version=to_version,
            commits=version_to.commits,  # Simplificado para el ejemplo
            features=version_to.features,
            improvements=[],  # Se podría expandir
            bug_fixes=version_to.bug_fixes,
            breaking_changes=version_to.breaking_changes,
            migration_notes=[],  # Se podría expandir
            generated_at=datetime.now()
        )
        
        # Obtener nombre de la aplicación
        app = db_manager.get_application(application_id)
        changelog_dict = changelog.dict()
        changelog_dict['application_name'] = app.name if app else application_id
        
        return ToolResult(
            success=True,
            message=f"Changelog generado entre {from_version} y {to_version} para {app.name if app else application_id}",
            data=changelog_dict
        )
        
    except Exception as e:
        return ToolResult(
            success=False,
            message=f"Error al comparar versiones: {str(e)}"
        )


def create_git_commit(
    hash: str,
    author: str,
    email: str,
    message: str,
    files_changed: List[str] = None
) -> ToolResult:
    """
    Crea un registro de commit de Git.
    
    Args:
        hash: Hash del commit
        author: Autor del commit
        email: Email del autor
        message: Mensaje del commit
        files_changed: Lista de archivos modificados
        
    Returns:
        ToolResult con el commit creado
    """
    try:
        commit = GitCommit(
            hash=hash,
            author=author,
            email=email,
            date=datetime.now(),
            message=message,
            files_changed=files_changed or []
        )
        
        return ToolResult(
            success=True,
            message="Commit creado exitosamente",
            data=commit.dict()
        )
        
    except Exception as e:
        return ToolResult(
            success=False,
            message=f"Error al crear commit: {str(e)}"
        )