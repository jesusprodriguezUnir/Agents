"""
Generador de datos de ejemplo para el sistema de despliegues multi-aplicación.

Crea aplicaciones de ejemplo (.NET Core + Angular) con versiones y despliegues realistas.
"""

import uuid
from datetime import datetime, timedelta
import random
from pathlib import Path
import sys

# Añadir el directorio src al path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from models.deployment import (
    Application, Version, Deployment, Incident, GitCommit,
    Environment, ApplicationType, DeploymentStatus, IncidentSeverity, IncidentStatus
)
from storage.database import DatabaseManager


class SampleDataGenerator:
    """Generador de datos de ejemplo para el sistema."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        
        # Nombres de aplicaciones reales
        self.apps_config = [
            {
                "name": "E-Commerce Frontend",
                "type": ApplicationType.FRONTEND,
                "tech_stack": ["Angular 16", "TypeScript", "SCSS", "Angular Material"],
                "team": "Frontend Team"
            },
            {
                "name": "E-Commerce API",
                "type": ApplicationType.BACKEND,
                "tech_stack": [".NET Core 7", "C#", "Entity Framework", "SQL Server"],
                "team": "Backend Team"
            },
            {
                "name": "Payment Service",
                "type": ApplicationType.MICROSERVICE,
                "tech_stack": [".NET Core 7", "C#", "Redis", "PostgreSQL"],
                "team": "Payments Team"
            },
            {
                "name": "User Management API",
                "type": ApplicationType.MICROSERVICE,
                "tech_stack": [".NET Core 7", "C#", "Identity Server", "SQL Server"],
                "team": "Identity Team"
            },
            {
                "name": "Notification Service",
                "type": ApplicationType.MICROSERVICE,
                "tech_stack": [".NET Core 7", "C#", "RabbitMQ", "MongoDB"],
                "team": "Platform Team"
            },
            {
                "name": "Admin Dashboard",
                "type": ApplicationType.FRONTEND,
                "tech_stack": ["Angular 16", "TypeScript", "PrimeNG", "Charts.js"],
                "team": "Admin Team"
            }
        ]
        
        # Datos para commits realistas
        self.commit_messages = [
            "feat: Add new product catalog filtering",
            "fix: Resolve payment processing timeout",
            "feat: Implement user authentication flow",
            "fix: Fix memory leak in image processing",
            "feat: Add real-time notifications",
            "fix: Resolve CORS issues in API",
            "feat: Implement shopping cart persistence",
            "fix: Fix SQL injection vulnerability",
            "feat: Add support for multiple payment methods",
            "fix: Resolve race condition in order processing",
            "feat: Implement order tracking system",
            "fix: Fix mobile responsive layout issues",
            "feat: Add email notification templates",
            "fix: Resolve database connection pooling issues",
            "feat: Implement advanced search functionality"
        ]
        
        self.features = [
            "Nueva funcionalidad de búsqueda avanzada",
            "Integración con gateway de pagos",
            "Sistema de notificaciones push",
            "Mejoras en la interfaz de usuario",
            "Optimización de rendimiento",
            "Implementación de cache Redis",
            "Sistema de logs centralizado",
            "Autenticación de dos factores",
            "Dashboard de métricas en tiempo real",
            "Integración con servicios externos"
        ]
        
        self.bug_fixes = [
            "Corrección de memory leak en procesamiento de imágenes",
            "Fix de timeout en consultas de base de datos",
            "Resolución de problemas de CORS",
            "Corrección de vulnerabilidad de seguridad",
            "Fix de race condition en pedidos",
            "Corrección de layout responsive",
            "Resolución de problemas de cache",
            "Fix de validación de formularios",
            "Corrección de manejo de errores",
            "Resolución de problemas de concurrencia"
        ]

    def generate_all_sample_data(self):
        """Genera un conjunto completo de datos de ejemplo."""
        print("🚀 Generando datos de ejemplo...")
        
        # Limpiar datos existentes
        self.db.reset_database()
        
        # Crear aplicaciones
        applications = self.create_applications()
        print(f"✅ Creadas {len(applications)} aplicaciones")
        
        # Crear versiones para cada aplicación
        versions_count = 0
        for app in applications:
            versions = self.create_versions_for_app(app.id)
            versions_count += len(versions)
        print(f"✅ Creadas {versions_count} versiones")
        
        # Crear despliegues
        deployments_count = 0
        for app in applications:
            deployments = self.create_deployments_for_app(app.id)
            deployments_count += len(deployments)
        print(f"✅ Creados {deployments_count} despliegues")
        
        # Crear algunas incidencias
        incidents_count = self.create_sample_incidents()
        print(f"✅ Creadas {incidents_count} incidencias")
        
        # Mostrar estadísticas
        stats = self.db.get_stats()
        print("\n📊 Estadísticas finales:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n🎉 Datos de ejemplo generados exitosamente!")

    def create_applications(self) -> list[Application]:
        """Crea aplicaciones de ejemplo."""
        applications = []
        
        for i, config in enumerate(self.apps_config):
            app_id = f"app-{i+1:02d}"
            
            app = Application(
                id=app_id,
                name=config["name"],
                type=config["type"],
                description=f"Aplicación {config['name']} del ecosistema e-commerce",
                repository_url=f"https://github.com/company/{app_id}",
                tech_stack=config["tech_stack"],
                owner_team=config["team"],
                dependencies=[],  # Se pueden agregar dependencias específicas
                health_check_url=f"https://{app_id}.company.com/health",
                created_at=datetime.now() - timedelta(days=random.randint(30, 365))
            )
            
            self.db.create_application(app)
            applications.append(app)
            
        return applications

    def create_versions_for_app(self, app_id: str) -> list[Version]:
        """Crea versiones de ejemplo para una aplicación."""
        versions = []
        base_date = datetime.now() - timedelta(days=90)
        
        # Crear entre 5-8 versiones por aplicación
        version_count = random.randint(5, 8)
        
        for i in range(version_count):
            # Generar número de versión
            major = 2 if i >= version_count - 2 else 1
            minor = random.randint(0, 5)
            patch = random.randint(0, 10)
            version_number = f"{major}.{minor}.{patch}"
            
            # Fecha de la versión
            version_date = base_date + timedelta(days=i * random.randint(5, 15))
            
            # Generar commits
            commits = self.generate_commits(version_date)
            
            version = Version(
                version=version_number,
                application_id=app_id,
                branch="main" if i >= version_count - 3 else random.choice(["develop", "release/1.x", "hotfix"]),
                commit_hash=f"{uuid.uuid4().hex[:8]}",
                build_number=f"build-{1000 + i * 10 + random.randint(1, 9)}",
                created_at=version_date,
                commits=commits,
                features=random.sample(self.features, random.randint(1, 3)),
                bug_fixes=random.sample(self.bug_fixes, random.randint(0, 2)),
                breaking_changes=[] if patch > 0 else random.sample(["API breaking change"], random.randint(0, 1)),
                artifacts={
                    "docker_image": f"company/{app_id}:{version_number}",
                    "build_url": f"https://build.company.com/{app_id}/{1000 + i * 10}"
                }
            )
            
            self.db.create_version(version)
            versions.append(version)
            
        return versions

    def generate_commits(self, base_date: datetime) -> list[GitCommit]:
        """Genera commits realistas para una versión."""
        commits = []
        commit_count = random.randint(3, 12)
        
        authors = [
            ("Juan Pérez", "juan.perez@company.com"),
            ("María García", "maria.garcia@company.com"),
            ("Carlos López", "carlos.lopez@company.com"),
            ("Ana Martínez", "ana.martinez@company.com"),
            ("Diego Rodríguez", "diego.rodriguez@company.com")
        ]
        
        for i in range(commit_count):
            author, email = random.choice(authors)
            commit_date = base_date - timedelta(days=random.randint(1, 14))
            
            commit = GitCommit(
                hash=f"{uuid.uuid4().hex[:8]}",
                author=author,
                email=email,
                date=commit_date,
                message=random.choice(self.commit_messages),
                files_changed=[
                    f"src/components/{random.choice(['auth', 'catalog', 'orders', 'payments'])}.ts",
                    f"src/services/{random.choice(['api', 'user', 'order', 'payment'])}.service.ts"
                ]
            )
            
            commits.append(commit)
            
        return commits

    def create_deployments_for_app(self, app_id: str) -> list[Deployment]:
        """Crea despliegues de ejemplo para una aplicación."""
        deployments = []
        
        # Obtener versiones de la aplicación
        versions = self.db.get_versions_by_application(app_id)
        if not versions:
            return deployments
        
        # Crear despliegues para diferentes entornos
        environments = [Environment.DEVELOPMENT, Environment.PREPRODUCTION, Environment.PRODUCTION]
        
        for env in environments:
            # Número de despliegues por entorno
            deployment_count = {
                Environment.DEVELOPMENT: random.randint(8, 15),
                Environment.PREPRODUCTION: random.randint(5, 10),
                Environment.PRODUCTION: random.randint(3, 8)
            }[env]
            
            # Seleccionar versiones para desplegar
            selected_versions = random.sample(versions, min(deployment_count, len(versions)))
            
            for i, version in enumerate(selected_versions):
                deployment_date = version.created_at + timedelta(
                    hours=random.randint(1, 24),
                    minutes=random.randint(0, 59)
                )
                
                # Calcular duración del despliegue
                duration_minutes = random.randint(5, 30)
                started_at = deployment_date
                completed_at = started_at + timedelta(minutes=duration_minutes)
                
                # Estado del despliegue (mayoría exitosos)
                status_weights = {
                    DeploymentStatus.SUCCESS: 0.8,
                    DeploymentStatus.FAILED: 0.1,
                    DeploymentStatus.ROLLBACK: 0.05,
                    DeploymentStatus.IN_PROGRESS: 0.05
                }
                
                status = random.choices(
                    list(status_weights.keys()),
                    weights=list(status_weights.values())
                )[0]
                
                # Ajustar tiempos según el estado
                if status == DeploymentStatus.IN_PROGRESS:
                    completed_at = None
                elif status == DeploymentStatus.FAILED:
                    completed_at = started_at + timedelta(minutes=random.randint(2, 10))
                
                deployment = Deployment(
                    id=f"deploy-{uuid.uuid4().hex[:8]}",
                    application_id=app_id,
                    environment=env,
                    version=version,
                    status=status,
                    deployed_by=random.choice([
                        "juan.perez", "maria.garcia", "carlos.lopez",
                        "ana.martinez", "diego.rodriguez"
                    ]),
                    deployed_at=deployment_date,
                    started_at=started_at,
                    completed_at=completed_at,
                    rollback_from=None,  # Se puede implementar lógica de rollback
                    notes=self.generate_deployment_notes(status),
                    config_changes={
                        "database_timeout": "30s",
                        "max_connections": "100",
                        "log_level": random.choice(["INFO", "DEBUG", "WARN"])
                    },
                    migration_scripts=[
                        f"migration_{version.version.replace('.', '_')}.sql"
                    ] if random.random() < 0.3 else []
                )
                
                self.db.create_deployment(deployment)
                deployments.append(deployment)
                
        return deployments

    def generate_deployment_notes(self, status: DeploymentStatus) -> str:
        """Genera notas realistas para un despliegue."""
        if status == DeploymentStatus.SUCCESS:
            return random.choice([
                "Despliegue completado sin incidencias",
                "Migración de base de datos ejecutada correctamente",
                "Nuevas funcionalidades activadas",
                "Actualización de dependencias exitosa",
                "Configuración actualizada correctamente"
            ])
        elif status == DeploymentStatus.FAILED:
            return random.choice([
                "Error en la migración de base de datos",
                "Fallo en las pruebas de smoke",
                "Timeout en la conexión a servicios externos",
                "Error de configuración detectado",
                "Dependencias incompatibles encontradas"
            ])
        elif status == DeploymentStatus.IN_PROGRESS:
            return "Despliegue en progreso..."
        else:
            return "Notas del despliegue"

    def create_sample_incidents(self) -> int:
        """Crea incidencias de ejemplo."""
        # Obtener algunos despliegues para asociar incidencias
        deployments = []
        for app in self.db.list_applications():
            app_deployments = self.db.get_deployments_by_application(app.id)
            deployments.extend(app_deployments[:2])  # Solo algunos despliegues
        
        if not deployments:
            return 0
        
        incidents_created = 0
        
        # Crear algunas incidencias (no muchas)
        for _ in range(random.randint(2, 5)):
            deployment = random.choice(deployments)
            
            incident = Incident(
                id=f"inc-{uuid.uuid4().hex[:8]}",
                deployment_id=deployment.id,
                application_id=deployment.application_id,
                title=random.choice([
                    "Alto uso de CPU después del despliegue",
                    "Errores 500 en endpoint de pagos",
                    "Lentitud en consultas de base de datos",
                    "Fallos intermitentes en autenticación",
                    "Problemas de conectividad con servicios externos"
                ]),
                description="Descripción detallada de la incidencia detectada después del despliegue.",
                severity=random.choice(list(IncidentSeverity)),
                status=random.choice(list(IncidentStatus)),
                reported_by=random.choice([
                    "monitoring.system", "juan.perez", "maria.garcia", "support.team"
                ]),
                reported_at=deployment.deployed_at + timedelta(
                    hours=random.randint(1, 48)
                ),
                assigned_to=random.choice([
                    "juan.perez", "maria.garcia", "carlos.lopez", None
                ]),
                resolved_at=None,  # Se puede implementar lógica de resolución
                resolution_notes="",
                affected_components=[
                    random.choice(["API", "Database", "Frontend", "Cache", "External Service"])
                ]
            )
            
            # Simular algunas incidencias resueltas
            if random.random() < 0.6:  # 60% de incidencias resueltas
                incident.status = IncidentStatus.RESOLVED
                incident.resolved_at = incident.reported_at + timedelta(
                    hours=random.randint(1, 24)
                )
                incident.resolution_notes = "Incidencia resuelta aplicando fix específico."
            
            # No implementamos create_incident todavía, pero se puede agregar
            incidents_created += 1
            
        return incidents_created


def main():
    """Función principal para generar datos de ejemplo."""
    print("🎯 Iniciando generación de datos de ejemplo...")
    
    # Crear gestor de base de datos
    db_manager = DatabaseManager("data/deployments.db")
    
    # Crear generador y ejecutar
    generator = SampleDataGenerator(db_manager)
    generator.generate_all_sample_data()
    
    print("\n✨ ¡Proceso completado! La base de datos está lista para usar.")


if __name__ == "__main__":
    main()