"""
Generador de estructura jerárquica para aplicaciones de UNIR.
Aplicaciones principales con componentes (frontend/backend) separados.
"""

import sqlite3
import uuid
from datetime import datetime, timedelta
import random
from pathlib import Path


class HierarchicalDatabaseManager:
    """Gestor de BD con estructura jerárquica de aplicaciones."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa las tablas con estructura jerárquica."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Eliminar tablas existentes para recrear con nueva estructura
        cursor.execute("DROP TABLE IF EXISTS deployments")
        cursor.execute("DROP TABLE IF EXISTS versions")
        cursor.execute("DROP TABLE IF EXISTS application_components")
        cursor.execute("DROP TABLE IF EXISTS applications")
        
        # Tabla principal de aplicaciones
        cursor.execute("""
            CREATE TABLE applications (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                owner_team TEXT,
                created_at TEXT
            )
        """)
        
        # Tabla de componentes (frontend/backend)
        cursor.execute("""
            CREATE TABLE application_components (
                id TEXT PRIMARY KEY,
                application_id TEXT NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('frontend', 'backend')),
                repository_url TEXT,
                tech_stack TEXT,
                health_check_url TEXT,
                created_at TEXT,
                FOREIGN KEY (application_id) REFERENCES applications (id)
            )
        """)
        
        # Tabla de versiones (vinculada a componentes)
        cursor.execute("""
            CREATE TABLE versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT NOT NULL,
                component_id TEXT NOT NULL,
                branch TEXT,
                commit_hash TEXT,
                build_number TEXT,
                created_at TEXT,
                features TEXT,
                bug_fixes TEXT,
                FOREIGN KEY (component_id) REFERENCES application_components (id)
            )
        """)
        
        # Tabla de despliegues (vinculada a versiones)
        cursor.execute("""
            CREATE TABLE deployments (
                id TEXT PRIMARY KEY,
                component_id TEXT NOT NULL,
                version_id INTEGER NOT NULL,
                environment TEXT NOT NULL,
                status TEXT NOT NULL,
                deployed_by TEXT,
                deployed_at TEXT,
                notes TEXT,
                FOREIGN KEY (component_id) REFERENCES application_components (id),
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
        cursor.execute("DELETE FROM application_components")
        cursor.execute("DELETE FROM applications")
        
        conn.commit()
        conn.close()
    
    def create_application(self, app_data):
        """Crea una aplicación principal."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO applications (id, name, description, owner_team, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            app_data['id'],
            app_data['name'],
            app_data['description'],
            app_data['owner_team'],
            app_data['created_at']
        ))
        
        conn.commit()
        conn.close()
        return app_data['id']
    
    def create_component(self, component_data):
        """Crea un componente de aplicación."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO application_components 
            (id, application_id, name, type, repository_url, tech_stack, health_check_url, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            component_data['id'],
            component_data['application_id'],
            component_data['name'],
            component_data['type'],
            component_data['repository_url'],
            ','.join(component_data['tech_stack']),
            component_data['health_check_url'],
            component_data['created_at']
        ))
        
        conn.commit()
        conn.close()
        return component_data['id']
    
    def create_version(self, version_data):
        """Crea una versión para un componente."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO versions (version, component_id, branch, commit_hash, build_number, created_at, features, bug_fixes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            version_data['version'],
            version_data['component_id'],
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
            INSERT INTO deployments (id, component_id, version_id, environment, status, deployed_by, deployed_at, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            deploy_data['id'],
            deploy_data['component_id'],
            deploy_data['version_id'],
            deploy_data['environment'],
            deploy_data['status'],
            deploy_data['deployed_by'],
            deploy_data['deployed_at'],
            deploy_data['notes']
        ))
        
        conn.commit()
        conn.close()
        return deploy_data['id']


class HierarchicalAppsGenerator:
    """Generador con estructura jerárquica de aplicaciones UNIR."""
    
    def __init__(self, db_manager):
        self.db = db_manager
        
        # Aplicaciones principales de UNIR
        self.applications = [
            {
                "id": "expedientes",
                "name": "Expedientes ERP",
                "description": "Sistema de gestión de expedientes académicos",
                "owner_team": "Equipo Académico",
                "components": {
                    "frontend": {
                        "tech_stack": ["Angular 18", "TypeScript", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/core-expedienteserp-spa"
                    },
                    "backend": {
                        "tech_stack": [".NET Core 8", "C#", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/ExpedientesErpNetCore"
                    }
                }
            },
            {
                "id": "expedicion-titulos",
                "name": "Expedición de Títulos",
                "description": "Sistema para expedición y gestión de títulos académicos",
                "owner_team": "Equipo Académico",
                "components": {
                    "frontend": {
                        "tech_stack": ["Angular 18", "TypeScript", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-expediciontitulos-spa"
                    },
                    "backend": {
                        "tech_stack": [".NET Core 8", "C#", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-expediciontitulos-be"
                    }
                }
            },
            {
                "id": "cargos-funcionales",
                "name": "Cargos Funcionales",
                "description": "Sistema de gestión de cargos funcionales académicos",
                "owner_team": "Equipo Académico",
                "components": {
                    "frontend": {
                        "tech_stack": ["Angular 18", "TypeScript", "Docker"],
                        "repository_url": ""  # No proporcionado
                    },
                    "backend": {
                        "tech_stack": [".NET Core 8", "C#", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-cargosfuncionales-be"
                    }
                }
            },
            {
                "id": "segmentacion",
                "name": "Segmentación Académica",
                "description": "Sistema de segmentación y análisis académico",
                "owner_team": "Equipo Académico",
                "components": {
                    "frontend": {
                        "tech_stack": ["Angular 18", "TypeScript", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-segmentacionacademica-spa"
                    },
                    "backend": {
                        "tech_stack": [".NET Core 8", "C#", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-segmentacionacademica-be"
                    }
                }
            },
            {
                "id": "convenios-integraciones",
                "name": "Convenios e Integraciones",
                "description": "Sistema de gestión de convenios e integraciones BO",
                "owner_team": "Equipo Académico",
                "components": {
                    "frontend": {
                        "tech_stack": ["Angular 18", "TypeScript", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-conveniosintegracionbo-spa"
                    },
                    "backend": {
                        "tech_stack": [".NET Core 8", "C#", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-conveniosintegracionbo-spa"
                    }
                }
            },
            {
                "id": "trabajadores-erp",
                "name": "Trabajadores ERP",
                "description": "Sistema de gestión de trabajadores ERP académico",
                "owner_team": "Equipo Académico",
                "components": {
                    "frontend": {
                        "tech_stack": ["Angular 18", "TypeScript", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-usuarioserpacademico-spa"
                    },
                    "backend": {
                        "tech_stack": [".NET Core 8", "C#", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-usuarioserpacademico-bff"
                    }
                }
            },
            {
                "id": "credenciales-academicas",
                "name": "Credenciales Académicas",
                "description": "Sistema de gestión de credenciales académicas",
                "owner_team": "Equipo Académico",
                "components": {
                    "frontend": {
                        "tech_stack": ["Angular 18", "TypeScript", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-credencialesacademicas-spa"
                    },
                    "backend": {
                        "tech_stack": [".NET Core 8", "C#", "Docker"],
                        "repository_url": "https://dev.azure.com/unirnet/UNIR/_git/aca-credencialesacademicas-be"
                    }
                }
            }
        ]
    
    def create_applications_and_components(self):
        """Crea aplicaciones principales y sus componentes."""
        print("🏗️  Creando aplicaciones y componentes...")
        
        created_components = []
        
        for app_config in self.applications:
            print(f"   📱 Aplicación principal: {app_config['name']}")
            
            # Crear aplicación principal
            app_data = {
                'id': app_config['id'],
                'name': app_config['name'],
                'description': app_config['description'],
                'owner_team': app_config['owner_team'],
                'created_at': datetime.now().isoformat()
            }
            
            app_id = self.db.create_application(app_data)
            print(f"      ✅ Aplicación creada: {app_id}")
            
            # Crear componentes
            for comp_type, comp_data in app_config['components'].items():
                component_id = f"{app_config['id']}-{comp_type}"
                
                component = {
                    'id': component_id,
                    'application_id': app_id,
                    'name': f"{app_config['name']} ({comp_type.capitalize()})",
                    'type': comp_type,
                    'repository_url': comp_data['repository_url'],
                    'tech_stack': comp_data['tech_stack'],
                    'health_check_url': f"https://{app_config['id']}-{comp_type}.unir.net/health",
                    'created_at': datetime.now().isoformat()
                }
                
                comp_id = self.db.create_component(component)
                created_components.append(comp_id)
                print(f"      📦 Componente: {comp_type} -> {comp_id}")
        
        return created_components
    
    def create_versions(self, component_ids):
        """Crea versiones para los componentes."""
        print(f"\n🔖 Creando versiones para {len(component_ids)} componentes...")
        
        frontend_versions = ["18.1.0", "18.1.1", "18.2.0"]
        backend_versions = ["8.1.0", "8.1.1", "8.2.0"]
        
        created_versions = []
        
        for comp_id in component_ids:
            versions = frontend_versions if 'frontend' in comp_id else backend_versions
            
            for i, version_num in enumerate(versions):
                version_data = {
                    'version': version_num,
                    'component_id': comp_id,
                    'branch': 'main',
                    'commit_hash': self._generate_commit_hash(),
                    'build_number': f"build-{random.randint(1000, 9999)}",
                    'created_at': (datetime.now() - timedelta(days=15-i*3)).isoformat(),
                    'features': self._get_features(comp_id),
                    'bug_fixes': self._get_bug_fixes()
                }
                
                version_id = self.db.create_version(version_data)
                created_versions.append((version_id, version_data))
        
        print(f"✅ Creadas {len(created_versions)} versiones")
        return created_versions
    
    def create_deployments(self, versions):
        """Crea despliegues para las versiones."""
        print(f"\n🚀 Creando despliegues...")
        
        environments = ['dev', 'pre', 'prod']
        deployers = ['jesus.rodriguez', 'admin.sistemas', 'devops.team']
        statuses = ['success', 'success', 'success', 'failed']
        
        created_deployments = []
        
        for version_id, version_data in versions:
            for env in environments:
                if env == 'prod' and random.random() > 0.7:
                    continue
                
                deploy_data = {
                    'id': f"deploy-{uuid.uuid4().hex[:8]}",
                    'component_id': version_data['component_id'],
                    'version_id': version_id,
                    'environment': env,
                    'status': random.choice(statuses),
                    'deployed_by': random.choice(deployers),
                    'deployed_at': (datetime.now() - timedelta(days=random.randint(1, 10))).isoformat(),
                    'notes': f"Despliegue de {version_data['version']} en {env}"
                }
                
                deploy_id = self.db.create_deployment(deploy_data)
                created_deployments.append(deploy_id)
        
        print(f"✅ Creados {len(created_deployments)} despliegues")
        return created_deployments
    
    def _generate_commit_hash(self):
        """Genera un hash de commit."""
        return ''.join(random.choices('abcdef0123456789', k=40))
    
    def _get_features(self, comp_id):
        """Obtiene características según el componente."""
        if 'frontend' in comp_id:
            return random.sample([
                "Nuevo componente de filtros",
                "Mejoras en UX/UI",
                "Optimización de rendimiento",
                "Nuevas validaciones"
            ], k=2)
        else:
            return random.sample([
                "Nueva API de consultas",
                "Optimización de BD",
                "Implementación de caché",
                "Mejoras en seguridad"
            ], k=2)
    
    def _get_bug_fixes(self):
        """Obtiene correcciones de bugs."""
        return random.sample([
            "Fix en validación",
            "Corrección de errores",
            "Solución problema memoria"
        ], k=random.randint(0, 2))
    
    def generate_all(self):
        """Genera toda la estructura jerárquica."""
        print("🎯 Generando estructura jerárquica para aplicaciones UNIR\n")
        
        # Limpiar datos
        print("🧹 Limpiando base de datos...")
        self.db.clear_data()
        
        # Crear aplicaciones y componentes
        components = self.create_applications_and_components()
        
        # Crear versiones
        versions = self.create_versions(components)
        
        # Crear despliegues
        deployments = self.create_deployments(versions)
        
        print(f"\n🎉 ¡Estructura jerárquica creada!")
        print(f"   🏢 Aplicaciones: {len(self.applications)}")
        print(f"   📦 Componentes: {len(components)}")
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
        db_manager = HierarchicalDatabaseManager(str(db_path))
        
        # Generar datos
        generator = HierarchicalAppsGenerator(db_manager)
        generator.generate_all()
        
        print(f"\n✅ Base de datos jerárquica creada en: {db_path}")
        print("📊 Estructura:")
        print("   └── applications (tabla principal)")
        print("       └── application_components (frontend/backend)")
        print("           └── versions")
        print("               └── deployments")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()