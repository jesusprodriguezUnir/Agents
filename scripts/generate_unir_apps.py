"""
Generador de datos reales para aplicaciones de UNIR.
Versión simplificada que usa SQLite directamente.
"""

import sqlite3
import uuid
from datetime import datetime, timedelta
import random
from pathlib import Path


class SimpleDatabaseManager:
    """Gestor simplificado de base de datos."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa las tablas de la base de datos."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de aplicaciones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                description TEXT,
                repository_url TEXT,
                tech_stack TEXT,
                owner_team TEXT,
                health_check_url TEXT,
                created_at TEXT
            )
        """)
        
        # Tabla de versiones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT NOT NULL,
                application_id TEXT NOT NULL,
                branch TEXT,
                commit_hash TEXT,
                build_number TEXT,
                created_at TEXT,
                features TEXT,
                bug_fixes TEXT,
                FOREIGN KEY (application_id) REFERENCES applications (id)
            )
        """)
        
        # Tabla de despliegues
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deployments (
                id TEXT PRIMARY KEY,
                application_id TEXT NOT NULL,
                environment TEXT NOT NULL,
                version_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                deployed_by TEXT,
                deployed_at TEXT,
                notes TEXT,
                FOREIGN KEY (application_id) REFERENCES applications (id),
                FOREIGN KEY (version_id) REFERENCES versions (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def clear_data(self):
        """Limpia todos los datos."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM deployments")
        cursor.execute("DELETE FROM versions")
        cursor.execute("DELETE FROM applications")
        
        conn.commit()
        conn.close()
    
    def create_application(self, app_data):
        """Crea una aplicación."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO applications (id, name, type, description, repository_url, tech_stack, owner_team, health_check_url, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            app_data['id'],
            app_data['name'],
            app_data['type'],
            app_data['description'],
            app_data['repository_url'],
            ','.join(app_data['tech_stack']),
            app_data['owner_team'],
            app_data['health_check_url'],
            app_data['created_at']
        ))
        
        conn.commit()
        conn.close()
        return app_data['id']
    
    def create_version(self, version_data):
        """Crea una versión."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO versions (version, application_id, branch, commit_hash, build_number, created_at, features, bug_fixes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            version_data['version'],
            version_data['application_id'],
            version_data['branch'],
            version_data['commit_hash'],
            version_data['build_number'],
            version_data['created_at'],
            ','.join(version_data['features']),
            ','.join(version_data['bug_fixes'])
        ))
        
        conn.commit()
        version_id = cursor.lastrowid
        conn.close()
        return version_id
    
    def create_deployment(self, deploy_data):
        """Crea un despliegue."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO deployments (id, application_id, environment, version_id, status, deployed_by, deployed_at, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            deploy_data['id'],
            deploy_data['application_id'],
            deploy_data['environment'],
            deploy_data['version_id'],
            deploy_data['status'],
            deploy_data['deployed_by'],
            deploy_data['deployed_at'],
            deploy_data['notes']
        ))
        
        conn.commit()
        conn.close()
        return deploy_data['id']


class RealAppsGenerator:
    """Generador de datos para aplicaciones reales de UNIR."""
    
    def __init__(self, db_manager):
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
                        "type": "frontend",
                        "tech_stack": ["Angular 18", "TypeScript", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/core-expedienteserp-spa"
                    },
                    {
                        "type": "backend",
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
                        "type": "frontend",
                        "tech_stack": ["Angular 18", "TypeScript", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-expediciontitulos-spa"
                    },
                    {
                        "type": "backend",
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
                        "type": "frontend",
                        "tech_stack": ["Angular 18", "TypeScript", "Docker"],
                        "repository_url": ""
                    },
                    {
                        "type": "backend",
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
                        "type": "frontend",
                        "tech_stack": ["Angular 18", "TypeScript", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-segmentacionacademica-spa"
                    },
                    {
                        "type": "backend",
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
                        "type": "frontend",
                        "tech_stack": ["Angular 18", "TypeScript", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-conveniosintegracionbo-spa"
                    },
                    {
                        "type": "backend",
                        "tech_stack": [".NET Core 8", "C#", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-conveniosintegracionbo-spa"
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
                        "type": "frontend",
                        "tech_stack": ["Angular 18", "TypeScript", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-usuarioserpacademico-spa"
                    },
                    {
                        "type": "backend",
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
                        "type": "frontend",
                        "tech_stack": ["Angular 18", "TypeScript", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-credencialesacademicas-spa"
                    },
                    {
                        "type": "backend",
                        "tech_stack": [".NET Core 8", "C#", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-credencialesacademicas-be"
                    }
                ]
            }
        ]
    
    def create_applications(self):
        """Crea las aplicaciones con sus componentes."""
        print("🏗️  Creando aplicaciones reales de UNIR...")
        
        created_apps = []
        
        for app_config in self.real_apps:
            print(f"   📱 Creando aplicación: {app_config['name']}")
            
            for component in app_config['components']:
                component_id = f"{app_config['id']}-{component['type']}"
                
                app_data = {
                    'id': component_id,
                    'name': f"{app_config['name']} ({component['type'].capitalize()})",
                    'type': component['type'],
                    'description': f"{app_config['description']} - Componente {component['type']}",
                    'repository_url': component['repository_url'],
                    'tech_stack': component['tech_stack'],
                    'owner_team': app_config['owner_team'],
                    'health_check_url': f"https://{app_config['id']}-{component['type']}.unir.net/health",
                    'created_at': datetime.now().isoformat()
                }
                
                app_id = self.db.create_application(app_data)
                created_apps.append(app_id)
                print(f"      ✅ {component['type'].capitalize()}: {component_id}")
        
        return created_apps
    
    def create_versions(self, app_ids):
        """Crea versiones para las aplicaciones."""
        print(f"\n🔖 Creando versiones para {len(app_ids)} aplicaciones...")
        
        frontend_versions = ["18.1.0", "18.1.1", "18.2.0", "19.0.0-beta.1"]
        backend_versions = ["8.1.0", "8.1.1", "8.2.0", "8.3.0-rc.1"]
        
        created_versions = []
        
        for app_id in app_ids:
            versions = frontend_versions if 'frontend' in app_id else backend_versions
            
            for i, version_num in enumerate(versions[:3]):  # 3 versiones por app
                version_data = {
                    'version': version_num,
                    'application_id': app_id,
                    'branch': 'main' if 'beta' not in version_num else 'develop',
                    'commit_hash': self._generate_commit_hash(),
                    'build_number': f"build-{random.randint(1000, 9999)}",
                    'created_at': (datetime.now() - timedelta(days=20-i*5)).isoformat(),
                    'features': self._get_features(app_id),
                    'bug_fixes': self._get_bug_fixes()
                }
                
                version_id = self.db.create_version(version_data)
                created_versions.append((version_id, version_data))
        
        print(f"✅ Creadas {len(created_versions)} versiones")
        return created_versions
    
    def create_deployments(self, versions):
        """Crea despliegues para las versiones."""
        print(f"\n🚀 Creando despliegues para {len(versions)} versiones...")
        
        environments = ['dev', 'pre', 'prod']
        deployers = ['jesus.rodriguez', 'admin.sistemas', 'devops.team']
        statuses = ['success', 'success', 'success', 'failed']  # Más éxitos que fallos
        
        created_deployments = []
        
        for version_id, version_data in versions:
            # Solo versiones estables van a prod
            envs_to_deploy = environments if 'beta' not in version_data['version'] else environments[:2]
            
            for env in envs_to_deploy:
                if env == 'prod' and random.random() > 0.7:  # No todo va a prod
                    continue
                
                deploy_data = {
                    'id': f"deploy-{uuid.uuid4().hex[:8]}",
                    'application_id': version_data['application_id'],
                    'environment': env,
                    'version_id': version_id,  # Usar version_id en lugar de version
                    'status': random.choice(statuses),
                    'deployed_by': random.choice(deployers),
                    'deployed_at': (datetime.now() - timedelta(days=random.randint(1, 15))).isoformat(),
                    'notes': f"Despliegue de {version_data['version']} en {env}"
                }
                
                deploy_id = self.db.create_deployment(deploy_data)
                created_deployments.append(deploy_id)
        
        print(f"✅ Creados {len(created_deployments)} despliegues")
        return created_deployments
    
    def _generate_commit_hash(self):
        """Genera un hash de commit."""
        return ''.join(random.choices('abcdef0123456789', k=40))
    
    def _get_features(self, app_id):
        """Obtiene características según el tipo de app."""
        if 'frontend' in app_id:
            return random.sample([
                "Nuevo componente de filtros",
                "Mejoras en UX/UI",
                "Optimización de rendimiento",
                "Nuevas validaciones",
                "Integración con API"
            ], k=2)
        else:
            return random.sample([
                "Nueva API de consultas",
                "Optimización de BD",
                "Implementación de caché",
                "Nuevos endpoints",
                "Mejoras en seguridad"
            ], k=2)
    
    def _get_bug_fixes(self):
        """Obtiene correcciones de bugs."""
        return random.sample([
            "Fix en validación",
            "Corrección de errores",
            "Solución problema memoria",
            "Fix en filtros",
            "Corrección autenticación"
        ], k=random.randint(0, 2))
    
    def generate_all(self):
        """Genera todos los datos."""
        print("🎯 Generando datos completos para aplicaciones reales de UNIR\n")
        
        # Limpiar datos
        print("🧹 Limpiando base de datos...")
        self.db.clear_data()
        
        # Crear aplicaciones
        app_ids = self.create_applications()
        
        # Crear versiones
        versions = self.create_versions(app_ids)
        
        # Crear despliegues
        deployments = self.create_deployments(versions)
        
        print(f"\n🎉 ¡Datos generados exitosamente!")
        print(f"   📱 Aplicaciones: {len(app_ids)}")
        print(f"   🔖 Versiones: {len(versions)}")
        print(f"   🚀 Despliegues: {len(deployments)}")


def main():
    """Función principal."""
    try:
        # Crear directorio de datos
        data_dir = Path(__file__).parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        
        # Inicializar BD
        db_path = data_dir / "deployments.db"
        db_manager = SimpleDatabaseManager(str(db_path))
        
        # Generar datos
        generator = RealAppsGenerator(db_manager)
        generator.generate_all()
        
        print(f"\n✅ Base de datos actualizada en: {db_path}")
        print("🌐 Reinicia el dashboard para ver los nuevos datos")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()