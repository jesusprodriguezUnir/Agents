"""
Generador de datos de ejemplo para el sistema multi-organización.

Crea datos de prueba para probar el nuevo esquema con múltiples organizaciones.
"""

import sqlite3
from datetime import datetime, timedelta
import random
from uuid import uuid4

DATABASE_PATH = "data/deployments.db"

def get_db_connection():
    """Obtiene una conexión a la base de datos."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def generate_deployment_data():
    """Genera datos de ejemplo de despliegues para el nuevo esquema."""
    
    print("🚀 Generando datos de ejemplo para sistema multi-organización...")
    
    with get_db_connection() as conn:
        # Obtener organizaciones disponibles
        organizations = conn.execute("SELECT id, name FROM organizations").fetchall()
        print(f"📊 Organizaciones encontradas: {len(organizations)}")
        
        # Obtener entornos por organización
        environments = {}
        for org in organizations:
            env_list = conn.execute(
                "SELECT id, name FROM environments WHERE organization_id = ?", 
                (org['id'],)
            ).fetchall()
            environments[org['id']] = env_list
            print(f"   • {org['name']}: {len(env_list)} entornos")
        
        # Obtener versiones disponibles
        versions = conn.execute("""
            SELECT v.id, v.version, ac.name as component_name, a.name as app_name
            FROM versions v
            JOIN application_components ac ON v.component_id = ac.id
            JOIN applications a ON ac.application_id = a.id
        """).fetchall()
        
        print(f"📦 Versiones disponibles: {len(versions)}")
        
        # Usuarios de ejemplo
        users = [
            "admin@proeduca.com",
            "developer@proeduca.com", 
            "devops@proeduca.com",
            "admin@villanueva.com",
            "developer@villanueva.com"
        ]
        
        # Estados de despliegue
        statuses = ['success', 'failed']
        status_weights = [0.8, 0.2]  # 80% éxito, 20% fallo
        
        # Generar despliegues para cada organización
        total_deployments = 0
        
        for org in organizations:
            org_environments = environments[org['id']]
            
            if not org_environments:
                print(f"⚠️  No hay entornos para {org['name']}, saltando...")
                continue
            
            # Generar entre 20-50 despliegues por organización
            num_deployments = random.randint(20, 50)
            
            for _ in range(num_deployments):
                # Seleccionar datos aleatorios
                env = random.choice(org_environments)
                version = random.choice(versions)
                user = random.choice(users)
                status = random.choices(statuses, weights=status_weights)[0]
                
                # Fecha aleatoria en los últimos 60 días
                days_ago = random.randint(0, 60)
                hours_ago = random.randint(0, 23)
                minutes_ago = random.randint(0, 59)
                
                deployment_date = datetime.now() - timedelta(
                    days=days_ago, 
                    hours=hours_ago, 
                    minutes=minutes_ago
                )
                
                # Notas de ejemplo
                notes_examples = [
                    "Despliegue automático",
                    "Despliegue manual por hotfix",
                    "Release programado",
                    "Rollback por incidencia",
                    "Actualización de seguridad",
                    "Nueva funcionalidad",
                    "Corrección de bugs"
                ]
                notes = random.choice(notes_examples)
                
                # Insertar despliegue
                deployment_id = str(uuid4())
                
                try:
                    conn.execute("""
                        INSERT INTO deployments (
                            id, environment_id, version_id, status, 
                            deployed_by, deployed_at, notes
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        deployment_id,
                        env['id'],
                        version['id'],
                        status,
                        user,
                        deployment_date.isoformat(),
                        notes
                    ))
                    total_deployments += 1
                    
                except sqlite3.IntegrityError as e:
                    # Si hay error de integridad, continuar con el siguiente
                    continue
            
            print(f"   ✅ {org['name']}: datos generados")
        
        conn.commit()
        print(f"✅ Generación completada: {total_deployments} nuevos despliegues creados")
        
        # Generar URLs de ejemplo adicionales
        generate_example_urls(conn)

def generate_example_urls(conn):
    """Genera URLs de ejemplo para los entornos."""
    
    print("🌐 Generando URLs de ejemplo...")
    
    # Obtener componentes y entornos
    components = conn.execute("""
        SELECT ac.id, ac.name as component_name, a.name as app_name
        FROM application_components ac
        JOIN applications a ON ac.application_id = a.id
    """).fetchall()
    
    environments = conn.execute("""
        SELECT e.id, e.name as env_name, o.name as org_name
        FROM environments e
        JOIN organizations o ON e.organization_id = o.id
    """).fetchall()
    
    # Tipos de URL
    url_types = ['frontend', 'backend', 'api', 'admin']
    
    # Dominios base por organización
    domains = {
        'proeduca': 'proeduca.com',
        'villanueva': 'villanueva.edu'
    }
    
    urls_created = 0
    
    for env in environments:
        domain = domains.get(env['org_name'], 'example.com')
        
        # Crear algunas URLs para este entorno
        for component in random.sample(list(components), min(3, len(components))):
            for url_type in random.sample(url_types, random.randint(1, 2)):
                
                # Generar URL
                if url_type == 'frontend':
                    url = f"https://{env['env_name']}.{domain}/{component['app_name'].lower()}"
                elif url_type == 'backend':
                    url = f"https://api-{env['env_name']}.{domain}/{component['component_name'].lower()}"
                elif url_type == 'api':
                    url = f"https://api.{env['env_name']}.{domain}/v1/{component['component_name'].lower()}"
                else:  # admin
                    url = f"https://admin-{env['env_name']}.{domain}/{component['app_name'].lower()}"
                
                # Verificar si ya existe
                existing = conn.execute("""
                    SELECT id FROM environment_urls 
                    WHERE environment_id = ? AND component_id = ? AND url_type = ?
                """, (env['id'], component['id'], url_type)).fetchone()
                
                if not existing:
                    conn.execute("""
                        INSERT INTO environment_urls (environment_id, component_id, url, url_type, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (env['id'], component['id'], url, url_type, datetime.now().isoformat()))
                    urls_created += 1
    
    conn.commit()
    print(f"✅ URLs creadas: {urls_created}")

def show_summary():
    """Muestra un resumen de los datos generados."""
    
    print("\n📊 RESUMEN DE DATOS GENERADOS")
    print("=" * 50)
    
    with get_db_connection() as conn:
        # Estadísticas por organización
        stats = conn.execute("""
            SELECT 
                o.name as organization,
                COUNT(DISTINCT e.id) as environments,
                COUNT(DISTINCT d.id) as deployments,
                COUNT(DISTINCT eu.id) as urls
            FROM organizations o
            LEFT JOIN environments e ON o.id = e.organization_id
            LEFT JOIN deployments d ON e.id = d.environment_id
            LEFT JOIN environment_urls eu ON e.id = eu.environment_id
            GROUP BY o.id, o.name
            ORDER BY o.name
        """).fetchall()
        
        for stat in stats:
            print(f"🏢 {stat['organization']}:")
            print(f"   • Entornos: {stat['environments']}")
            print(f"   • Despliegues: {stat['deployments']}")
            print(f"   • URLs: {stat['urls']}")
            print()
        
        # Estadísticas generales
        total_deployments = conn.execute("SELECT COUNT(*) as count FROM deployments").fetchone()['count']
        total_urls = conn.execute("SELECT COUNT(*) as count FROM environment_urls").fetchone()['count']
        
        print(f"📈 TOTALES:")
        print(f"   • Despliegues totales: {total_deployments}")
        print(f"   • URLs totales: {total_urls}")

def main():
    """Función principal."""
    
    print("🎯 GENERADOR DE DATOS MULTI-ORGANIZACIÓN")
    print("=" * 50)
    
    try:
        # Generar datos
        generate_deployment_data()
        
        # Mostrar resumen
        show_summary()
        
        print("\n✅ ¡Generación de datos completada exitosamente!")
        print("🚀 Puedes ejecutar el dashboard con: python run_multi_org_dashboard.py")
        
    except Exception as e:
        print(f"❌ Error durante la generación: {e}")
        raise

if __name__ == "__main__":
    main()