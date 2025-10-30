"""
Modelos de datos para gestión de despliegues y versiones.

Define las estructuras de datos para aplicaciones, despliegues, versiones,
entornos e incidencias en un ecosistema multi-aplicación.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Environment(str, Enum):
    """Entornos de despliegue disponibles."""
    DEVELOPMENT = "dev"
    PREPRODUCTION = "pre"
    PRODUCTION = "prod"


class ApplicationType(str, Enum):
    """Tipos de aplicación."""
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


class Application(BaseModel):
    """Definición de una aplicación."""
    id: str = Field(..., description="ID único de la aplicación")
    name: str = Field(..., description="Nombre de la aplicación")
    type: ApplicationType = Field(..., description="Tipo de aplicación")
    description: str = Field(default="", description="Descripción de la aplicación")
    repository_url: str = Field(default="", description="URL del repositorio Git")
    tech_stack: List[str] = Field(default_factory=list, description="Stack tecnológico")
    owner_team: str = Field(default="", description="Equipo responsable")
    dependencies: List[str] = Field(default_factory=list, description="IDs de aplicaciones dependientes")
    health_check_url: str = Field(default="", description="URL de health check")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")


class GitCommit(BaseModel):
    """Información de un commit de Git."""
    hash: str = Field(..., description="Hash del commit")
    author: str = Field(..., description="Autor del commit")
    email: str = Field(..., description="Email del autor")
    date: datetime = Field(..., description="Fecha del commit")
    message: str = Field(..., description="Mensaje del commit")
    files_changed: List[str] = Field(default_factory=list, description="Archivos modificados")


class Version(BaseModel):
    """Información de una versión de aplicación."""
    version: str = Field(..., description="Número de versión (ej: 1.2.3)")
    application_id: str = Field(..., description="ID de la aplicación")
    branch: str = Field(..., description="Rama de Git")
    commit_hash: str = Field(..., description="Hash del commit de la versión")
    build_number: str = Field(..., description="Número de build")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")
    commits: List[GitCommit] = Field(default_factory=list, description="Commits incluidos")
    features: List[str] = Field(default_factory=list, description="Nuevas funcionalidades")
    bug_fixes: List[str] = Field(default_factory=list, description="Correcciones de errores")
    breaking_changes: List[str] = Field(default_factory=list, description="Cambios que rompen compatibilidad")
    artifacts: Dict[str, str] = Field(default_factory=dict, description="URLs de artefactos de build")


class Deployment(BaseModel):
    """Registro de un despliegue."""
    id: str = Field(..., description="ID único del despliegue")
    application_id: str = Field(..., description="ID de la aplicación")
    environment: Environment = Field(..., description="Entorno de despliegue")
    version: Version = Field(..., description="Versión desplegada")
    status: DeploymentStatus = Field(..., description="Estado del despliegue")
    deployed_by: str = Field(..., description="Usuario que realizó el despliegue")
    deployed_at: datetime = Field(default_factory=datetime.now, description="Fecha del despliegue")
    started_at: Optional[datetime] = Field(None, description="Hora de inicio del despliegue")
    completed_at: Optional[datetime] = Field(None, description="Hora de finalización")
    rollback_from: Optional[str] = Field(None, description="ID de despliegue del cual se hizo rollback")
    notes: str = Field(default="", description="Notas adicionales del despliegue")
    config_changes: Dict[str, Any] = Field(default_factory=dict, description="Cambios de configuración")
    migration_scripts: List[str] = Field(default_factory=list, description="Scripts de migración ejecutados")


class Incident(BaseModel):
    """Incidencia post-despliegue."""
    id: str = Field(..., description="ID único de la incidencia")
    deployment_id: str = Field(..., description="ID del despliegue relacionado")
    application_id: str = Field(..., description="ID de la aplicación afectada")
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


class ApplicationEnvironmentStatus(BaseModel):
    """Estado de una aplicación en un entorno específico."""
    application_id: str = Field(..., description="ID de la aplicación")
    environment: Environment = Field(..., description="Entorno")
    current_version: Optional[str] = Field(None, description="Versión actual desplegada")
    current_deployment: Optional[Deployment] = Field(None, description="Despliegue actual")
    last_successful_deployment: Optional[Deployment] = Field(None, description="Último despliegue exitoso")
    health_status: str = Field(default="unknown", description="Estado de salud")
    uptime_percentage: float = Field(default=0.0, description="Porcentaje de uptime")
    active_incidents: List[Incident] = Field(default_factory=list, description="Incidencias activas")
    last_health_check: Optional[datetime] = Field(None, description="Último health check")


class EnvironmentOverview(BaseModel):
    """Vista general de un entorno con todas las aplicaciones."""
    environment: Environment = Field(..., description="Entorno")
    applications: List[ApplicationEnvironmentStatus] = Field(default_factory=list, description="Estado de aplicaciones")
    total_applications: int = Field(default=0, description="Total de aplicaciones")
    healthy_applications: int = Field(default=0, description="Aplicaciones saludables")
    applications_with_issues: int = Field(default=0, description="Aplicaciones con problemas")
    last_deployment: Optional[datetime] = Field(None, description="Último despliegue en el entorno")
    pending_deployments: int = Field(default=0, description="Despliegues pendientes")


class DeploymentSummary(BaseModel):
    """Resumen de despliegues por período."""
    period: str = Field(..., description="Período de tiempo")
    application_id: Optional[str] = Field(None, description="ID de aplicación (opcional para filtro)")
    total_deployments: int = Field(..., description="Total de despliegues")
    successful_deployments: int = Field(..., description="Despliegues exitosos")
    failed_deployments: int = Field(..., description="Despliegues fallidos")
    rollbacks: int = Field(..., description="Rollbacks realizados")
    average_duration: float = Field(..., description="Duración promedio en minutos")
    environments: Dict[Environment, int] = Field(default_factory=dict, description="Despliegues por entorno")


class ChangeLog(BaseModel):
    """Registro de cambios entre versiones."""
    application_id: str = Field(..., description="ID de la aplicación")
    from_version: str = Field(..., description="Versión origen")
    to_version: str = Field(..., description="Versión destino")
    commits: List[GitCommit] = Field(default_factory=list, description="Commits entre versiones")
    features: List[str] = Field(default_factory=list, description="Nuevas funcionalidades")
    improvements: List[str] = Field(default_factory=list, description="Mejoras")
    bug_fixes: List[str] = Field(default_factory=list, description="Correcciones")
    breaking_changes: List[str] = Field(default_factory=list, description="Cambios incompatibles")
    migration_notes: List[str] = Field(default_factory=list, description="Notas de migración")
    generated_at: datetime = Field(default_factory=datetime.now, description="Fecha de generación")