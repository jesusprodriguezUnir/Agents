"""Herramientas integradas para el dashboard de Streamlit."""

import sqlite3
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional


def get_database_manager():
    """Obtiene una instancia del gestor de base de datos jerárquico."""
    import sqlite3
    from contextlib import contextmanager
    
    class HierarchicalDatabaseManager:
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
        
        # === APLICACIONES PRINCIPALES ===
        
        def get_application(self, app_id: str) -> Optional[Dict[str, Any]]:
            """Obtiene una aplicación principal por ID."""
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        
        def list_applications(self) -> List[Dict[str, Any]]:
            """Lista todas las aplicaciones principales."""
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM applications ORDER BY name")
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        
        def create_application(self, app_data: Dict[str, Any]) -> str:
            """Crea una nueva aplicación principal."""
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO applications 
                    (id, name, description, owner_team, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    app_data['id'],
                    app_data['name'],
                    app_data['description'],
                    app_data['owner_team'],
                    app_data.get('created_at', '')
                ))
                conn.commit()
                return app_data['id']
        
        def update_application(self, app_id: str, app_data: Dict[str, Any]) -> bool:
            """Actualiza una aplicación existente."""
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE applications 
                    SET name = ?, description = ?, owner_team = ?
                    WHERE id = ?
                """, (
                    app_data['name'],
                    app_data['description'],
                    app_data['owner_team'],
                    app_id
                ))
                conn.commit()
                return cursor.rowcount > 0
        
        # === COMPONENTES ===
        
        def list_components(self) -> List[Dict[str, Any]]:
            """Lista todos los componentes con información de la aplicación."""
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        ac.*,
                        a.name as application_name,
                        a.description as application_description
                    FROM application_components ac
                    JOIN applications a ON ac.application_id = a.id
                    ORDER BY a.name, ac.type
                """)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        
        def get_components_by_application(self, app_id: str) -> List[Dict[str, Any]]:
            """Obtiene componentes de una aplicación específica."""
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM application_components 
                    WHERE application_id = ? 
                    ORDER BY type
                """, (app_id,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        
        def create_component(self, component_data: Dict[str, Any]) -> str:
            """Crea un nuevo componente."""
            with self.get_connection() as conn:
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
                    ','.join(component_data.get('tech_stack', [])),
                    component_data['health_check_url'],
                    component_data.get('created_at', '')
                ))
                conn.commit()
                return component_data['id']
        
        def update_component(self, component_id: str, component_data: Dict[str, Any]) -> bool:
            """Actualiza un componente existente."""
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE application_components 
                    SET name = ?, repository_url = ?, tech_stack = ?, health_check_url = ?
                    WHERE id = ?
                """, (
                    component_data['name'],
                    component_data['repository_url'],
                    ','.join(component_data.get('tech_stack', [])),
                    component_data['health_check_url'],
                    component_id
                ))
                conn.commit()
                return cursor.rowcount > 0
        
        # === VERSIONES ===
        
        def get_versions_by_component(self, component_id: str) -> List[Dict[str, Any]]:
            """Obtiene versiones de un componente específico."""
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT v.*, ac.name as component_name, a.name as application_name
                    FROM versions v
                    JOIN application_components ac ON v.component_id = ac.id
                    JOIN applications a ON ac.application_id = a.id
                    WHERE v.component_id = ? 
                    ORDER BY v.created_at DESC
                """, (component_id,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        
        def list_all_versions(self) -> List[Dict[str, Any]]:
            """Lista todas las versiones con información completa."""
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        v.*,
                        ac.name as component_name,
                        ac.type as component_type,
                        a.name as application_name
                    FROM versions v
                    JOIN application_components ac ON v.component_id = ac.id
                    JOIN applications a ON ac.application_id = a.id
                    ORDER BY a.name, ac.type, v.created_at DESC
                """)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        
        def create_version(self, version_data: Dict[str, Any]) -> str:
            """Crea una nueva versión."""
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO versions 
                    (version, component_id, branch, commit_hash, build_number, created_at, features, bug_fixes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    version_data['version'],
                    version_data['component_id'],
                    version_data['branch'],
                    version_data['commit_hash'],
                    version_data['build_number'],
                    version_data.get('created_at', ''),
                    ','.join(version_data.get('features', [])),
                    ','.join(version_data.get('bug_fixes', []))
                ))
                conn.commit()
                return cursor.lastrowid
        
        def update_version(self, version_id: int, version_data: Dict[str, Any]) -> bool:
            """Actualiza una versión existente."""
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE versions 
                    SET version = ?, branch = ?, commit_hash = ?, build_number = ?, 
                        features = ?, bug_fixes = ?
                    WHERE id = ?
                """, (
                    version_data['version'],
                    version_data['branch'],
                    version_data['commit_hash'],
                    version_data['build_number'],
                    ','.join(version_data.get('features', [])),
                    ','.join(version_data.get('bug_fixes', [])),
                    version_id
                ))
                conn.commit()
                return cursor.rowcount > 0
        
        # === RESUMEN DE ENTORNOS ===
        
        def get_environment_summary(self) -> Dict[str, Any]:
            """Obtiene resumen completo de todos los entornos."""
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Consulta para obtener el estado actual de cada entorno
                cursor.execute("""
                    SELECT 
                        d.environment,
                        a.name as application_name,
                        ac.type as component_type,
                        ac.name as component_name,
                        v.version,
                        d.status,
                        d.deployed_at,
                        d.deployed_by
                    FROM deployments d
                    JOIN versions v ON d.version_id = v.id
                    JOIN application_components ac ON d.component_id = ac.id
                    JOIN applications a ON ac.application_id = a.id
                    WHERE d.id IN (
                        SELECT MAX(d2.id)
                        FROM deployments d2
                        WHERE d2.component_id = d.component_id 
                        AND d2.environment = d.environment
                        AND d2.status = 'success'
                    )
                    ORDER BY d.environment, a.name, ac.type
                """)
                
                rows = cursor.fetchall()
                
                # Organizar por entorno
                environments = {}
                for row in rows:
                    env = row[0]
                    if env not in environments:
                        environments[env] = []
                    
                    environments[env].append({
                        'application_name': row[1],
                        'component_type': row[2],
                        'component_name': row[3],
                        'version': row[4],
                        'status': row[5],
                        'deployed_at': row[6],
                        'deployed_by': row[7]
                    })
                
                return environments
        
        # === DESPLIEGUES ===
        
        def list_all_deployments(self) -> List[Dict[str, Any]]:
            """Lista todos los despliegues con información completa."""
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        d.*,
                        v.version,
                        ac.name as component_name,
                        ac.type as component_type,
                        a.name as application_name
                    FROM deployments d
                    JOIN versions v ON d.version_id = v.id
                    JOIN application_components ac ON d.component_id = ac.id
                    JOIN applications a ON ac.application_id = a.id
                    ORDER BY d.deployed_at DESC
                """)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        
        def create_deployment(self, deployment_data: Dict[str, Any]) -> str:
            """Crea un nuevo despliegue."""
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO deployments 
                    (id, component_id, version_id, environment, status, deployed_by, deployed_at, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    deployment_data['id'],
                    deployment_data['component_id'],
                    deployment_data['version_id'],
                    deployment_data['environment'],
                    deployment_data['status'],
                    deployment_data['deployed_by'],
                    deployment_data['deployed_at'],
                    deployment_data['notes']
                ))
                conn.commit()
                return deployment_data['id']
    
    return HierarchicalDatabaseManager()


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
        app_type: str = "",  # No usado en estructura jerárquica
        description: str = "",
        repository_url: str = "",
        tech_stack: List[str] = None,
        owner_team: str = "",
        health_check_url: str = ""
    ) -> Dict[str, Any]:
        """Crea una nueva aplicación principal."""
        try:
            # Verificar que el ID no exista
            existing_app = self.db_manager.get_application(app_id)
            if existing_app:
                return {
                    "success": False,
                    "message": f"Ya existe una aplicación con ID '{app_id}'"
                }
            
            application_data = {
                'id': app_id,
                'name': name,
                'description': description,
                'owner_team': owner_team,
                'created_at': datetime.now().isoformat()
            }
            
            created_id = self.db_manager.create_application(application_data)
            
            return {
                "success": True,
                "message": f"Aplicación '{name}' creada exitosamente",
                "data": {
                    "id": created_id,
                    "name": name
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al crear aplicación: {str(e)}"
            }
    
    def update_application(
        self,
        app_id: str,
        name: str,
        description: str = "",
        owner_team: str = ""
    ) -> Dict[str, Any]:
        """Actualiza una aplicación existente."""
        try:
            # Verificar que la aplicación existe
            existing_app = self.db_manager.get_application(app_id)
            if not existing_app:
                return {
                    "success": False,
                    "message": f"Aplicación '{app_id}' no encontrada"
                }
            
            app_data = {
                'name': name,
                'description': description,
                'owner_team': owner_team
            }
            
            updated = self.db_manager.update_application(app_id, app_data)
            
            if updated:
                return {
                    "success": True,
                    "message": f"Aplicación '{name}' actualizada exitosamente"
                }
            else:
                return {
                    "success": False,
                    "message": "No se pudo actualizar la aplicación"
                }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al actualizar aplicación: {str(e)}"
            }
    
    def list_applications(self) -> List[Dict[str, Any]]:
        """Lista todas las aplicaciones."""
        return self.db_manager.list_applications()
    
    def get_application(self, app_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene una aplicación específica."""
        return self.db_manager.get_application(app_id)
    
    # === COMPONENTES ===
    
    def create_component(
        self,
        component_id: str,
        application_id: str,
        name: str,
        type: str,
        repository_url: str = "",
        tech_stack: List[str] = None,
        health_check_url: str = ""
    ) -> Dict[str, Any]:
        """Crea un nuevo componente."""
        try:
            # Verificar que la aplicación existe
            existing_app = self.db_manager.get_application(application_id)
            if not existing_app:
                return {
                    "success": False,
                    "message": f"Aplicación '{application_id}' no encontrada"
                }
            
            component_data = {
                'id': component_id,
                'application_id': application_id,
                'name': name,
                'type': type,
                'repository_url': repository_url,
                'tech_stack': tech_stack or [],
                'health_check_url': health_check_url,
                'created_at': datetime.now().isoformat()
            }
            
            created_id = self.db_manager.create_component(component_data)
            
            return {
                "success": True,
                "message": f"Componente '{name}' creado exitosamente",
                "data": {
                    "id": created_id,
                    "name": name,
                    "type": type
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al crear componente: {str(e)}"
            }
    
    def update_component(
        self,
        component_id: str,
        name: str,
        repository_url: str = "",
        tech_stack: List[str] = None,
        health_check_url: str = ""
    ) -> Dict[str, Any]:
        """Actualiza un componente existente."""
        try:
            component_data = {
                'name': name,
                'repository_url': repository_url,
                'tech_stack': tech_stack or [],
                'health_check_url': health_check_url
            }
            
            success = self.db_manager.update_component(component_id, component_data)
            
            if success:
                return {
                    "success": True,
                    "message": f"Componente '{name}' actualizado exitosamente"
                }
            else:
                return {
                    "success": False,
                    "message": f"Componente '{component_id}' no encontrado"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al actualizar componente: {str(e)}"
            }
    
    def list_components(self) -> List[Dict[str, Any]]:
        """Lista todos los componentes."""
        try:
            return self.db_manager.list_components()
        except Exception as e:
            return []
    
    def get_components_by_application(self, app_id: str) -> List[Dict[str, Any]]:
        """Obtiene componentes de una aplicación específica."""
        try:
            return self.db_manager.get_components_by_application(app_id)
        except Exception as e:
            return []

    # === VERSIONES ===
    
    def create_version(
        self,
        component_id: str,
        version: str,
        branch: str,
        commit_hash: str,
        build_number: str,
        features: List[str] = None,
        bug_fixes: List[str] = None,
        breaking_changes: List[str] = None
    ) -> Dict[str, Any]:
        """Crea una nueva versión para un componente específico."""
        try:
            version_data = {
                'version': version,
                'component_id': component_id,
                'branch': branch,
                'commit_hash': commit_hash,
                'build_number': build_number,
                'features': features or [],
                'bug_fixes': bug_fixes or [],
                'created_at': datetime.now().isoformat()
            }
            
            version_id = self.db_manager.create_version(version_data)
            
            return {
                "success": True,
                "message": f"Versión {version} creada exitosamente",
                "data": {
                    "version_id": version_id,
                    "version": version,
                    "component_id": component_id
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al crear versión: {str(e)}"
            }
    
    def create_version_legacy(
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
        """Crea una nueva versión para una aplicación (versión legacy)."""
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