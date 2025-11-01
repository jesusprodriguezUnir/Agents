"""
Modelos de datos actualizados para gestión multi-organización.

Define las estructuras de datos para organizaciones, entornos flexibles, aplicaciones, 
despliegues, versiones e incidencias en un ecosistema multi-organización.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# ENUMS - Definiciones de valores permitidos
# ============================================================================

class ComponentType(str, Enum):
    """Tipos de componente de aplicación."""
    FRONTEND = "frontend"  # Angular, React, Vue
    BACKEND = "backend"    # .NET Core API, Node.js
    MICROSERVICE = "microservice"  # Microservicios
    DATABASE = "database"  # Scripts de BD
    INFRASTRUCTURE = "infrastructure"  # Terraform, scripts


class DeploymentStatus(str, Enum):
    """Estados de despliegue."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLBACK = "rollback"


class UrlType(str, Enum):
    """Tipos de URL por entorno/componente."""
    MAIN_APP = "main_app"           # URL principal de la aplicación
    VERSION_API = "version_api"     # Endpoint para consultar versión
    HEALTH_CHECK = "health_check"   # Endpoint de health check
    SWAGGER = "swagger"             # Documentación Swagger/OpenAPI
    ADMIN = "admin"                 # Panel de administración


class IncidentSeverity(str, Enum):
    """Severidad de incidencias."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    """Estados de incidencias."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


# ============================================================================
# MODELOS BASE - Organizaciones y Entornos
# ============================================================================

class Organization(BaseModel):
    """Modelo para organizaciones (proeduca, villanueva, etc.)."""
    id: str = Field(..., description="ID único de la organización")
    name: str = Field(..., description="Nombre de la organización")
    display_name: str = Field(..., description="Nombre para mostrar")
    description: Optional[str] = Field(None, description="Descripción de la organización")
    active: bool = Field(True, description="Si la organización está activa")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de última actualización")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Environment(BaseModel):
    """Modelo para entornos flexibles por organización."""
    id: str = Field(..., description="ID único del entorno")
    organization_id: str = Field(..., description="ID de la organización")
    name: str = Field(..., description="Nombre del entorno (des, pre, test, pro)")
    display_name: str = Field(..., description="Nombre para mostrar")
    description: Optional[str] = Field(None, description="Descripción del entorno")
    order_priority: int = Field(1, description="Orden de prioridad para mostrar")
    active: bool = Field(True, description="Si el entorno está activo")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")
    
    # Relaciones
    organization: Optional[Organization] = Field(None, description="Organización asociada")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EnvironmentUrl(BaseModel):
    """Modelo para URLs específicas por entorno/componente."""
    id: str = Field(..., description="ID único de la URL")
    environment_id: str = Field(..., description="ID del entorno")
    component_id: str = Field(..., description="ID del componente")
    url_type: UrlType = Field(..., description="Tipo de URL")
    url: str = Field(..., description="URL completa")
    description: Optional[str] = Field(None, description="Descripción de la URL")
    active: bool = Field(True, description="Si la URL está activa")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")
    
    # Relaciones
    environment: Optional[Environment] = Field(None, description="Entorno asociado")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ============================================================================
# MODELOS DE APLICACIONES Y COMPONENTES
# ============================================================================

class Application(BaseModel):
    """Aplicación principal del ecosistema."""
    id: str = Field(..., description="ID único de la aplicación")
    organization_id: str = Field(..., description="ID de la organización")
    name: str = Field(..., description="Nombre de la aplicación")
    description: Optional[str] = Field(None, description="Descripción detallada")
    owner_team: Optional[str] = Field(None, description="Equipo responsable")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")
    
    # Relaciones
    organization: Optional[Organization] = Field(None, description="Organización asociada")
    components: List["ApplicationComponent"] = Field(default_factory=list, description="Componentes")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ApplicationComponent(BaseModel):
    """Componente de una aplicación (frontend, backend, etc.)."""
    id: str = Field(..., description="ID único del componente")
    application_id: str = Field(..., description="ID de la aplicación padre")
    name: str = Field(..., description="Nombre del componente")
    type: ComponentType = Field(..., description="Tipo de componente")
    repository_url: Optional[str] = Field(None, description="URL del repositorio")
    tech_stack: Optional[str] = Field(None, description="Stack tecnológico")
    health_check_url: Optional[str] = Field(None, description="URL de health check")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")
    
    # Relaciones
    application: Optional[Application] = Field(None, description="Aplicación padre")
    versions: List["Version"] = Field(default_factory=list, description="Versiones")
    urls: List[EnvironmentUrl] = Field(default_factory=list, description="URLs por entorno")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ============================================================================
# MODELOS DE VERSIONES Y DESPLIEGUES
# ============================================================================

class GitCommit(BaseModel):
    """Información de un commit de Git."""
    hash: str = Field(..., description="Hash del commit")
    author: str = Field(..., description="Autor del commit")
    email: str = Field(..., description="Email del autor")
    date: datetime = Field(..., description="Fecha del commit")
    message: str = Field(..., description="Mensaje del commit")
    files_changed: List[str] = Field(default_factory=list, description="Archivos modificados")


class Version(BaseModel):
    """Versión específica de un componente."""
    id: Optional[int] = Field(None, description="ID autoincremental")
    version: str = Field(..., description="Número de versión")
    component_id: str = Field(..., description="ID del componente")
    branch: Optional[str] = Field(None, description="Rama de Git")
    commit_hash: Optional[str] = Field(None, description="Hash del commit")
    build_number: Optional[str] = Field(None, description="Número de build")
    features: Optional[str] = Field(None, description="Nuevas características")
    bug_fixes: Optional[str] = Field(None, description="Correcciones de errores")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")
    
    # Información extendida
    commits: List[GitCommit] = Field(default_factory=list, description="Commits incluidos")
    breaking_changes: List[str] = Field(default_factory=list, description="Cambios que rompen compatibilidad")
    artifacts: Dict[str, str] = Field(default_factory=dict, description="URLs de artefactos de build")
    
    # Relaciones
    component: Optional[ApplicationComponent] = Field(None, description="Componente asociado")
    deployments: List["Deployment"] = Field(default_factory=list, description="Despliegues")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Deployment(BaseModel):
    """Despliegue de una versión en un entorno específico."""
    id: str = Field(..., description="ID único del despliegue")
    component_id: str = Field(..., description="ID del componente")
    version_id: int = Field(..., description="ID de la versión")
    environment_id: str = Field(..., description="ID del entorno")
    status: DeploymentStatus = Field(..., description="Estado del despliegue")
    deployed_by: Optional[str] = Field(None, description="Usuario que realizó el despliegue")
    deployed_at: datetime = Field(default_factory=datetime.now, description="Fecha del despliegue")
    started_at: Optional[datetime] = Field(None, description="Hora de inicio del despliegue")
    completed_at: Optional[datetime] = Field(None, description="Hora de finalización")
    rollback_from: Optional[str] = Field(None, description="ID de despliegue del cual se hizo rollback")
    notes: Optional[str] = Field(None, description="Notas adicionales")
    
    # Información extendida
    config_changes: Dict[str, Any] = Field(default_factory=dict, description="Cambios de configuración")
    migration_scripts: List[str] = Field(default_factory=list, description="Scripts de migración ejecutados")
    
    # Relaciones
    component: Optional[ApplicationComponent] = Field(None, description="Componente")
    version: Optional[Version] = Field(None, description="Versión")
    environment: Optional[Environment] = Field(None, description="Entorno")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ============================================================================
# MODELOS DE AGREGACIÓN Y CONSULTA
# ============================================================================

class OrganizationSummary(BaseModel):
    """Resumen por organización."""
    organization: Organization
    environments: List[Environment]
    applications_count: int = Field(0, description="Número de aplicaciones")
    components_count: int = Field(0, description="Número de componentes")
    versions_count: int = Field(0, description="Número de versiones")
    deployments_count: int = Field(0, description="Número de despliegues")
    last_deployment: Optional[datetime] = Field(None, description="Último despliegue")


class EnvironmentStatus(BaseModel):
    """Estado de un entorno específico."""
    environment: Environment
    components_total: int = Field(0, description="Total de componentes")
    components_deployed: int = Field(0, description="Componentes desplegados")
    components_successful: int = Field(0, description="Despliegues exitosos")
    components_failed: int = Field(0, description="Despliegues fallidos")
    last_deployment: Optional[datetime] = Field(None, description="Último despliegue")
    success_rate: float = Field(0.0, description="Tasa de éxito")


class ApplicationStatus(BaseModel):
    """Estado de una aplicación en todos sus entornos."""
    application: Application
    environments_status: Dict[str, EnvironmentStatus] = Field(
        default_factory=dict, 
        description="Estado por entorno"
    )
    total_deployments: int = Field(0, description="Total de despliegues")
    success_rate: float = Field(0.0, description="Tasa de éxito general")


class ComponentEnvironmentStatus(BaseModel):
    """Estado de un componente en un entorno específico."""
    component: ApplicationComponent
    environment: Environment
    current_version: Optional[str] = Field(None, description="Versión actual desplegada")
    current_deployment: Optional[Deployment] = Field(None, description="Despliegue actual")
    last_successful_deployment: Optional[Deployment] = Field(None, description="Último despliegue exitoso")
    health_status: str = Field(default="unknown", description="Estado de salud")
    uptime_percentage: float = Field(default=0.0, description="Porcentaje de uptime")
    last_health_check: Optional[datetime] = Field(None, description="Último health check")
    urls: List[EnvironmentUrl] = Field(default_factory=list, description="URLs del componente en este entorno")


class DeploymentHistory(BaseModel):
    """Historial de despliegues para consulta."""
    deployments: List[Deployment]
    total_count: int = Field(0, description="Total de despliegues")
    success_count: int = Field(0, description="Despliegues exitosos")
    failed_count: int = Field(0, description="Despliegues fallidos")
    success_rate: float = Field(0.0, description="Tasa de éxito")


class DeploymentSummary(BaseModel):
    """Resumen de despliegues por período."""
    period: str = Field(..., description="Período de tiempo")
    organization_id: Optional[str] = Field(None, description="ID de organización (opcional para filtro)")
    application_id: Optional[str] = Field(None, description="ID de aplicación (opcional para filtro)")
    total_deployments: int = Field(..., description="Total de despliegues")
    successful_deployments: int = Field(..., description="Despliegues exitosos")
    failed_deployments: int = Field(..., description="Despliegues fallidos")
    rollbacks: int = Field(..., description="Rollbacks realizados")
    average_duration: float = Field(..., description="Duración promedio en minutos")
    environments: Dict[str, int] = Field(default_factory=dict, description="Despliegues por entorno")


# ============================================================================
# MODELOS DE INCIDENCIAS
# ============================================================================

class Incident(BaseModel):
    """Incidencia post-despliegue."""
    id: str = Field(..., description="ID único de la incidencia")
    deployment_id: str = Field(..., description="ID del despliegue relacionado")
    component_id: str = Field(..., description="ID del componente afectado")
    title: str = Field(..., description="Título de la incidencia")
    description: str = Field(..., description="Descripción detallada")
    severity: IncidentSeverity = Field(..., description="Severidad de la incidencia")
    status: IncidentStatus = Field(..., description="Estado actual")
    reported_by: str = Field(..., description="Usuario que reportó la incidencia")
    reported_at: datetime = Field(default_factory=datetime.now, description="Fecha de reporte")
    assigned_to: Optional[str] = Field(None, description="Usuario asignado")
    resolved_at: Optional[datetime] = Field(None, description="Fecha de resolución")
    resolution_notes: str = Field(default="", description="Notas de resolución")
    affected_components: List[str] = Field(default_factory=list, description="Componentes afectados")
    
    # Relaciones
    deployment: Optional[Deployment] = Field(None, description="Despliegue relacionado")
    component: Optional[ApplicationComponent] = Field(None, description="Componente afectado")


class ChangeLog(BaseModel):
    """Registro de cambios entre versiones."""
    component_id: str = Field(..., description="ID del componente")
    from_version: str = Field(..., description="Versión origen")
    to_version: str = Field(..., description="Versión destino")
    commits: List[GitCommit] = Field(default_factory=list, description="Commits entre versiones")
    features: List[str] = Field(default_factory=list, description="Nuevas funcionalidades")
    bug_fixes: List[str] = Field(default_factory=list, description="Correcciones de errores")
    breaking_changes: List[str] = Field(default_factory=list, description="Cambios que rompen compatibilidad")


# ============================================================================
# MODELOS DE RESPUESTA API
# ============================================================================

class VersionApiResponse(BaseModel):
    """Respuesta estándar de API de versión."""
    version: str = Field(..., description="Versión actual")
    build_number: str = Field(..., description="Número de build")
    commit_hash: str = Field(..., description="Hash del commit")
    build_date: str = Field(..., description="Fecha de build")
    environment: str = Field(..., description="Entorno actual")


class HealthCheckResponse(BaseModel):
    """Respuesta estándar de health check."""
    status: str = Field(..., description="Estado (healthy, unhealthy, degraded)")
    version: str = Field(..., description="Versión actual")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp del check")
    details: Dict[str, Any] = Field(default_factory=dict, description="Detalles adicionales")
    checks: Dict[str, str] = Field(default_factory=dict, description="Estado de checks individuales")


# Habilitar forward references
Application.model_rebuild()
ApplicationComponent.model_rebuild()
Version.model_rebuild()
Deployment.model_rebuild()