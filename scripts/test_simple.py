"""
Script simple para probar la base de datos multi-aplicación.
"""

import sqlite3
import json
from datetime import datetime

def test_database():
    """Prueba directa de la base de datos."""
    print("🧪 Probando base de datos multi-aplicación...")
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect("data/deployments.db")
        conn.row_factory = sqlite3.Row
        
        # Probar aplicaciones
        print("\n📱 Aplicaciones registradas:")
        apps = conn.execute("SELECT * FROM applications ORDER BY name").fetchall()
        for app in apps:
            print(f"   • {app['name']} ({app['type']}) - {app['owner_team']}")
            
            # Contar versiones y despliegues
            version_count = conn.execute(
                "SELECT COUNT(*) FROM versions WHERE application_id = ?", 
                (app['id'],)
            ).fetchone()[0]
            
            deployment_count = conn.execute(
                "SELECT COUNT(*) FROM deployments WHERE application_id = ?", 
                (app['id'],)
            ).fetchone()[0]
            
            print(f"     └─ {version_count} versiones, {deployment_count} despliegues")
        
        # Probar versiones
        print(f"\n🏷️ Total de versiones: {len(conn.execute('SELECT * FROM versions').fetchall())}")
        print("   Últimas 5 versiones:")
        latest_versions = conn.execute("""
            SELECT v.version, a.name as app_name, v.created_at 
            FROM versions v
            JOIN applications a ON v.application_id = a.id
            ORDER BY v.created_at DESC
            LIMIT 5
        """).fetchall()
        
        for version in latest_versions:
            created_at = datetime.fromisoformat(version['created_at']).strftime('%Y-%m-%d')
            print(f"   • {version['app_name']} v{version['version']} ({created_at})")
        
        # Probar despliegues por entorno
        print(f"\n🚀 Total de despliegues: {len(conn.execute('SELECT * FROM deployments').fetchall())}")
        
        for env in ['dev', 'pre', 'prod']:
            env_deployments = conn.execute(
                "SELECT COUNT(*) FROM deployments WHERE environment = ?", 
                (env,)
            ).fetchone()[0]
            
            success_deployments = conn.execute(
                "SELECT COUNT(*) FROM deployments WHERE environment = ? AND status = 'success'", 
                (env, )
            ).fetchone()[0]
            
            print(f"   • {env.upper()}: {env_deployments} despliegues ({success_deployments} exitosos)")
        
        # Estado actual por entorno
        print(f"\n🌍 Estado actual por entorno:")
        
        for env in ['dev', 'pre', 'prod']:
            print(f"\n   {env.upper()}:")
            
            # Últimos despliegues por aplicación en este entorno
            latest_deployments = conn.execute("""
                SELECT DISTINCT
                    a.name as app_name,
                    v.version,
                    d.status,
                    d.deployed_at,
                    d.deployed_by
                FROM deployments d
                JOIN versions v ON d.version_id = v.id
                JOIN applications a ON d.application_id = a.id
                WHERE d.environment = ?
                AND d.id IN (
                    SELECT d2.id 
                    FROM deployments d2 
                    WHERE d2.application_id = d.application_id 
                    AND d2.environment = ?
                    ORDER BY d2.deployed_at DESC 
                    LIMIT 1
                )
                ORDER BY a.name
            """, (env, env)).fetchall()
            
            for deployment in latest_deployments:
                status_icon = {
                    'success': '✅',
                    'failed': '❌',
                    'in_progress': '🔄',
                    'rollback': '↩️'
                }.get(deployment['status'], '❓')
                
                deployed_at = datetime.fromisoformat(deployment['deployed_at']).strftime('%m-%d %H:%M')
                print(f"     {status_icon} {deployment['app_name']} v{deployment['version']} ({deployed_at} by {deployment['deployed_by']})")
        
        conn.close()
        
        print("\n✨ ¡Prueba de base de datos completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()


def test_real_scenario():
    """Simula un escenario real de despliegues."""
    print("\n🎯 Simulando escenario de despliegues...")
    
    try:
        conn = sqlite3.connect("data/deployments.db")
        
        # Obtener una aplicación para crear un nuevo despliegue
        app = conn.execute("SELECT * FROM applications LIMIT 1").fetchone()
        if not app:
            print("❌ No hay aplicaciones disponibles")
            return
        
        app_id = app[0]  # id
        app_name = app[1]  # name
        
        # Obtener una versión de esa aplicación
        version = conn.execute(
            "SELECT * FROM versions WHERE application_id = ? ORDER BY created_at DESC LIMIT 1",
            (app_id,)
        ).fetchone()
        
        if not version:
            print(f"❌ No hay versiones para {app_name}")
            return
        
        version_id = version[0]  # id
        version_number = version[1]  # version
        
        # Simular creación de un nuevo despliegue
        import uuid
        deployment_id = f"deploy-{uuid.uuid4().hex[:8]}"
        
        conn.execute("""
            INSERT INTO deployments 
            (id, application_id, environment, version_id, status, deployed_by, deployed_at, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            deployment_id,
            app_id,
            "dev",
            version_id,
            "success",
            "test_user",
            datetime.now().isoformat(),
            "Despliegue de prueba generado por script"
        ))
        
        conn.commit()
        
        print(f"✅ Nuevo despliegue creado:")
        print(f"   ID: {deployment_id}")
        print(f"   Aplicación: {app_name}")
        print(f"   Versión: {version_number}")
        print(f"   Entorno: dev")
        print(f"   Estado: success")
        
        # Verificar el nuevo despliegue
        new_deployment = conn.execute("""
            SELECT d.*, a.name as app_name, v.version
            FROM deployments d
            JOIN applications a ON d.application_id = a.id
            JOIN versions v ON d.version_id = v.id
            WHERE d.id = ?
        """, (deployment_id,)).fetchone()
        
        if new_deployment:
            print(f"✅ Despliegue verificado en la base de datos")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error en escenario: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Función principal."""
    print("🚀 Iniciando pruebas del sistema multi-aplicación")
    print("=" * 60)
    
    test_database()
    test_real_scenario()
    
    print("\n" + "=" * 60)
    print("🎉 ¡Todas las pruebas completadas!")
    print("🌐 Dashboard disponible en: http://localhost:8502")


if __name__ == "__main__":
    main()