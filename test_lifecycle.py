"""
Test adicional para probar cambio de estado de despliegue.
"""

import asyncio
import sys
from pathlib import Path
import json

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.tools.registry import ToolRegistry
from src.tools.basic_tools import register_basic_tools


async def test_deployment_lifecycle():
    """Test completo del ciclo de vida de un despliegue."""
    
    print("🔄 Test del ciclo completo de despliegue")
    print("=" * 45)
    
    registry = ToolRegistry()
    await register_basic_tools(registry)
    
    # 1. Crear versión
    print("1️⃣ Creando versión 2.0.0 en PROD...")
    result = await registry.execute_tool("create_sample_version", {
        "environment": "prod",
        "version": "2.0.0",
        "branch": "release/2.0.0"
    })
    version_data = json.loads(result[0].text if hasattr(result[0], 'text') else result[0]['text'])
    print(f"✅ Versión creada: {version_data['version']['version']}")
    
    # 2. Registrar despliegue
    print("\n2️⃣ Iniciando despliegue en PROD...")
    result = await registry.execute_tool("register_deployment", {
        "environment": "prod",
        "version": "2.0.0",
        "deployed_by": "Release Manager",
        "notes": "Despliegue de nueva versión major con breaking changes"
    })
    deployment_data = json.loads(result[0].text if hasattr(result[0], 'text') else result[0]['text'])
    deployment_id = deployment_data['deployment_id']
    print(f"✅ Despliegue iniciado: {deployment_id}")
    
    # 3. Actualizar a exitoso
    print("\n3️⃣ Marcando despliegue como exitoso...")
    result = await registry.execute_tool("update_deployment_status", {
        "deployment_id": deployment_id,
        "status": "success",
        "notes": "Despliegue completado sin incidencias. Todas las validaciones pasaron."
    })
    update_data = json.loads(result[0].text if hasattr(result[0], 'text') else result[0]['text'])
    print(f"✅ Estado actualizado: {update_data['new_status']}")
    
    # 4. Verificar estado del entorno PROD
    print("\n4️⃣ Verificando estado de PROD...")
    result = await registry.execute_tool("get_environment_status", {
        "environment": "prod"
    })
    env_data = json.loads(result[0].text if hasattr(result[0], 'text') else result[0]['text'])
    print(f"✅ Health Status: {env_data['metrics']['health_status']}")
    print(f"📊 Success Rate: {env_data['metrics']['success_rate_percentage']}%")
    
    # 5. Comparar versiones
    print("\n5️⃣ Comparando versiones...")
    # Primero crear otra versión para comparar
    await registry.execute_tool("create_sample_version", {
        "environment": "prod",
        "version": "1.9.0",
        "branch": "release/1.9.0"
    })
    
    result = await registry.execute_tool("compare_versions", {
        "environment": "prod",
        "version1": "1.9.0",
        "version2": "2.0.0"
    })
    compare_data = json.loads(result[0].text if hasattr(result[0], 'text') else result[0]['text'])
    print(f"✅ Diferencias encontradas:")
    print(f"   - Nuevas features: {len(compare_data['differences']['new_features'])}")
    print(f"   - Bug fixes: {len(compare_data['differences']['new_bug_fixes'])}")
    print(f"   - Breaking changes: {len(compare_data['differences']['new_breaking_changes'])}")
    
    print("\n🎉 ¡Ciclo completo de despliegue simulado exitosamente!")
    print("\n📋 Resumen:")
    print(f"   • Versión desplegada: 2.0.0")
    print(f"   • Entorno: PROD")
    print(f"   • Estado: SUCCESS")
    print(f"   • ID de despliegue: {deployment_id[:8]}...")


if __name__ == "__main__":
    asyncio.run(test_deployment_lifecycle())