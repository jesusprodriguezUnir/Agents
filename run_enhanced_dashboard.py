#!/usr/bin/env python3
"""
Script para lanzar el Dashboard Mejorado de MCP Deployment Manager

Este script verifica los requisitos del sistema, la base de datos y
lanza el dashboard mejorado en el puerto 8501.
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def check_requirements():
    """Verifica que todos los requisitos estén instalados."""
    try:
        import streamlit
        import plotly
        import pandas
        print("✅ Todas las dependencias están instaladas")
        return True
    except ImportError as e:
        print(f"❌ Faltan dependencias: {e}")
        print("Ejecuta: pip install -r requirements.txt")
        return False

def check_database():
    """Verifica que la base de datos existe y tiene datos."""
    db_path = Path("data/deployments.db")
    
    if not db_path.exists():
        print("❌ Base de datos no encontrada")
        print("Ejecuta: python scripts/generate_hierarchical_apps.py")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar que las tablas existen
        cursor.execute("SELECT count(*) FROM applications")
        apps_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT count(*) FROM application_components")
        components_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT count(*) FROM versions")
        versions_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT count(*) FROM deployments")
        deployments_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"✅ Base de datos encontrada:")
        print(f"   - {apps_count} aplicaciones")
        print(f"   - {components_count} componentes")
        print(f"   - {versions_count} versiones")
        print(f"   - {deployments_count} despliegues")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")
        return False

def check_dashboard_file():
    """Verifica que el archivo del dashboard existe."""
    dashboard_path = Path("src/frontend/enhanced_dashboard.py")
    
    if not dashboard_path.exists():
        print("❌ Dashboard mejorado no encontrado")
        return False
    
    print("✅ Dashboard mejorado encontrado")
    return True

def launch_dashboard():
    """Lanza el dashboard mejorado."""
    print("\n🚀 Lanzando Dashboard Mejorado...")
    print("📊 URL: http://localhost:8501")
    print("⏹️  Para detener: Ctrl+C")
    print("-" * 50)
    
    try:
        # Cambiar al directorio del proyecto
        os.chdir(Path(__file__).parent)
        
        # Ejecutar Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "src/frontend/enhanced_dashboard.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard detenido")
    except Exception as e:
        print(f"❌ Error lanzando dashboard: {e}")

def main():
    """Función principal."""
    print("🔧 MCP Deployment Manager - Launcher")
    print("=" * 50)
    
    # Verificaciones pre-lanzamiento
    if not check_requirements():
        sys.exit(1)
    
    if not check_database():
        sys.exit(1)
    
    if not check_dashboard_file():
        sys.exit(1)
    
    # Lanzar dashboard
    launch_dashboard()

if __name__ == "__main__":
    main()