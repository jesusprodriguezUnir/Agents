"""
Script de prueba para las nuevas herramientas MCP multi-aplicación.
"""

import sys
from pathlib import Path

# Añadir src al path
script_dir = Path(__file__).parent
project_dir = script_dir.parent
src_dir = project_dir / "src"
sys.path.insert(0, str(src_dir))

from tools.deployment.version_tools_new import (
    list_applications, get_application, list_versions, create_version
)
from tools.deployment.deployment_tools_new import (
    list_deployments, get_environment_overview, create_deployment
)

def test_application_tools():
    """Prueba las herramientas de aplicaciones."""
    print("🧪 Probando herramientas de aplicaciones...")
    
    # Listar aplicaciones
    result = list_applications()
    print(f"✅ list_applications: {result.message}")
    if result.success and result.data:
        apps = result.data['applications']
        print(f"   Encontradas {len(apps)} aplicaciones")
        for app in apps[:3]:  # Mostrar solo las primeras 3
            print(f"   - {app['name']} ({app['type']})")
    
    # Obtener detalles de una aplicación específica
    if result.success and result.data['applications']:
        app_id = result.data['applications'][0]['id']
        app_result = get_application(app_id)
        print(f"✅ get_application: {app_result.message}")


def test_version_tools():
    """Prueba las herramientas de versiones."""
    print("\n🏷️ Probando herramientas de versiones...")
    
    # Listar todas las versiones
    result = list_versions()
    print(f"✅ list_versions (todas): {result.message}")
    if result.success and result.data:
        versions = result.data['versions']
        print(f"   Encontradas {len(versions)} versiones")
        for version in versions[:3]:  # Mostrar solo las primeras 3
            print(f"   - {version['application_name']} v{version['version']}")
    
    # Listar versiones de una aplicación específica
    apps_result = list_applications()
    if apps_result.success and apps_result.data['applications']:
        app_id = apps_result.data['applications'][0]['id']
        app_name = apps_result.data['applications'][0]['name']
        
        app_versions_result = list_versions(application_id=app_id)
        print(f"✅ list_versions ({app_name}): {app_versions_result.message}")


def test_deployment_tools():
    """Prueba las herramientas de despliegues."""
    print("\n🚀 Probando herramientas de despliegues...")
    
    # Listar todos los despliegues
    result = list_deployments(limit=10)
    print(f"✅ list_deployments: {result.message}")
    if result.success and result.data:
        deployments = result.data['deployments']
        print(f"   Encontrados {len(deployments)} despliegues")
        for deployment in deployments[:3]:  # Mostrar solo los primeros 3
            print(f"   - {deployment['application_name']} v{deployment['version']} en {deployment['environment']} ({deployment['status']})")
    
    # Vista general de entornos
    for env in ['dev', 'pre', 'prod']:
        env_result = get_environment_overview(env)
        print(f"✅ get_environment_overview ({env}): {env_result.message}")
        if env_result.success and env_result.data:
            overview = env_result.data
            print(f"   {overview['total_applications']} aplicaciones, {overview['healthy_applications']} saludables")


def test_deployment_creation():
    """Prueba la creación de un nuevo despliegue."""
    print("\n🆕 Probando creación de despliegue...")
    
    # Obtener una aplicación y versión existente
    apps_result = list_applications()
    if not apps_result.success or not apps_result.data['applications']:
        print("❌ No hay aplicaciones disponibles para prueba")
        return
    
    app = apps_result.data['applications'][0]
    app_id = app['id']
    app_name = app['name']
    
    # Obtener versiones de la aplicación
    versions_result = list_versions(application_id=app_id)
    if not versions_result.success or not versions_result.data['versions']:
        print(f"❌ No hay versiones disponibles para {app_name}")
        return
    
    version = versions_result.data['versions'][0]['version']
    
    # Crear un nuevo despliegue
    deployment_result = create_deployment(
        application_id=app_id,
        environment="dev",
        version=version,
        deployed_by="test_user",
        notes="Despliegue de prueba desde script de testing"
    )
    
    print(f"✅ create_deployment: {deployment_result.message}")
    if deployment_result.success:
        deployment_data = deployment_result.data
        print(f"   Creado despliegue {deployment_data['deployment_id']} para {deployment_data['application_name']}")


def main():
    """Función principal de pruebas."""
    print("🚀 Iniciando pruebas de herramientas MCP multi-aplicación...")
    print("=" * 60)
    
    try:
        test_application_tools()
        test_version_tools()
        test_deployment_tools()
        test_deployment_creation()
        
        print("\n" + "=" * 60)
        print("✨ ¡Todas las pruebas completadas exitosamente!")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()