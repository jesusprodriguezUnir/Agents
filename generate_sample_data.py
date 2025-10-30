"""
Script para generar datos de prueba para el dashboard de despliegues.
"""

import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.tools.registry import ToolRegistry
from src.tools.basic_tools import register_basic_tools


async def generate_sample_data():
    """Genera datos de ejemplo para el dashboard."""
    
    print("🎯 Generando datos de ejemplo para el dashboard...")
    print("=" * 50)
    
    registry = ToolRegistry()
    await register_basic_tools(registry)
    
    # Crear versiones en diferentes entornos
    versions_to_create = [
        # DEV environment
        ("dev", "1.0.0", "main"),
        ("dev", "1.1.0", "develop"),
        ("dev", "1.2.0", "feature/new-ui"),
        ("dev", "2.0.0-beta", "develop"),
        
        # PRE environment
        ("pre", "1.0.0", "main"),
        ("pre", "1.1.0", "release/1.1.0"),
        ("pre", "1.2.0", "release/1.2.0"),
        
        # PROD environment
        ("prod", "1.0.0", "main"),
        ("prod", "1.1.0", "release/1.1.0"),
    ]
    
    print("📦 Creando versiones...")
    for env, version, branch in versions_to_create:
        result = await registry.execute_tool("create_sample_version", {
            "environment": env,
            "version": version,
            "branch": branch
        })
        print(f"  ✅ {env.upper()}: {version} ({branch})")
    
    # Crear despliegues de ejemplo
    deployments_to_create = [
        # Despliegues exitosos
        ("dev", "1.0.0", "DevOps Team", "success", "Despliegue inicial exitoso"),
        ("dev", "1.1.0", "Frontend Team", "success", "Nueva interfaz de usuario"),
        ("dev", "1.2.0", "Backend Team", "success", "Optimizaciones de API"),
        
        ("pre", "1.0.0", "Release Manager", "success", "Primera release en PRE"),
        ("pre", "1.1.0", "QA Team", "success", "Testing completo aprobado"),
        
        ("prod", "1.0.0", "Release Manager", "success", "Go-live exitoso"),
        ("prod", "1.1.0", "DevOps Team", "success", "Release mensual"),
        
        # Algunos despliegues problemáticos
        ("dev", "2.0.0-beta", "Developer", "failed", "Error en migración de BD"),
        ("pre", "1.2.0", "QA Team", "in_progress", "Testing en progreso"),
    ]
    
    print("\n🚀 Creando despliegues...")
    deployment_ids = []
    
    for env, version, deployer, status, notes in deployments_to_create:
        # Registrar despliegue
        result = await registry.execute_tool("register_deployment", {
            "environment": env,
            "version": version,
            "deployed_by": deployer,
            "notes": notes
        })
        
        # Obtener ID del despliegue
        import json
        data = json.loads(result[0].text if hasattr(result[0], 'text') else result[0])
        deployment_id = data.get('deployment_id')
        deployment_ids.append((deployment_id, status, notes))
        
        print(f"  🚀 {env.upper()}: {version} por {deployer}")
        
        # Si no es 'in_progress', actualizar el estado
        if status != "in_progress":
            await registry.execute_tool("update_deployment_status", {
                "deployment_id": deployment_id,
                "status": status,
                "notes": f"Estado final: {status}. {notes}"
            })
    
    print("\n📊 Verificando estados de entornos...")
    
    for env in ["dev", "pre", "prod"]:
        result = await registry.execute_tool("get_environment_status", {
            "environment": env
        })
        
        import json
        data = json.loads(result[0].text if hasattr(result[0], 'text') else result[0])
        
        if "error" not in data:
            metrics = data.get("metrics", {})
            current = data.get("current_deployment", {})
            
            print(f"  🌍 {env.upper()}:")
            print(f"    - Versión actual: {current.get('version', 'N/A')}")
            print(f"    - Health: {metrics.get('health_status', 'unknown')}")
            print(f"    - Success rate: {metrics.get('success_rate_percentage', 0)}%")
            print(f"    - Total despliegues: {metrics.get('total_deployments', 0)}")
    
    print("\n🎉 ¡Datos de ejemplo generados exitosamente!")
    print("\n🌐 Ahora puedes abrir el dashboard en: http://localhost:8501")
    print("\n✨ Características del Dashboard:")
    print("  • 🌍 Vista general de entornos con métricas")
    print("  • 🚀 Gestión completa de despliegues")
    print("  • 📋 Administración de versiones")
    print("  • 🔍 Comparación entre versiones")
    print("  • 📊 Gráficos y tendencias")
    print("  • 🎨 Interfaz profesional y responsive")


if __name__ == "__main__":
    asyncio.run(generate_sample_data())