"""
Script para ejecutar el dashboard multi-organización.
"""

import os
import sys
import subprocess

def main():
    """Ejecuta el dashboard multi-organización."""
    
    # Cambiar al directorio del proyecto
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Agregar src/frontend al path
    frontend_dir = os.path.join(project_dir, 'src', 'frontend')
    sys.path.insert(0, frontend_dir)
    
    # Comando para ejecutar Streamlit
    python_exe = os.path.join('.venv', 'Scripts', 'python.exe')
    streamlit_cmd = [
        python_exe, '-m', 'streamlit', 'run', 
        'src/frontend/multi_org_dashboard.py',
        '--server.port=8503',
        '--server.headless=true',
        '--browser.gatherUsageStats=false'
    ]
    
    print("🚀 Iniciando Dashboard Multi-Organización...")
    print(f"📂 Directorio: {project_dir}")
    print(f"🌐 URL: http://localhost:8503")
    print("-" * 50)
    
    try:
        subprocess.run(streamlit_cmd, check=True)
    except KeyboardInterrupt:
        print("\n✅ Dashboard detenido por el usuario.")
    except Exception as e:
        print(f"❌ Error al ejecutar dashboard: {e}")

if __name__ == "__main__":
    main()