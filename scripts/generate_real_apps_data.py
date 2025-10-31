"""
Generador de datos reales para el sistema de despliegues.

Crea las aplicaciones reales de UNIR con sus repositorios y tecnologías específicas.
"""

import uuid
from datetime import datetime, timedelta
import random
from pathlib import Path
import sys

# Añadir el directorio src al path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from models.deployment import (
    Application, Version, Deployment, Incident, GitCommit,
    Environment, ApplicationType, DeploymentStatus, IncidentSeverity, IncidentStatus
)
from storage.database import DatabaseManager


class RealAppsDataGenerator:
    """Generador de datos con aplicaciones reales de UNIR."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        
        # Aplicaciones reales de UNIR
        self.real_apps = [
            {
                "id": "expedientes",
                "name": "Expedientes ERP",
                "description": "Sistema de gestión de expedientes académicos",
                "owner_team": "Equipo Académico",
                "components": [
                    {
                        "type": ApplicationType.FRONTEND,
                        "tech_stack": ["Angular 18", "TypeScript", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/core-expedienteserp-spa"
                    },
                    {
                        "type": ApplicationType.BACKEND,
                        "tech_stack": [".NET Core 8", "C#", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/ExpedientesErpNetCore"
                    }
                ]
            },
            {
                "id": "expedicion-titulos",
                "name": "Expedición de Títulos",
                "description": "Sistema para expedición y gestión de títulos académicos",
                "owner_team": "Equipo Académico",
                "components": [
                    {
                        "type": ApplicationType.FRONTEND,
                        "tech_stack": ["Angular 18", "TypeScript", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-expediciontitulos-spa"
                    },
                    {
                        "type": ApplicationType.BACKEND,
                        "tech_stack": [".NET Core 8", "C#", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-expediciontitulos-be"
                    }
                ]
            },
            {
                "id": "cargos-funcionales",
                "name": "Cargos Funcionales",
                "description": "Sistema de gestión de cargos funcionales académicos",
                "owner_team": "Equipo Académico",
                "components": [
                    {
                        "type": ApplicationType.FRONTEND,
                        "tech_stack": ["Angular 18", "TypeScript", "Docker"],
                        "repository_url": ""  # No proporcionado
                    },
                    {
                        "type": ApplicationType.BACKEND,
                        "tech_stack": [".NET Core 8", "C#", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-cargosfuncionales-be"
                    }
                ]
            },
            {
                "id": "segmentacion",
                "name": "Segmentación Académica",
                "description": "Sistema de segmentación y análisis académico",
                "owner_team": "Equipo Académico",
                "components": [
                    {
                        "type": ApplicationType.FRONTEND,
                        "tech_stack": ["Angular 18", "TypeScript", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-segmentacionacademica-spa"
                    },
                    {
                        "type": ApplicationType.BACKEND,
                        "tech_stack": [".NET Core 8", "C#", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-segmentacionacademica-be"
                    }
                ]
            },
            {
                "id": "convenios-integraciones",
                "name": "Convenios e Integraciones",
                "description": "Sistema de gestión de convenios e integraciones BO",
                "owner_team": "Equipo Académico",
                "components": [
                    {
                        "type": ApplicationType.FRONTEND,
                        "tech_stack": ["Angular 18", "TypeScript", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-conveniosintegracionbo-spa"
                    },
                    {
                        "type": ApplicationType.BACKEND,
                        "tech_stack": [".NET Core 8", "C#", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-conveniosintegracionbo-spa"  # Mismo repo que front (revisar)
                    }
                ]
            },
            {
                "id": "trabajadores-erp",
                "name": "Trabajadores ERP",
                "description": "Sistema de gestión de trabajadores ERP académico",
                "owner_team": "Equipo Académico",
                "components": [
                    {
                        "type": ApplicationType.FRONTEND,
                        "tech_stack": ["Angular 18", "TypeScript", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-usuarioserpacademico-spa"
                    },
                    {
                        "type": ApplicationType.BACKEND,
                        "tech_stack": [".NET Core 8", "C#", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-usuarioserpacademico-bff"
                    }
                ]
            },
            {
                "id": "credenciales-academicas",
                "name": "Credenciales Académicas",
                "description": "Sistema de gestión de credenciales académicas",
                "owner_team": "Equipo Académico",
                "components": [
                    {
                        "type": ApplicationType.FRONTEND,
                        "tech_stack": ["Angular 18", "TypeScript", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-credencialesacademicas-spa"
                    },
                    {
                        "type": ApplicationType.BACKEND,
                        "tech_stack": [".NET Core 8", "C#", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-credencialesacademicas-be"
                    }
                ]
            }
        ]

    def create_applications(self):
        """Crea las aplicaciones reales con sus componentes."""
        print("🏗️  Creando aplicaciones reales de UNIR...")
        
        created_apps = []
        
        for app_config in self.real_apps:
            print(f"   📱 Creando aplicación: {app_config['name']}")
            
            # Crear componentes (frontend y backend)
            for component in app_config['components']:
                component_id = f"{app_config['id']}-{component['type'].value}"
                
                application = Application(
                    id=component_id,
                    name=f"{app_config['name']} ({component['type'].value.capitalize()})",
                    type=component['type'],
                    description=f"{app_config['description']} - Componente {component['type'].value}",
                    repository_url=component['repository_url'],
                    tech_stack=component['tech_stack'],
                    owner_team=app_config['owner_team'],
                    dependencies=[],
                    health_check_url=f"https://{app_config['id']}-{component['type'].value}.unir.net/health",
                    created_at=datetime.now()
                )
                
                app_id = self.db.create_application(application)
                created_apps.append((app_id, application))
                print(f"      ✅ {component['type'].value.capitalize()}: {component_id}")
        
        print(f"✅ Creadas {len(created_apps)} aplicaciones componente")
        return created_apps

    def create_versions_for_apps(self, applications: list):
        """Crea versiones realistas para cada aplicación."""
        print("\n🔖 Creando versiones para aplicaciones...")
        
        version_patterns = {
            ApplicationType.FRONTEND: [
                "18.1.0", "18.1.1", "18.1.2", "18.2.0", "18.2.1", "19.0.0-beta.1"
            ],
            ApplicationType.BACKEND: [
                "8.1.0", "8.1.1", "8.1.2", "8.2.0", "8.2.1", "8.3.0-rc.1"
            ]
        }
        
        created_versions = []
        
        for app_id, app in applications:
            versions = version_patterns.get(app.type, ["1.0.0", "1.1.0", "1.2.0"])
            
            for i, version_num in enumerate(versions[:4]):  # Crear 4 versiones por app
                version = Version(
                    version=version_num,
                    application_id=app.id,
                    branch="main" if not "beta" in version_num and not "rc" in version_num else "develop",
                    commit_hash=self._generate_commit_hash(),
                    build_number=f"build-{random.randint(1000, 9999)}",
                    created_at=datetime.now() - timedelta(days=30-i*5),
                    features=self._generate_features(app.type),
                    bug_fixes=self._generate_bug_fixes(),
                    breaking_changes=[] if i < 2 else ["Actualización de Angular", "Cambios en API"],
                    commits=[],
                    artifacts={}
                )
                
                version_id = self.db.create_version(version)
                created_versions.append((version_id, version))
        
        print(f"✅ Creadas {len(created_versions)} versiones")
        return created_versions

    def create_deployments_for_versions(self, versions: list):
        """Crea despliegues para las versiones."""
        print("\n🚀 Creando despliegues...")
        
        environments = [Environment.DEVELOPMENT, Environment.PREPRODUCTION, Environment.PRODUCTION]
        deployers = ["jesus.rodriguez", "admin.sistemas", "devops.team"]
        
        created_deployments = []
        
        for version_id, version in versions:
            # Solo hacer despliegues para las versiones estables (no beta/rc)
            if "beta" not in version.version and "rc" not in version.version:
                for env in environments:
                    # No todas las versiones van a prod
                    if env == Environment.PRODUCTION and random.random() > 0.6:
                        continue
                    
                    deployment = Deployment(
                        id=f"deploy-{uuid.uuid4().hex[:8]}",
                        application_id=version.application_id,
                        environment=env,
                        version=version,
                        status=random.choice([DeploymentStatus.SUCCESS, DeploymentStatus.SUCCESS, DeploymentStatus.FAILED]),
                        deployed_by=random.choice(deployers),
                        deployed_at=datetime.now() - timedelta(days=random.randint(1, 20)),
                        notes=f"Despliegue de {version.version} en {env.value}",
                        config_changes={},
                        migration_scripts=[]
                    )
                    
                    deployment_id = self.db.create_deployment(deployment)
                    created_deployments.append((deployment_id, deployment))
        
        print(f"✅ Creados {len(created_deployments)} despliegues")
        return created_deployments

    def _generate_commit_hash(self):
        """Genera un hash de commit realista."""
        return ''.join(random.choices('abcdef0123456789', k=40))

    def _generate_features(self, app_type: ApplicationType):
        """Genera características según el tipo de aplicación."""
        frontend_features = [
            "Nuevo componente de filtros",
            "Mejoras en UX/UI",
            "Optimización de rendimiento",
            "Nuevas validaciones de formulario",
            "Integración con nueva API"
        ]
        
        backend_features = [
            "Nueva API de consultas",
            "Optimización de base de datos",
            "Implementación de caché",
            "Nuevos endpoints REST",
            "Mejoras en seguridad"
        ]
        
        if app_type == ApplicationType.FRONTEND:
            return random.sample(frontend_features, k=random.randint(1, 3))
        else:
            return random.sample(backend_features, k=random.randint(1, 3))

    def _generate_bug_fixes(self):
        """Genera correcciones de bugs comunes."""
        bugs = [
            "Corrección en validación de formularios",
            "Fix en manejo de errores",
            "Solución a problema de memoria",
            "Corrección en filtros de búsqueda",
            "Fix en autenticación"
        ]
        return random.sample(bugs, k=random.randint(0, 2))

    def generate_all_data(self):
        """Genera todos los datos de las aplicaciones reales."""
        print("🎯 Generando datos completos para aplicaciones reales de UNIR\n")
        
        # Limpiar datos existentes
        print("🧹 Limpiando base de datos...")
        self.db._clear_all_data()
        
        # Crear aplicaciones
        applications = self.create_applications()
        
        # Crear versiones
        versions = self.create_versions_for_apps(applications)
        
        # Crear despliegues
        deployments = self.create_deployments_for_versions(versions)
        
        print(f"\n🎉 ¡Datos generados exitosamente!")
        print(f"   📱 Aplicaciones: {len(applications)}")
        print(f"   🔖 Versiones: {len(versions)}")
        print(f"   🚀 Despliegues: {len(deployments)}")
        
        return {
            "applications": len(applications),
            "versions": len(versions),
            "deployments": len(deployments)
        }


def main():
    """Función principal para generar los datos."""
    try:
        # Crear directorio de datos si no existe
        data_dir = Path(__file__).parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        
        # Inicializar base de datos
        db_path = data_dir / "deployments.db"
        db_manager = DatabaseManager(str(db_path))
        
        # Inicializar base de datos
        db_manager.initialize_database()
        
        # Generar datos
        generator = RealAppsDataGenerator(db_manager)
        stats = generator.generate_all_data()
        
        print(f"\n✅ Base de datos actualizada en: {db_path}")
        print("🌐 Ejecuta el dashboard para ver los nuevos datos:")
        print("   streamlit run src/frontend/multi_app_dashboard.py")
        
    except Exception as e:
        print(f"❌ Error generando datos: {e}")
        return False
    
    return True


if __name__ == "__main__":
    main()