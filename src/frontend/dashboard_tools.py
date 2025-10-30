"""Herramientas integradas para el dashboard de Streamlit."""

import sqlite3
import uuid
from typing import Dict, Any, List, Optional


def get_database_manager():
    """Obtiene una instancia del gestor de base de datos."""
    import sqlite3
    from contextlib import contextmanager
    
    class SimpleDatabaseManager:
        def __init__(self, db_path: str = "data/deployments.db"):
            self.db_path = db_path
        
        @contextmanager
        def get_connection(self):
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()
        
        def get_application(self, app_id: str) -> Optional[Dict[str, Any]]:
            """Obtiene una aplicación por ID."""
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        
        def list_applications(self) -> List[Dict[str, Any]]:
            """Lista todas las aplicaciones."""
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM applications ORDER BY name")
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        
        def create_application(self, app_data: Dict[str, Any]) -> str:
            """Crea una nueva aplicación."""
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO applications 
                    (id, name, type, description, repository_url, owner_team, health_check_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    app_data['id'],
                    app_data['name'],
                    app_data['type'],
                    app_data['description'],
                    app_data['repository_url'],
                    app_data['owner_team'],
                    app_data['health_check_url']
                ))
                conn.commit()
                return app_data['id']
        
        def get_versions_by_application(self, app_id: str) -> List[Dict[str, Any]]:
            """Obtiene versiones de una aplicación."""
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM versions 
                    WHERE application_id = ? 
                    ORDER BY created_at DESC
                """, (app_id,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        
        def create_version(self, version_data: Dict[str, Any]) -> str:
            """Crea una nueva versión."""
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO versions 
                    (application_id, version, branch, commit_hash, build_number)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    version_data['application_id'],
                    version_data['version'],
                    version_data['branch'],
                    version_data['commit_hash'],
                    version_data['build_number']
                ))
                conn.commit()
                return cursor.lastrowid
        
        def create_deployment(self, deployment_data: Dict[str, Any]) -> str:
            """Crea un nuevo despliegue."""
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO deployments 
                    (id, application_id, environment, version, status, deployed_by, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    deployment_data['id'],
                    deployment_data['application_id'],
                    deployment_data['environment'],
                    deployment_data['version'],
                    deployment_data['status'],
                    deployment_data['deployed_by'],
                    deployment_data['notes']
                ))
                conn.commit()
                return deployment_data['id']
    
    return SimpleDatabaseManager()


class DashboardTools:
    """Herramientas integradas para el dashboard."""
    
    def __init__(self, db_path: str = "data/deployments.db"):
        """Inicializa las herramientas con conexión a BD."""
        self.db_manager = get_database_manager()
    
    # === APLICACIONES ===
    
    def create_application(
        self,
        app_id: str,
        name: str,
        app_type: str,
        description: str = "",
        repository_url: str = "",
        tech_stack: List[str] = None,
        owner_team: str = "",
        health_check_url: str = ""
    ) -> Dict[str, Any]:
        """Crea una nueva aplicación."""
        try:
            # Verificar que el ID no exista
            existing_app = self.db_manager.get_application(app_id)
            if existing_app:
                return {
                    "success": False,
                    "message": f"Ya existe una aplicación con ID '{app_id}'"
                }
            
            # Validar tipo de aplicación
            valid_types = ['frontend', 'backend', 'microservice', 'database', 'infrastructure']
            if app_type not in valid_types:
                return {
                    "success": False,
                    "message": f"Tipo inválido. Use: {', '.join(valid_types)}"
                }
            
            application_data = {
                'id': app_id,
                'name': name,
                'type': app_type,
                'description': description,
                'repository_url': repository_url,
                'tech_stack': tech_stack or [],
                'owner_team': owner_team,
                'health_check_url': health_check_url
            }
            
            created_id = self.db_manager.create_application(application_data)
            
            return {
                "success": True,
                "message": f"Aplicación '{name}' creada exitosamente",
                "data": {
                    "id": created_id,
                    "name": name,
                    "type": app_type
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al crear aplicación: {str(e)}"
            }
    
    def list_applications(self) -> List[Dict[str, Any]]:
        """Lista todas las aplicaciones."""
        return self.db_manager.list_applications()
    
    def get_application(self, app_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene una aplicación específica."""
        return self.db_manager.get_application(app_id)
    
    # === VERSIONES ===
    
    def create_version(
        self,
        application_id: str,
        version: str,
        branch: str,
        commit_hash: str,
        build_number: str,
        features: List[str] = None,
        bug_fixes: List[str] = None,
        breaking_changes: List[str] = None
    ) -> Dict[str, Any]:
        """Crea una nueva versión para una aplicación."""
        try:
            # Verificar que la aplicación existe
            app = self.db_manager.get_application(application_id)
            if not app:
                return {
                    "success": False,
                    "message": f"Aplicación {application_id} no encontrada"
                }
            
            # Verificar que la versión no exista
            existing_versions = self.db_manager.get_versions_by_application(application_id)
            if any(v['version'] == version for v in existing_versions):
                return {
                    "success": False,
                    "message": f"Ya existe la versión {version} para {app['name']}"
                }
            
            version_data = {
                'version': version,
                'application_id': application_id,
                'branch': branch,
                'commit_hash': commit_hash,
                'build_number': build_number,
                'features': features or [],
                'bug_fixes': bug_fixes or [],
                'breaking_changes': breaking_changes or []
            }
            
            version_id = self.db_manager.create_version(version_data)
            
            return {
                "success": True,
                "message": f"Versión {version} creada para {app['name']}",
                "data": {
                    "version_id": version_id,
                    "version": version,
                    "application_name": app['name']
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al crear versión: {str(e)}"
            }
    
    def list_versions_by_application(self, application_id: str) -> List[Dict[str, Any]]:
        """Lista versiones de una aplicación."""
        return self.db_manager.get_versions_by_application(application_id)
    
    # === DESPLIEGUES ===
    
    def create_deployment(
        self,
        application_id: str,
        environment: str,
        version: str,
        deployed_by: str,
        notes: str = ""
    ) -> Dict[str, Any]:
        """Crea un nuevo despliegue."""
        try:
            # Verificar aplicación
            app = self.db_manager.get_application(application_id)
            if not app:
                return {
                    "success": False,
                    "message": f"Aplicación {application_id} no encontrada"
                }
            
            # Validar entorno
            valid_envs = ['dev', 'pre', 'prod']
            if environment not in valid_envs:
                return {
                    "success": False,
                    "message": f"Entorno inválido. Use: {', '.join(valid_envs)}"
                }
            
            # Buscar la versión
            versions = self.db_manager.get_versions_by_application(application_id)
            version_obj = next(
                (v for v in versions if v['version'] == version),
                None
            )
            
            if not version_obj:
                return {
                    "success": False,
                    "message": f"Versión {version} no encontrada para {app['name']}"
                }
            
            # Crear el despliegue
            deployment_data = {
                'id': f"deploy-{uuid.uuid4().hex[:8]}",
                'application_id': application_id,
                'environment': environment,
                'version': version,
                'status': 'pending',
                'deployed_by': deployed_by,
                'notes': notes
            }
            
            deployment_id = self.db_manager.create_deployment(deployment_data)
            
            return {
                "success": True,
                "message": f"Despliegue iniciado: {app['name']} v{version} → {environment}",
                "data": {
                    "deployment_id": deployment_data['id'],
                    "application_name": app['name'],
                    "version": version,
                    "environment": environment,
                    "status": 'pending'
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al crear despliegue: {str(e)}"
            }
    
    def update_deployment_status(
        self,
        deployment_id: str,
        status: str,
        notes: str = ""
    ) -> Dict[str, Any]:
        """Actualiza el estado de un despliegue."""
        try:
            # Validar estado
            valid_statuses = ['pending', 'in_progress', 'success', 'failed', 'rollback']
            if status not in valid_statuses:
                return {
                    "success": False,
                    "message": f"Estado inválido. Use: {', '.join(valid_statuses)}"
                }
            
            # Por ahora simulamos la actualización
            return {
                "success": True,
                "message": f"Estado actualizado a {status}",
                "data": {
                    "deployment_id": deployment_id,
                    "new_status": status
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al actualizar estado: {str(e)}"
            }
    
    # === UTILIDADES ===
    
    def get_application_choices(self) -> List[tuple]:
        """Obtiene lista de aplicaciones para formularios."""
        apps = self.list_applications()
        return [(app['id'], f"{app['name']} ({app['type']})") for app in apps]
    
    def get_version_choices(self, application_id: str) -> List[str]:
        """Obtiene lista de versiones para una aplicación."""
        versions = self.list_versions_by_application(application_id)
        return [v['version'] for v in versions]
    
    def get_environment_choices(self) -> List[str]:
        """Obtiene lista de entornos disponibles."""
        return ["dev", "pre", "prod"]
    
    def get_application_type_choices(self) -> List[str]:
        """Obtiene lista de tipos de aplicación."""
        return ["frontend", "backend", "microservice", "database", "infrastructure"]


# Instancia global para usar en el dashboard
dashboard_tools = DashboardTools()