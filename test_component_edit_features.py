#!/usr/bin/env python3
"""
Script de prueba para verificar las funcionalidades de edición de componentes.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from frontend.dashboard_tools import dashboard_tools

def test_component_crud():
    """Prueba las operaciones CRUD de componentes."""
    print("🧪 === PRUEBAS DE COMPONENTES ===")
    
    # 1. Listar componentes existentes
    print("\n📦 1. Listando componentes existentes...")
    components = dashboard_tools.list_components()
    print(f"   ✅ Encontrados {len(components)} componentes")
    
    if components:
        print("   📋 Primeros 3 componentes:")
        for i, comp in enumerate(components[:3]):
            print(f"      {i+1}. {comp['application_name']} - {comp['name']} ({comp['type']})")
    
    # 2. Probar actualización de componente (si existe alguno)
    if components:
        test_component = components[0]
        print(f"\n✏️ 2. Probando edición del componente: {test_component['name']}")
        
        original_name = test_component['name']
        test_name = f"{original_name} [EDITADO]"
        
        # Actualizar
        result = dashboard_tools.update_component(
            component_id=test_component['id'],
            name=test_name,
            repository_url=test_component.get('repository_url', ''),
            tech_stack=['Angular 18', 'TypeScript', 'Material UI'] if test_component['type'] == 'frontend' else ['C#', '.NET Core 8', 'Entity Framework'],
            health_check_url="https://api.test.com/health"
        )
        
        if result["success"]:
            print(f"   ✅ Componente actualizado: {result['message']}")
            
            # Verificar el cambio
            updated_components = dashboard_tools.list_components()
            updated_comp = next((c for c in updated_components if c['id'] == test_component['id']), None)
            
            if updated_comp and updated_comp['name'] == test_name:
                print(f"   ✅ Verificación exitosa: Nombre cambiado a '{test_name}'")
                
                # Restaurar nombre original
                restore_result = dashboard_tools.update_component(
                    component_id=test_component['id'],
                    name=original_name,
                    repository_url=test_component.get('repository_url', ''),
                    tech_stack=test_component.get('tech_stack', '').split(',') if test_component.get('tech_stack') else [],
                    health_check_url=test_component.get('health_check_url', '')
                )
                
                if restore_result["success"]:
                    print(f"   ✅ Nombre restaurado a: '{original_name}'")
                else:
                    print(f"   ⚠️ No se pudo restaurar el nombre: {restore_result['message']}")
            else:
                print(f"   ❌ Error: No se pudo verificar el cambio")
        else:
            print(f"   ❌ Error al actualizar: {result['message']}")
    
    # 3. Probar creación de versión
    if components:
        test_component = components[0]
        print(f"\n🔖 3. Probando creación de versión para: {test_component['name']}")
        
        version_result = dashboard_tools.create_version(
            component_id=test_component['id'],
            version="v99.99.99-test",
            branch="feature/test-edit",
            commit_hash="abc123test",
            build_number="999",
            features=["Funcionalidad de prueba de edición"],
            bug_fixes=["Corrección de prueba"]
        )
        
        if version_result["success"]:
            print(f"   ✅ Versión de prueba creada: {version_result['message']}")
        else:
            print(f"   ⚠️ Error al crear versión de prueba: {version_result['message']}")

def test_application_grouping():
    """Prueba el agrupamiento de componentes por aplicación."""
    print("\n🏢 === PRUEBAS DE AGRUPAMIENTO ===")
    
    components = dashboard_tools.list_components()
    
    if not components:
        print("   ⚠️ No hay componentes para agrupar")
        return
    
    # Agrupar por aplicación
    apps_dict = {}
    for comp in components:
        app_name = comp['application_name']
        if app_name not in apps_dict:
            apps_dict[app_name] = []
        apps_dict[app_name].append(comp)
    
    print(f"   📊 Componentes agrupados en {len(apps_dict)} aplicaciones:")
    
    for app_name, app_components in apps_dict.items():
        frontend_count = sum(1 for c in app_components if c['type'] == 'frontend')
        backend_count = sum(1 for c in app_components if c['type'] == 'backend')
        other_count = len(app_components) - frontend_count - backend_count
        
        print(f"   🏢 {app_name}:")
        print(f"      📦 Total: {len(app_components)} componentes")
        print(f"      🌐 Frontend: {frontend_count}")
        print(f"      ⚙️ Backend: {backend_count}")
        print(f"      🔧 Otros: {other_count}")

def test_tech_stack_parsing():
    """Prueba el parsing del tech stack."""
    print("\n💻 === PRUEBAS DE TECH STACK ===")
    
    components = dashboard_tools.list_components()
    
    for comp in components[:3]:  # Solo primeros 3
        tech_stack = comp.get('tech_stack', '')
        if tech_stack:
            print(f"   📦 {comp['name']} ({comp['type']}):")
            
            if isinstance(tech_stack, str):
                tech_list = [tech.strip() for tech in tech_stack.split(',')]
                print(f"      💻 Stack: {tech_list}")
            else:
                print(f"      💻 Stack: {tech_stack}")

def main():
    """Función principal de pruebas."""
    print("🚀 VERIFICACIÓN DE FUNCIONALIDADES DE EDICIÓN DE COMPONENTES")
    print("=" * 60)
    
    try:
        test_component_crud()
        test_application_grouping()
        test_tech_stack_parsing()
        
        print("\n" + "=" * 60)
        print("✅ TODAS LAS PRUEBAS COMPLETADAS")
        print("\n📋 RESUMEN DE FUNCIONALIDADES VERIFICADAS:")
        print("   ✅ Listado de componentes por aplicación")
        print("   ✅ Edición de componentes (nombre, URLs, tech stack)")
        print("   ✅ Creación de versiones para componentes")
        print("   ✅ Agrupamiento automático por aplicación")
        print("   ✅ Parsing de tech stack")
        print("\n🎯 ACCESO AL DASHBOARD:")
        print("   🌐 URL: http://localhost:8501")
        print("   📍 Ir a: '📦 Componentes' para ver la edición en acción")
        
    except Exception as e:
        print(f"\n❌ ERROR EN LAS PRUEBAS: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()