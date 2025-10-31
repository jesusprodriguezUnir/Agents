#!/usr/bin/env python3
"""
Script de verificación después de eliminar gráficos
"""

import sys
import os

def verify_no_graphs():
    """Verifica que se eliminaron los gráficos correctamente."""
    print("🧪 Verificando eliminación de gráficos...")
    
    dashboard_file = "src/frontend/enhanced_dashboard.py"
    
    if not os.path.exists(dashboard_file):
        print("❌ Archivo dashboard no encontrado")
        return False
    
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar que se eliminaron las referencias
    removed_items = [
        "plotly_chart",
        "px.bar",
        "px.pie", 
        "📊 Componentes por Aplicación",
        "🎯 Despliegues por Entorno",
        "comp_counts",
        "env_counts"
    ]
    
    found_items = []
    for item in removed_items:
        if item in content:
            found_items.append(item)
    
    if found_items:
        print(f"⚠️  Elementos de gráficos aún presentes: {found_items}")
        return False
    
    # Verificar que las importaciones fueron limpiadas
    if "import plotly.express as px" in content:
        print("⚠️  Importación de plotly.express aún presente")
        return False
    
    if "import plotly.graph_objects as go" in content:
        print("⚠️  Importación de plotly.graph_objects aún presente")
        return False
    
    print("✅ Gráficos eliminados correctamente")
    print("✅ Importaciones de plotly limpiadas")
    print("✅ Dashboard más ligero y enfocado")
    
    return True

def verify_essential_features():
    """Verifica que las funcionalidades esenciales siguen presentes."""
    print("\n🔍 Verificando funcionalidades esenciales...")
    
    dashboard_file = "src/frontend/enhanced_dashboard.py"
    
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    essential_features = [
        "get_compact_environment_summary",
        "create_pdf_report", 
        "show_enhanced_overview",
        "show_applications_with_edit",
        "Estado Actual de Entornos",
        "environment-card",
        "✅",  # Indicadores de estado
        "⚠️"   # Indicadores de advertencia
    ]
    
    missing_features = []
    for feature in essential_features:
        if feature not in content:
            missing_features.append(feature)
    
    if missing_features:
        print(f"❌ Funcionalidades faltantes: {missing_features}")
        return False
    
    print("✅ Todas las funcionalidades esenciales presentes")
    print("✅ Resumen compacto de entornos mantenido")
    print("✅ Exportación PDF disponible")
    print("✅ Edición de aplicaciones disponible")
    
    return True

def main():
    """Función principal de verificación."""
    print("🔧 Verificación Post-Eliminación de Gráficos")
    print("=" * 50)
    
    graphs_ok = verify_no_graphs()
    features_ok = verify_essential_features()
    
    print("\n" + "=" * 50)
    
    if graphs_ok and features_ok:
        print("🎉 ¡VERIFICACIÓN EXITOSA!")
        print("✅ Gráficos eliminados correctamente")
        print("✅ Funcionalidades esenciales preservadas") 
        print("✅ Dashboard más limpio y enfocado")
        print("\n💡 Beneficios obtenidos:")
        print("   - Menor tiempo de carga")
        print("   - Interfaz más limpia") 
        print("   - Enfoque en información esencial")
        print("   - Menos dependencias")
    else:
        print("❌ VERIFICACIÓN FALLIDA")
        print("   Revisar los elementos reportados arriba")
    
    print(f"\n🌐 Dashboard: http://localhost:8501")

if __name__ == "__main__":
    main()