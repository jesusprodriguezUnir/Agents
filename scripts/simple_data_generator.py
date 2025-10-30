"""
Script simple para generar datos de ejemplo y probar la nueva estructura.
"""

import os
import sys
from pathlib import Path

# Añadir el src al path
script_dir = Path(__file__).parent
project_dir = script_dir.parent
src_dir = project_dir / "src"
sys.path.insert(0, str(src_dir))

# Ahora importar con rutas absolutas
os.chdir(str(project_dir))

try:
    import sqlite3
    from datetime import datetime, timedelta
    import uuid
    import random
    import json
    
    # Crear base de datos manualmente
    db_path = "data/deployments.db"
    os.makedirs("data", exist_ok=True)
    
    print("🚀 Generando datos de ejemplo con nueva estructura...")
    
    # Crear conexión
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Crear tablas
    print("📊 Creando estructura de base de datos...")
    
    # Tabla aplicaciones
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            description TEXT DEFAULT '',
            repository_url TEXT DEFAULT '',
            tech_stack TEXT DEFAULT '[]',
            owner_team TEXT DEFAULT '',
            dependencies TEXT DEFAULT '[]',
            health_check_url TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabla versiones
    conn.execute("""
        CREATE TABLE IF NOT EXISTS versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT NOT NULL,
            application_id TEXT NOT NULL,
            branch TEXT NOT NULL,
            commit_hash TEXT NOT NULL,
            build_number TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            commits TEXT DEFAULT '[]',
            features TEXT DEFAULT '[]',
            bug_fixes TEXT DEFAULT '[]',
            breaking_changes TEXT DEFAULT '[]',
            artifacts TEXT DEFAULT '{}',
            FOREIGN KEY (application_id) REFERENCES applications (id),
            UNIQUE(application_id, version)
        )
    """)
    
    # Tabla despliegues
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
            config_changes TEXT DEFAULT '{}',
            migration_scripts TEXT DEFAULT '[]',
            FOREIGN KEY (application_id) REFERENCES applications (id),
            FOREIGN KEY (version_id) REFERENCES versions (id)
        )
    """)
    
    # Limpiar datos existentes
    print("🧹 Limpiando datos anteriores...")
    conn.execute("DELETE FROM deployments")
    conn.execute("DELETE FROM versions")
    conn.execute("DELETE FROM applications")
    
    # Crear aplicaciones de ejemplo
    print("📱 Creando aplicaciones...")
    applications = [
        {
            "id": "app-01",
            "name": "E-Commerce Frontend",
            "type": "frontend",
            "description": "Aplicación frontend Angular para e-commerce",
            "repository_url": "https://github.com/company/ecommerce-frontend",
            "tech_stack": json.dumps(["Angular 16", "TypeScript", "SCSS", "Angular Material"]),
            "owner_team": "Frontend Team",
            "health_check_url": "https://app-01.company.com/health"
        },
        {
            "id": "app-02",
            "name": "E-Commerce API",
            "type": "backend",
            "description": "API principal del sistema e-commerce",
            "repository_url": "https://github.com/company/ecommerce-api",
            "tech_stack": json.dumps([".NET Core 7", "C#", "Entity Framework", "SQL Server"]),
            "owner_team": "Backend Team",
            "health_check_url": "https://app-02.company.com/health"
        },
        {
            "id": "app-03",
            "name": "Payment Service",
            "type": "microservice",
            "description": "Microservicio de procesamiento de pagos",
            "repository_url": "https://github.com/company/payment-service",
            "tech_stack": json.dumps([".NET Core 7", "C#", "Redis", "PostgreSQL"]),
            "owner_team": "Payments Team",
            "health_check_url": "https://app-03.company.com/health"
        },
        {
            "id": "app-04",
            "name": "User Management API",
            "type": "microservice",
            "description": "Servicio de gestión de usuarios y autenticación",
            "repository_url": "https://github.com/company/user-management",
            "tech_stack": json.dumps([".NET Core 7", "C#", "Identity Server", "SQL Server"]),
            "owner_team": "Identity Team",
            "health_check_url": "https://app-04.company.com/health"
        },
        {
            "id": "app-05",
            "name": "Admin Dashboard",
            "type": "frontend",
            "description": "Panel de administración del sistema",
            "repository_url": "https://github.com/company/admin-dashboard",
            "tech_stack": json.dumps(["Angular 16", "TypeScript", "PrimeNG", "Charts.js"]),
            "owner_team": "Admin Team",
            "health_check_url": "https://app-05.company.com/health"
        }
    ]
    
    for app in applications:
        conn.execute("""
            INSERT INTO applications 
            (id, name, type, description, repository_url, tech_stack, owner_team, health_check_url, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            app["id"], app["name"], app["type"], app["description"],
            app["repository_url"], app["tech_stack"], app["owner_team"],
            app["health_check_url"], datetime.now().isoformat()
        ))
    
    print(f"✅ Creadas {len(applications)} aplicaciones")
    
    # Crear versiones para cada aplicación
    print("🏷️ Creando versiones...")
    version_count = 0
    
    features_samples = [
        "Nueva funcionalidad de búsqueda avanzada",
        "Integración con gateway de pagos",
        "Sistema de notificaciones push",
        "Mejoras en la interfaz de usuario",
        "Optimización de rendimiento"
    ]
    
    bug_fixes_samples = [
        "Corrección de memory leak en procesamiento",
        "Fix de timeout en consultas de base de datos",
        "Resolución de problemas de CORS",
        "Corrección de vulnerabilidad de seguridad",
        "Fix de race condition en pedidos"
    ]
    
    for app in applications:
        app_id = app["id"]
        
        # Crear 5-7 versiones por aplicación
        num_versions = random.randint(5, 7)
        base_date = datetime.now() - timedelta(days=90)
        
        used_versions = set()  # Para evitar duplicados
        
        for i in range(num_versions):
            # Generar número de versión único
            while True:
                major = 2 if i >= num_versions - 2 else 1
                minor = random.randint(0, 5)
                patch = random.randint(0, 10)
                version_number = f"{major}.{minor}.{patch}"
                
                if version_number not in used_versions:
                    used_versions.add(version_number)
                    break
            
            version_date = base_date + timedelta(days=i * random.randint(5, 15))
            
            conn.execute("""
                INSERT INTO versions 
                (version, application_id, branch, commit_hash, build_number, created_at,
                 features, bug_fixes, breaking_changes, artifacts)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                version_number, app_id, 
                "main" if i >= num_versions - 3 else random.choice(["develop", "release/1.x"]),
                f"{uuid.uuid4().hex[:8]}",
                f"build-{1000 + i * 10 + random.randint(1, 9)}",
                version_date.isoformat(),
                json.dumps(random.sample(features_samples, random.randint(1, 2))),
                json.dumps(random.sample(bug_fixes_samples, random.randint(0, 2))),
                json.dumps([]),
                json.dumps({
                    "docker_image": f"company/{app_id}:{version_number}",
                    "build_url": f"https://build.company.com/{app_id}/{1000 + i * 10}"
                })
            ))
            version_count += 1
    
    print(f"✅ Creadas {version_count} versiones")
    
    # Crear despliegues
    print("🚀 Creando despliegues...")
    deployment_count = 0
    
    environments = ["dev", "pre", "prod"]
    users = ["juan.perez", "maria.garcia", "carlos.lopez", "ana.martinez"]
    
    for app in applications:
        app_id = app["id"]
        
        # Obtener versiones de esta aplicación
        app_versions = conn.execute(
            "SELECT * FROM versions WHERE application_id = ? ORDER BY created_at",
            (app_id,)
        ).fetchall()
        
        for env in environments:
            # Número de despliegues por entorno
            num_deployments = {
                "dev": random.randint(8, 12),
                "pre": random.randint(5, 8),
                "prod": random.randint(3, 6)
            }[env]
            
            # Seleccionar versiones para desplegar
            selected_versions = random.sample(app_versions, min(num_deployments, len(app_versions)))
            
            for version_row in selected_versions:
                version_id = version_row[0]  # id de la versión
                version_date = datetime.fromisoformat(version_row[6])  # created_at
                
                deployment_date = version_date + timedelta(
                    hours=random.randint(1, 24),
                    minutes=random.randint(0, 59)
                )
                
                # Duración del despliegue
                duration_minutes = random.randint(5, 30)
                started_at = deployment_date
                completed_at = started_at + timedelta(minutes=duration_minutes)
                
                # Estado del despliegue (mayoría exitosos)
                status = random.choices(
                    ["success", "failed", "rollback", "in_progress"],
                    weights=[0.8, 0.1, 0.05, 0.05]
                )[0]
                
                # Ajustar tiempos según el estado
                if status == "in_progress":
                    completed_at = None
                elif status == "failed":
                    completed_at = started_at + timedelta(minutes=random.randint(2, 10))
                
                notes = {
                    "success": "Despliegue completado sin incidencias",
                    "failed": "Error en la migración de base de datos",
                    "in_progress": "Despliegue en progreso...",
                    "rollback": "Rollback ejecutado correctamente"
                }[status]
                
                conn.execute("""
                    INSERT INTO deployments 
                    (id, application_id, environment, version_id, status, deployed_by,
                     deployed_at, started_at, completed_at, notes, config_changes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"deploy-{uuid.uuid4().hex[:8]}",
                    app_id, env, version_id, status, random.choice(users),
                    deployment_date.isoformat(),
                    started_at.isoformat(),
                    completed_at.isoformat() if completed_at else None,
                    notes,
                    json.dumps({
                        "database_timeout": "30s",
                        "max_connections": "100",
                        "log_level": random.choice(["INFO", "DEBUG", "WARN"])
                    })
                ))
                deployment_count += 1
    
    print(f"✅ Creados {deployment_count} despliegues")
    
    # Confirmar todos los cambios
    conn.commit()
    
    # Mostrar estadísticas finales
    print("\n📊 Estadísticas finales:")
    app_count = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    version_count = conn.execute("SELECT COUNT(*) FROM versions").fetchone()[0]
    deployment_count = conn.execute("SELECT COUNT(*) FROM deployments").fetchone()[0]
    
    print(f"   Aplicaciones: {app_count}")
    print(f"   Versiones: {version_count}")
    print(f"   Despliegues: {deployment_count}")
    
    # Mostrar ejemplo de aplicaciones creadas
    print("\n🎯 Aplicaciones creadas:")
    apps = conn.execute("SELECT id, name, type FROM applications").fetchall()
    for app_id, name, app_type in apps:
        version_count = conn.execute(
            "SELECT COUNT(*) FROM versions WHERE application_id = ?", (app_id,)
        ).fetchone()[0]
        deployment_count = conn.execute(
            "SELECT COUNT(*) FROM deployments WHERE application_id = ?", (app_id,)
        ).fetchone()[0]
        print(f"   {app_id}: {name} ({app_type}) - {version_count} versiones, {deployment_count} despliegues")
    
    conn.close()
    
    print("\n✨ ¡Datos de ejemplo generados exitosamente!")
    print(f"💾 Base de datos creada en: {db_path}")
    print("🎉 El sistema está listo para usar con la nueva estructura multi-aplicación")
    
except Exception as e:
    print(f"❌ Error al generar datos: {e}")
    import traceback
    traceback.print_exc()