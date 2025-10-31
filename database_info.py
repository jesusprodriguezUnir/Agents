#!/usr/bin/env python3
"""
Script para mostrar información detallada de la base de datos del MCP Deployment Manager.
Utiliza las consultas documentadas en docs/SQL_QUERIES.md
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

def connect_to_database():
    """Conectar a la base de datos del proyecto."""
    db_path = Path("data/deployments.db")
    if not db_path.exists():
        print("❌ Error: Base de datos no encontrada en data/deployments.db")
        print("💡 Ejecuta: python scripts/generate_hierarchical_apps.py")
        return None
    
    return sqlite3.connect(str(db_path))

def show_database_summary():
    """Mostrar resumen general de la base de datos."""
    conn = connect_to_database()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    print("🗄️  RESUMEN DE BASE DE DATOS - MCP Deployment Manager")
    print("=" * 60)
    
    # Estadísticas generales
    cursor.execute("""
        SELECT 
            (SELECT COUNT(*) FROM applications) as aplicaciones,
            (SELECT COUNT(*) FROM application_components) as componentes,
            (SELECT COUNT(*) FROM versions) as versiones,
            (SELECT COUNT(*) FROM deployments) as despliegues
    """)
    
    stats = cursor.fetchone()
    print(f"📊 Estadísticas Generales:")
    print(f"   • Aplicaciones: {stats[0]}")
    print(f"   • Componentes: {stats[1]}")
    print(f"   • Versiones: {stats[2]}")
    print(f"   • Despliegues: {stats[3]}")
    
    # Estado por entorno
    print(f"\n🌍 Estado por Entorno:")
    cursor.execute("""
        SELECT 
            environment,
            status,
            COUNT(*) as cantidad
        FROM deployments 
        GROUP BY environment, status 
        ORDER BY environment, status
    """)
    
    env_stats = cursor.fetchall()
    current_env = None
    for env, status, count in env_stats:
        if env != current_env:
            print(f"   {env.upper()}:")
            current_env = env
        print(f"     • {status}: {count}")
    
    # Aplicaciones más activas
    print(f"\n🚀 Aplicaciones Más Activas:")
    cursor.execute("""
        SELECT 
            a.name as aplicacion,
            COUNT(d.id) as total_despliegues,
            COUNT(CASE WHEN d.status = 'success' THEN 1 END) as exitosos,
            ROUND(
                (COUNT(CASE WHEN d.status = 'success' THEN 1 END) * 100.0) / COUNT(d.id), 
                1
            ) as tasa_exito
        FROM applications a
        JOIN application_components ac ON a.id = ac.application_id
        JOIN deployments d ON ac.id = d.component_id
        GROUP BY a.id, a.name
        ORDER BY total_despliegues DESC
        LIMIT 5
    """)
    
    app_stats = cursor.fetchall()
    for app, total, exitosos, tasa in app_stats:
        print(f"   • {app}: {total} despliegues ({tasa}% éxito)")
    
    # Actividad reciente
    print(f"\n📅 Actividad Reciente (últimos 7 días):")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM deployments 
        WHERE DATE(deployed_at) >= DATE('now', '-7 days')
    """)
    recent = cursor.fetchone()[0]
    print(f"   • Despliegues: {recent}")
    
    cursor.execute("""
        SELECT COUNT(DISTINCT deployed_by) 
        FROM deployments 
        WHERE DATE(deployed_at) >= DATE('now', '-7 days')
        AND deployed_by IS NOT NULL
    """)
    users = cursor.fetchone()[0]
    print(f"   • Usuarios activos: {users}")
    
    conn.close()

def show_environment_status():
    """Mostrar estado detallado por entorno."""
    conn = connect_to_database()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    print("\n🌍 ESTADO DETALLADO POR ENTORNO")
    print("=" * 60)
    
    # Consulta del estado actual por aplicación y entorno
    cursor.execute("""
        SELECT 
            a.name as aplicacion,
            COUNT(DISTINCT ac.id) as total_componentes,
            
            -- Estado DEV
            COUNT(DISTINCT CASE 
                WHEN d_dev.environment = 'dev' AND d_dev.status = 'success' 
                THEN ac.id END) as dev_ok,
            COUNT(DISTINCT CASE 
                WHEN d_dev.environment = 'dev' AND d_dev.status = 'failed' 
                THEN ac.id END) as dev_failed,
            
            -- Estado PRE
            COUNT(DISTINCT CASE 
                WHEN d_pre.environment = 'pre' AND d_pre.status = 'success' 
                THEN ac.id END) as pre_ok,
            COUNT(DISTINCT CASE 
                WHEN d_pre.environment = 'pre' AND d_pre.status = 'failed' 
                THEN ac.id END) as pre_failed,
            
            -- Estado PROD
            COUNT(DISTINCT CASE 
                WHEN d_prod.environment = 'prod' AND d_prod.status = 'success' 
                THEN ac.id END) as prod_ok,
            COUNT(DISTINCT CASE 
                WHEN d_prod.environment = 'prod' AND d_prod.status = 'failed' 
                THEN ac.id END) as prod_failed

        FROM applications a
        LEFT JOIN application_components ac ON a.id = ac.application_id
        LEFT JOIN deployments d_dev ON ac.id = d_dev.component_id 
            AND d_dev.environment = 'dev'
            AND d_dev.id = (
                SELECT d2.id FROM deployments d2 
                WHERE d2.component_id = ac.id AND d2.environment = 'dev'
                ORDER BY d2.deployed_at DESC LIMIT 1
            )
        LEFT JOIN deployments d_pre ON ac.id = d_pre.component_id 
            AND d_pre.environment = 'pre'
            AND d_pre.id = (
                SELECT d2.id FROM deployments d2 
                WHERE d2.component_id = ac.id AND d2.environment = 'pre'
                ORDER BY d2.deployed_at DESC LIMIT 1
            )
        LEFT JOIN deployments d_prod ON ac.id = d_prod.component_id 
            AND d_prod.environment = 'prod'
            AND d_prod.id = (
                SELECT d2.id FROM deployments d2 
                WHERE d2.component_id = ac.id AND d2.environment = 'prod'
                ORDER BY d2.deployed_at DESC LIMIT 1
            )
        GROUP BY a.id, a.name
        ORDER BY a.name
    """)
    
    env_data = cursor.fetchall()
    
    print(f"{'Aplicación':<25} {'DEV':<8} {'PRE':<8} {'PROD':<8}")
    print("-" * 60)
    
    for row in env_data:
        app, total, dev_ok, dev_fail, pre_ok, pre_fail, prod_ok, prod_fail = row
        
        # Indicadores de estado
        dev_status = "✅" if dev_ok == total and dev_fail == 0 else "⚠️" if dev_ok > 0 else "❌"
        pre_status = "✅" if pre_ok == total and pre_fail == 0 else "⚠️" if pre_ok > 0 else "❌"
        prod_status = "✅" if prod_ok == total and prod_fail == 0 else "⚠️" if prod_ok > 0 else "❌"
        
        print(f"{app:<25} {dev_status} {dev_ok}/{total:<5} {pre_status} {pre_ok}/{total:<5} {prod_status} {prod_ok}/{total}")
    
    conn.close()

def show_recent_activity():
    """Mostrar actividad reciente de despliegues."""
    conn = connect_to_database()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    print("\n📈 ACTIVIDAD RECIENTE (Últimos 10 despliegues)")
    print("=" * 80)
    
    cursor.execute("""
        SELECT 
            a.name as aplicacion,
            ac.name as componente,
            v.version,
            d.environment,
            d.status,
            d.deployed_by,
            d.deployed_at,
            CASE 
                WHEN d.status = 'success' THEN '✅'
                WHEN d.status = 'failed' THEN '❌'
                WHEN d.status = 'rollback' THEN '🔄'
                ELSE '⏳'
            END as status_icon
        FROM deployments d
        JOIN application_components ac ON d.component_id = ac.id
        JOIN applications a ON ac.application_id = a.id
        JOIN versions v ON d.version_id = v.id
        ORDER BY d.deployed_at DESC
        LIMIT 10
    """)
    
    recent_deployments = cursor.fetchall()
    
    for deploy in recent_deployments:
        app, comp, version, env, status, user, deployed_at, icon = deploy
        # Formatear fecha
        try:
            dt = datetime.fromisoformat(deployed_at.replace('Z', '+00:00'))
            date_str = dt.strftime('%Y-%m-%d %H:%M')
        except:
            date_str = deployed_at[:16]
        
        comp_short = comp[:30] + "..." if len(comp) > 30 else comp
        print(f"{icon} {date_str} | {env.upper():<4} | {app:<20} | {comp_short:<35} | v{version} | {user or 'N/A'}")
    
    conn.close()

def main():
    """Función principal."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "summary":
            show_database_summary()
        elif command == "environments":
            show_environment_status()
        elif command == "recent":
            show_recent_activity()
        elif command == "all":
            show_database_summary()
            show_environment_status()
            show_recent_activity()
        else:
            print("❌ Comando no reconocido.")
            print("💡 Uso: python database_info.py [summary|environments|recent|all]")
    else:
        # Por defecto, mostrar resumen
        show_database_summary()

if __name__ == "__main__":
    main()