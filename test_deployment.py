"""
Test simple de las herramientas de deployment.
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.tools.registry import ToolRegistry
from src.tools.basic_tools import register_basic_tools


async def main():
    """Test de las herramientas de deployment."""
    
    print("🧪 Iniciando test del servidor MCP de Deployment")
    print("=" * 50)
    
    # Crear registro de herramientas
    registry = ToolRegistry()
    
    # Registrar herramientas
    print("📝 Registrando herramientas...")
    await register_basic_tools(registry)
    
    print(f"✅ {registry.get_tools_count()} herramientas registradas")
    print("\n🛠️ Herramientas disponibles:")
    
    tools = await registry.list_tools()
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    print("\n🚀 Probando herramientas de deployment...")
    
    # Test 1: Crear versiones de ejemplo
    print("\n1️⃣ Creando versiones de ejemplo...")
    
    result = await registry.execute_tool("create_sample_version", {
        "environment": "dev",
        "version": "1.0.0",
        "branch": "main"
    })
    print("Resultado:", result[0].text if hasattr(result[0], 'text') else result)
    
    result = await registry.execute_tool("create_sample_version", {
        "environment": "dev", 
        "version": "1.1.0",
        "branch": "develop"
    })
    print("Resultado:", result[0].text if hasattr(result[0], 'text') else result)
    
    # Test 2: Listar versiones
    print("\n2️⃣ Listando versiones en DEV...")
    result = await registry.execute_tool("list_versions", {
        "environment": "dev"
    })
    print("Resultado:", result[0].text if hasattr(result[0], 'text') else result)
    
    # Test 3: Registrar un despliegue
    print("\n3️⃣ Registrando despliegue...")
    result = await registry.execute_tool("register_deployment", {
        "environment": "dev",
        "version": "1.0.0",
        "deployed_by": "DevOps Team",
        "notes": "Despliegue inicial para testing"
    })
    print("Resultado:", result[0].text if hasattr(result[0], 'text') else result)
    
    # Test 4: Obtener historial
    print("\n4️⃣ Obteniendo historial de despliegues...")
    result = await registry.execute_tool("get_deployment_history", {
        "environment": "dev",
        "limit": 5
    })
    print("Resultado:", result[0].text if hasattr(result[0], 'text') else result)
    
    # Test 5: Estado del entorno
    print("\n5️⃣ Estado del entorno DEV...")
    result = await registry.execute_tool("get_environment_status", {
        "environment": "dev"
    })
    print("Resultado:", result[0].text if hasattr(result[0], 'text') else result)
    
    print("\n✅ Test completado exitosamente!")
    print("🌐 Ahora puedes ejecutar: streamlit run src/frontend/app.py")


if __name__ == "__main__":
    asyncio.run(main())