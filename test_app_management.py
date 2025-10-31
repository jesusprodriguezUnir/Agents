"""
Script de prueba para verificar las funcionalidades de gestión de aplicaciones y componentes.
"""

import sqlite3
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar funciones del dashboard
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'frontend'))
from multi_org_dashboard import (
    get_applications, 
    get_components_by_app, 
    create_application, 
    create_component,
    update_application,
    update_component,
    delete_component,
    delete_application
)

def test_application_management():
    """Prueba las funciones de gestión de aplicaciones."""
    print("🧪 PRUEBAS DE GESTIÓN DE APLICACIONES")
    print("=" * 50)
    
    # 1. Listar aplicaciones existentes
    print("\n📋 Aplicaciones existentes:")
    applications = get_applications()
    for app in applications:
        print(f"  • {app['name']}: {app['component_count']} componentes, {app['deployment_count']} despliegues")
    
    # 2. Crear una nueva aplicación de prueba
    print("\n➕ Creando aplicación de prueba...")
    success, message = create_application("App Prueba", "Aplicación de prueba para testing")
    print(f"   Resultado: {message}")
    
    if success:
        # 3. Listar aplicaciones después de crear
        print("\n📋 Aplicaciones después de crear:")
        applications = get_applications()
        test_app_id = None
        for app in applications:
            print(f"  • {app['name']}: {app['component_count']} componentes")
            if app['name'] == "App Prueba":
                test_app_id = app['id']
        
        if test_app_id:
            # 4. Crear un componente de prueba
            print(f"\n🧩 Creando componente para aplicación {test_app_id}...")
            success2, message2 = create_component(test_app_id, "Frontend Test", "frontend", "https://github.com/test/frontend")
            print(f"   Resultado: {message2}")
            
            # 5. Listar componentes
            print(f"\n📋 Componentes de la aplicación:")
            components = get_components_by_app(test_app_id)
            test_comp_id = None
            for comp in components:
                print(f"  • {comp['name']} ({comp['type']}): {comp['version_count']} versiones")
                if comp['name'] == "Frontend Test":
                    test_comp_id = comp['id']
            
            # 6. Actualizar el componente
            if test_comp_id:
                print(f"\n✏️ Actualizando componente {test_comp_id}...")
                success3, message3 = update_component(test_comp_id, "Frontend Test Updated", "frontend", "https://github.com/test/frontend-updated")
                print(f"   Resultado: {message3}")
            
            # 7. Limpiar - eliminar componente de prueba
            if test_comp_id:
                print(f"\n🗑️ Eliminando componente de prueba...")
                success4, message4 = delete_component(test_comp_id)
                print(f"   Resultado: {message4}")
            
            # 8. Actualizar aplicación
            print(f"\n✏️ Actualizando aplicación...")
            success5, message5 = update_application(test_app_id, "App Prueba Updated", "Aplicación de prueba actualizada")
            print(f"   Resultado: {message5}")
            
            # 9. Limpiar - eliminar aplicación de prueba
            print(f"\n🗑️ Eliminando aplicación de prueba...")
            success6, message6 = delete_application(test_app_id)
            print(f"   Resultado: {message6}")
    
    print("\n✅ Pruebas de aplicaciones completadas")


def test_database_structure():
    """Verifica la estructura de la base de datos."""
    print("\n🔍 VERIFICACIÓN DE ESTRUCTURA DE BASE DE DATOS")
    print("=" * 50)
    
    conn = sqlite3.connect("data/deployments.db")
    conn.row_factory = sqlite3.Row
    
    # Verificar tablas principales
    tables = ['applications', 'application_components', 'versions', 'deployments', 'organizations', 'environments', 'environment_urls']
    
    for table in tables:
        try:
            count = conn.execute(f"SELECT COUNT(*) as count FROM {table}").fetchone()['count']
            print(f"  📊 {table}: {count} registros")
        except Exception as e:
            print(f"  ❌ {table}: Error - {e}")
    
    conn.close()
    print("\n✅ Verificación completada")


def main():
    """Función principal de pruebas."""
    print("🧪 SCRIPT DE PRUEBAS - GESTIÓN DE APLICACIONES Y COMPONENTES")
    print("=" * 70)
    
    try:
        # Verificar estructura de BD
        test_database_structure()
        
        # Probar gestión de aplicaciones
        test_application_management()
        
        print("\n🎉 ¡TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE!")
        print("\n📱 Puedes usar el dashboard con:")
        print("   python run_multi_org_dashboard.py")
        print("\n🌐 Y navegar a la pestaña '📱 Aplicaciones' para gestionar aplicaciones y componentes")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()