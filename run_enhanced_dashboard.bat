@echo off
REM Script para lanzar el Dashboard Mejorado de MCP Deployment Manager en Windows

echo.
echo ================================================================
echo  MCP Deployment Manager - Dashboard Mejorado
echo ================================================================
echo.

REM Verificar que Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado o no está en el PATH
    echo    Instala Python 3.9+ desde https://python.org
    pause
    exit /b 1
)

REM Verificar que el entorno virtual existe
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Entorno virtual no encontrado
    echo    Ejecuta: python -m venv venv
    pause
    exit /b 1
)

REM Activar entorno virtual
echo 🔧 Activando entorno virtual...
call venv\Scripts\activate.bat

REM Verificar que las dependencias están instaladas
echo 🔍 Verificando dependencias...
python -c "import streamlit, plotly, pandas" >nul 2>&1
if errorlevel 1 (
    echo ❌ Dependencias no instaladas
    echo    Ejecuta: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Verificar que la base de datos existe
if not exist "data\deployments.db" (
    echo ❌ Base de datos no encontrada
    echo    Ejecuta: python scripts\generate_hierarchical_apps.py
    pause
    exit /b 1
)

REM Verificar que el dashboard existe
if not exist "src\frontend\enhanced_dashboard.py" (
    echo ❌ Dashboard mejorado no encontrado
    pause
    exit /b 1
)

echo ✅ Todas las verificaciones pasaron
echo.

REM Lanzar dashboard
echo 🚀 Lanzando Dashboard Mejorado...
echo 📊 URL: http://localhost:8501
echo ⏹️  Para detener: Ctrl+C
echo.
echo ================================================================
echo.

streamlit run src\frontend\enhanced_dashboard.py --server.port 8501 --server.address localhost --browser.gatherUsageStats false

echo.
echo 👋 Dashboard detenido
pause