#!/usr/bin/env python3
"""
Script de prueba para verificar el resumen compacto de entornos
"""

import sys
import os
import sqlite3
import pandas as pd
from datetime import datetime

def get_database_connection():
    """Obtiene conexión a la base de datos."""
    return sqlite3.connect('data/deployments.db')

def get_environment_summary():
    """Obtiene resumen de todos los entornos."""
    conn = get_database_connection()
    
    # Obtener último despliegue exitoso por componente y entorno
    df = pd.read_sql_query("""
        WITH latest_deployments AS (
            SELECT 
                d.component_id,
                d.environment,
                MAX(d.deployed_at) as last_deployed
            FROM deployments d
            WHERE d.status = 'success'
            GROUP BY d.component_id, d.environment
        )
        SELECT 
            d.environment,
            a.name as application_name,
            ac.type as component_type,
            ac.name as component_name,
            v.version,
            d.deployed_at,
            d.deployed_by,
            ac.repository_url
        FROM deployments d
        JOIN latest_deployments ld ON d.component_id = ld.component_id 
            AND d.environment = ld.environment 
            AND d.deployed_at = ld.last_deployed
        JOIN versions v ON d.version_id = v.id
        JOIN application_components ac ON d.component_id = ac.id
        JOIN applications a ON ac.application_id = a.id
        WHERE d.status = 'success'
        ORDER BY d.environment, a.name, ac.type
    """, conn)
    
    conn.close()
    return df

def get_compact_environment_summary():
    """Obtiene resumen compacto agrupado por aplicación y entorno."""
    env_summary = get_environment_summary()
    
    if env_summary.empty:
        return {}
    
    # Filtrar aplicaciones específicas (excluir Cargos Funcionales)
    excluded_apps = ['Cargos Funcionales']
    env_summary = env_summary[~env_summary['application_name'].isin(excluded_apps)]
    
    # Agrupar por entorno y aplicación
    compact_summary = {}
    
    for env in ['dev', 'pre', 'prod']:
        env_data = env_summary[env_summary['environment'] == env]
        compact_summary[env] = {}
        
        for app_name in env_data['application_name'].unique():
            app_data = env_data[env_data['application_name'] == app_name]
            
            compact_summary[env][app_name] = {
                'frontend': None,
                'backend': None,
                'last_deploy': None
            }
            
            for _, row in app_data.iterrows():
                component_type = row['component_type']
                compact_summary[env][app_name][component_type] = {
                    'version': row['version'],
                    'deployed_at': row['deployed_at']
                }
                
                # Mantener la fecha más reciente
                if compact_summary[env][app_name]['last_deploy'] is None or \
                   (row['deployed_at'] and row['deployed_at'] > compact_summary[env][app_name]['last_deploy']):
                    compact_summary[env][app_name]['last_deploy'] = row['deployed_at']
    
    return compact_summary

def test_compact_summary():
    """Prueba el resumen compacto de entornos."""
    print("🧪 Probando resumen compacto de entornos...")
    
    try:
        compact_summary = get_compact_environment_summary()
        
        if not compact_summary:
            print("❌ No se encontraron datos")
            return
        
        print("✅ Datos obtenidos correctamente")
        print("\n📊 Resumen por Entorno:\n")
        
        env_icons = {
            'dev': '🔧 DESARROLLO',
            'pre': '🧪 PREPRODUCCIÓN', 
            'prod': '🌟 PRODUCCIÓN'
        }
        
        for env, env_data in compact_summary.items():
            print(f"\n{env_icons.get(env, env.upper())}")
            print("=" * 40)
            
            if not env_data:
                print("  Sin despliegues")
                continue
            
            for app_name, app_data in env_data.items():
                frontend_version = app_data['frontend']['version'] if app_data['frontend'] else 'N/A'
                backend_version = app_data['backend']['version'] if app_data['backend'] else 'N/A'
                last_deploy = app_data['last_deploy'][:10] if app_data['last_deploy'] else 'N/A'
                
                has_both = app_data['frontend'] and app_data['backend']
                status = "✅" if has_both else "⚠️"
                
                print(f"  {status} {app_name}")
                print(f"    🌐 Frontend: v{frontend_version}")
                print(f"    ⚙️ Backend:  v{backend_version}")
                print(f"    📅 Último:   {last_deploy}")
                print()
        
        print("✅ Prueba completada correctamente")
        print("\n💡 Notas:")
        print("   - Cargos Funcionales ha sido excluido del resumen")
        print("   - Cada aplicación muestra frontend y backend en la misma card")
        print("   - ✅ = Ambos componentes desplegados, ⚠️ = Falta algún componente")
        
    except Exception as e:
        print(f"❌ Error en la prueba: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_compact_summary()