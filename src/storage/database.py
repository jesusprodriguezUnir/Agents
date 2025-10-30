"""
Sistema de almacenamiento de datos para el MCP Deployment Manager.

Implementa persistencia con SQLite para aplicaciones, versiones, despliegues e incidencias.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging

from ..models.deployment import (
    Application, Version, Deployment, Incident,
    ApplicationEnvironmentStatus, EnvironmentOverview,
    Environment, DeploymentStatus, IncidentStatus,
    ApplicationType, IncidentSeverity
)

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gestor de base de datos SQLite para el sistema de despliegues."""

    def __init__(self, db_path: str = "deployments.db"):
        """
        Inicializa la conexión a la base de datos.
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Inicializa las tablas de la base de datos."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Tabla de aplicaciones
            conn.execute("""
                CREATE TABLE IF NOT EXISTS applications (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    repository_url TEXT DEFAULT '',
                    tech_stack TEXT DEFAULT '[]',  -- JSON array
                    owner_team TEXT DEFAULT '',
                    dependencies TEXT DEFAULT '[]',  -- JSON array
                    health_check_url TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tabla de versiones
            conn.execute("""
                CREATE TABLE IF NOT EXISTS versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT NOT NULL,
                    application_id TEXT NOT NULL,
                    branch TEXT NOT NULL,
                    commit_hash TEXT NOT NULL,
                    build_number TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    commits TEXT DEFAULT '[]',  -- JSON array
                    features TEXT DEFAULT '[]',  -- JSON array
                    bug_fixes TEXT DEFAULT '[]',  -- JSON array
                    breaking_changes TEXT DEFAULT '[]',  -- JSON array
                    artifacts TEXT DEFAULT '{}',  -- JSON object
                    FOREIGN KEY (application_id) REFERENCES applications (id),
                    UNIQUE(application_id, version)
                )
            """)

            # Tabla de despliegues
            conn.execute("""
                CREATE TABLE IF NOT EXISTS deployments (
                    id TEXT PRIMARY KEY,
                    application_id TEXT NOT NULL,
                    environment TEXT NOT NULL,
                    version_id INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    deployed_by TEXT NOT NULL,
                    deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    rollback_from TEXT,
                    notes TEXT DEFAULT '',
                    config_changes TEXT DEFAULT '{}',  -- JSON object
                    migration_scripts TEXT DEFAULT '[]',  -- JSON array
                    FOREIGN KEY (application_id) REFERENCES applications (id),
                    FOREIGN KEY (version_id) REFERENCES versions (id),
                    FOREIGN KEY (rollback_from) REFERENCES deployments (id)
                )
            """)

            # Tabla de incidencias
            conn.execute("""
                CREATE TABLE IF NOT EXISTS incidents (
                    id TEXT PRIMARY KEY,
                    deployment_id TEXT NOT NULL,
                    application_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    status TEXT NOT NULL,
                    reported_by TEXT NOT NULL,
                    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    assigned_to TEXT,
                    resolved_at TIMESTAMP,
                    resolution_notes TEXT DEFAULT '',
                    affected_components TEXT DEFAULT '[]',  -- JSON array
                    FOREIGN KEY (deployment_id) REFERENCES deployments (id),
                    FOREIGN KEY (application_id) REFERENCES applications (id)
                )
            """)

            # Tabla de estado de aplicaciones por entorno
            conn.execute("""
                CREATE TABLE IF NOT EXISTS app_environment_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    application_id TEXT NOT NULL,
                    environment TEXT NOT NULL,
                    current_version TEXT,
                    current_deployment_id TEXT,
                    health_status TEXT DEFAULT 'unknown',
                    uptime_percentage REAL DEFAULT 0.0,
                    last_health_check TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (application_id) REFERENCES applications (id),
                    FOREIGN KEY (current_deployment_id) REFERENCES deployments (id),
                    UNIQUE(application_id, environment)
                )
            """)

            # Índices para mejorar rendimiento
            conn.execute("CREATE INDEX IF NOT EXISTS idx_deployments_app_env ON deployments(application_id, environment)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_deployments_date ON deployments(deployed_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_incidents_deployment ON incidents(deployment_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_versions_app ON versions(application_id)")

            conn.commit()
            logger.info("Base de datos inicializada correctamente")

    # === APLICACIONES ===

    def create_application(self, application: Application) -> str:
        """Crea una nueva aplicación."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO applications 
                (id, name, type, description, repository_url, tech_stack, 
                 owner_team, dependencies, health_check_url, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                application.id, application.name, application.type.value,
                application.description, application.repository_url,
                json.dumps(application.tech_stack), application.owner_team,
                json.dumps(application.dependencies), application.health_check_url,
                application.created_at.isoformat()
            ))
            conn.commit()
            logger.info(f"Aplicación creada: {application.name} ({application.id})")
            return application.id

    def get_application(self, app_id: str) -> Optional[Application]:
        """Obtiene una aplicación por ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM applications WHERE id = ?", (app_id,)
            ).fetchone()
            
            if row:
                return Application(
                    id=row['id'],
                    name=row['name'],
                    type=ApplicationType(row['type']),
                    description=row['description'],
                    repository_url=row['repository_url'],
                    tech_stack=json.loads(row['tech_stack']),
                    owner_team=row['owner_team'],
                    dependencies=json.loads(row['dependencies']),
                    health_check_url=row['health_check_url'],
                    created_at=datetime.fromisoformat(row['created_at'])
                )
            return None

    def list_applications(self) -> List[Application]:
        """Lista todas las aplicaciones."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM applications ORDER BY name").fetchall()
            
            return [
                Application(
                    id=row['id'],
                    name=row['name'],
                    type=ApplicationType(row['type']),
                    description=row['description'],
                    repository_url=row['repository_url'],
                    tech_stack=json.loads(row['tech_stack']),
                    owner_team=row['owner_team'],
                    dependencies=json.loads(row['dependencies']),
                    health_check_url=row['health_check_url'],
                    created_at=datetime.fromisoformat(row['created_at'])
                )
                for row in rows
            ]

    # === VERSIONES ===

    def create_version(self, version: Version) -> int:
        """Crea una nueva versión."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO versions 
                (version, application_id, branch, commit_hash, build_number, 
                 created_at, commits, features, bug_fixes, breaking_changes, artifacts)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                version.version, version.application_id, version.branch,
                version.commit_hash, version.build_number,
                version.created_at.isoformat(),
                json.dumps([commit.dict() for commit in version.commits]),
                json.dumps(version.features),
                json.dumps(version.bug_fixes),
                json.dumps(version.breaking_changes),
                json.dumps(version.artifacts)
            ))
            conn.commit()
            version_id = cursor.lastrowid
            logger.info(f"Versión creada: {version.version} para app {version.application_id}")
            return version_id

    def get_version(self, version_id: int) -> Optional[Version]:
        """Obtiene una versión por ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM versions WHERE id = ?", (version_id,)
            ).fetchone()
            
            if row:
                return self._row_to_version(row)
            return None

    def get_versions_by_application(self, app_id: str) -> List[Version]:
        """Obtiene todas las versiones de una aplicación."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM versions WHERE application_id = ? ORDER BY created_at DESC",
                (app_id,)
            ).fetchall()
            
            return [self._row_to_version(row) for row in rows]

    def _row_to_version(self, row: sqlite3.Row) -> Version:
        """Convierte una fila de BD a objeto Version."""
        from ..models.deployment import GitCommit
        
        commits_data = json.loads(row['commits'])
        commits = [GitCommit(**commit) for commit in commits_data]
        
        return Version(
            version=row['version'],
            application_id=row['application_id'],
            branch=row['branch'],
            commit_hash=row['commit_hash'],
            build_number=row['build_number'],
            created_at=datetime.fromisoformat(row['created_at']),
            commits=commits,
            features=json.loads(row['features']),
            bug_fixes=json.loads(row['bug_fixes']),
            breaking_changes=json.loads(row['breaking_changes']),
            artifacts=json.loads(row['artifacts'])
        )

    # === DESPLIEGUES ===

    def create_deployment(self, deployment: Deployment) -> str:
        """Crea un nuevo despliegue."""
        # Primero necesitamos obtener el version_id
        version_id = self._get_version_id(deployment.application_id, deployment.version.version)
        if not version_id:
            # Si la versión no existe, la creamos
            version_id = self.create_version(deployment.version)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO deployments 
                (id, application_id, environment, version_id, status, deployed_by,
                 deployed_at, started_at, completed_at, rollback_from, notes,
                 config_changes, migration_scripts)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                deployment.id, deployment.application_id, deployment.environment.value,
                version_id, deployment.status.value, deployment.deployed_by,
                deployment.deployed_at.isoformat(),
                deployment.started_at.isoformat() if deployment.started_at else None,
                deployment.completed_at.isoformat() if deployment.completed_at else None,
                deployment.rollback_from, deployment.notes,
                json.dumps(deployment.config_changes),
                json.dumps(deployment.migration_scripts)
            ))
            conn.commit()
            
            # Actualizar estado del entorno si el despliegue fue exitoso
            if deployment.status == DeploymentStatus.SUCCESS:
                self._update_environment_status(deployment)
            
            logger.info(f"Despliegue creado: {deployment.id}")
            return deployment.id

    def _get_version_id(self, app_id: str, version: str) -> Optional[int]:
        """Obtiene el ID de una versión."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT id FROM versions WHERE application_id = ? AND version = ?",
                (app_id, version)
            ).fetchone()
            return row[0] if row else None

    def _update_environment_status(self, deployment: Deployment):
        """Actualiza el estado del entorno después de un despliegue exitoso."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO app_environment_status
                (application_id, environment, current_version, current_deployment_id, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                deployment.application_id, deployment.environment.value,
                deployment.version.version, deployment.id,
                datetime.now().isoformat()
            ))
            conn.commit()

    def get_deployments_by_application(self, app_id: str, environment: Optional[Environment] = None) -> List[Deployment]:
        """Obtiene despliegues de una aplicación."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if environment:
                rows = conn.execute("""
                    SELECT d.*, v.* FROM deployments d
                    JOIN versions v ON d.version_id = v.id
                    WHERE d.application_id = ? AND d.environment = ?
                    ORDER BY d.deployed_at DESC
                """, (app_id, environment.value)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT d.*, v.* FROM deployments d
                    JOIN versions v ON d.version_id = v.id
                    WHERE d.application_id = ?
                    ORDER BY d.deployed_at DESC
                """, (app_id,)).fetchall()
            
            return [self._row_to_deployment(row) for row in rows]

    def _row_to_deployment(self, row: sqlite3.Row) -> Deployment:
        """Convierte una fila de BD a objeto Deployment."""
        # Construir objeto Version
        version = Version(
            version=row['version'],
            application_id=row['application_id'],
            branch=row['branch'],
            commit_hash=row['commit_hash'],
            build_number=row['build_number'],
            created_at=datetime.fromisoformat(row['created_at']),
            commits=[],  # Los commits se cargan por separado si es necesario
            features=json.loads(row['features']),
            bug_fixes=json.loads(row['bug_fixes']),
            breaking_changes=json.loads(row['breaking_changes']),
            artifacts=json.loads(row['artifacts'])
        )
        
        return Deployment(
            id=row['id'],
            application_id=row['application_id'],
            environment=Environment(row['environment']),
            version=version,
            status=DeploymentStatus(row['status']),
            deployed_by=row['deployed_by'],
            deployed_at=datetime.fromisoformat(row['deployed_at']),
            started_at=datetime.fromisoformat(row['started_at']) if row['started_at'] else None,
            completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None,
            rollback_from=row['rollback_from'],
            notes=row['notes'],
            config_changes=json.loads(row['config_changes']),
            migration_scripts=json.loads(row['migration_scripts'])
        )

    # === ESTADO DE ENTORNOS ===

    def get_environment_overview(self, environment: Environment) -> EnvironmentOverview:
        """Obtiene vista general de un entorno."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Obtener estado de todas las aplicaciones en el entorno
            rows = conn.execute("""
                SELECT 
                    a.id, a.name, a.type,
                    aes.current_version, aes.health_status, aes.uptime_percentage,
                    aes.last_health_check, aes.current_deployment_id
                FROM applications a
                LEFT JOIN app_environment_status aes ON a.id = aes.application_id 
                    AND aes.environment = ?
                ORDER BY a.name
            """, (environment.value,)).fetchall()
            
            app_statuses = []
            healthy_count = 0
            issues_count = 0
            
            for row in rows:
                # Obtener incidencias activas
                active_incidents = self._get_active_incidents(row['id'])
                
                # Determinar estado de salud
                health_status = row['health_status'] or 'unknown'
                if health_status == 'healthy':
                    healthy_count += 1
                elif len(active_incidents) > 0 or health_status in ['unhealthy', 'degraded']:
                    issues_count += 1
                
                # Obtener despliegue actual
                current_deployment = None
                if row['current_deployment_id']:
                    current_deployment = self._get_deployment_by_id(row['current_deployment_id'])
                
                app_status = ApplicationEnvironmentStatus(
                    application_id=row['id'],
                    environment=environment,
                    current_version=row['current_version'],
                    current_deployment=current_deployment,
                    health_status=health_status,
                    uptime_percentage=row['uptime_percentage'] or 0.0,
                    active_incidents=active_incidents,
                    last_health_check=datetime.fromisoformat(row['last_health_check']) if row['last_health_check'] else None
                )
                app_statuses.append(app_status)
            
            # Obtener último despliegue en el entorno
            last_deployment_row = conn.execute("""
                SELECT MAX(deployed_at) as last_deployment
                FROM deployments 
                WHERE environment = ?
            """, (environment.value,)).fetchone()
            
            last_deployment = None
            if last_deployment_row['last_deployment']:
                last_deployment = datetime.fromisoformat(last_deployment_row['last_deployment'])
            
            # Contar despliegues pendientes
            pending_count = conn.execute("""
                SELECT COUNT(*) as count
                FROM deployments 
                WHERE environment = ? AND status = 'pending'
            """, (environment.value,)).fetchone()['count']
            
            return EnvironmentOverview(
                environment=environment,
                applications=app_statuses,
                total_applications=len(app_statuses),
                healthy_applications=healthy_count,
                applications_with_issues=issues_count,
                last_deployment=last_deployment,
                pending_deployments=pending_count
            )

    def _get_active_incidents(self, app_id: str) -> List[Incident]:
        """Obtiene incidencias activas de una aplicación."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT * FROM incidents 
                WHERE application_id = ? AND status IN ('open', 'in_progress')
                ORDER BY reported_at DESC
            """, (app_id,)).fetchall()
            
            return [self._row_to_incident(row) for row in rows]

    def _get_deployment_by_id(self, deployment_id: str) -> Optional[Deployment]:
        """Obtiene un despliegue por ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("""
                SELECT d.*, v.* FROM deployments d
                JOIN versions v ON d.version_id = v.id
                WHERE d.id = ?
            """, (deployment_id,)).fetchone()
            
            return self._row_to_deployment(row) if row else None

    def _row_to_incident(self, row: sqlite3.Row) -> Incident:
        """Convierte una fila de BD a objeto Incident."""
        return Incident(
            id=row['id'],
            deployment_id=row['deployment_id'],
            application_id=row['application_id'],
            title=row['title'],
            description=row['description'],
            severity=IncidentSeverity(row['severity']),
            status=IncidentStatus(row['status']),
            reported_by=row['reported_by'],
            reported_at=datetime.fromisoformat(row['reported_at']),
            assigned_to=row['assigned_to'],
            resolved_at=datetime.fromisoformat(row['resolved_at']) if row['resolved_at'] else None,
            resolution_notes=row['resolution_notes'],
            affected_components=json.loads(row['affected_components'])
        )

    # === UTILIDADES ===

    def reset_database(self):
        """Reinicia la base de datos eliminando todos los datos."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM incidents")
            conn.execute("DELETE FROM app_environment_status")
            conn.execute("DELETE FROM deployments")
            conn.execute("DELETE FROM versions")
            conn.execute("DELETE FROM applications")
            conn.commit()
            logger.info("Base de datos reiniciada")

    def get_stats(self) -> Dict[str, int]:
        """Obtiene estadísticas generales de la base de datos."""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            
            stats['applications'] = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
            stats['versions'] = conn.execute("SELECT COUNT(*) FROM versions").fetchone()[0]
            stats['deployments'] = conn.execute("SELECT COUNT(*) FROM deployments").fetchone()[0]
            stats['incidents'] = conn.execute("SELECT COUNT(*) FROM incidents").fetchone()[0]
            
            return stats