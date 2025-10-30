"""
Dashboard Streamlit para Gestión de Despliegues MCP.

Interfaz web especializada para gestionar despliegues, versiones y 
monitorear el estado de entornos .NET Core + Angular.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
import time
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

import streamlit as st
import pandas as pd

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.tools.registry import ToolRegistry
from src.tools.basic_tools import register_basic_tools
from src.utils.logging import setup_logging, get_logger


# Configuración de la página
st.set_page_config(
    page_title="MCP Deployment Manager",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para el dashboard
st.markdown("""
<style>
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .success-metric {
        border-left-color: #2ca02c;
    }
    .warning-metric {
        border-left-color: #ff7f0e;
    }
    .error-metric {
        border-left-color: #d62728;
    }
    .environment-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .deployment-status-success {
        background-color: #d4edda;
        color: #155724;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .deployment-status-failed {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .deployment-status-in_progress {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Configurar logging para la app
setup_logging(level="INFO", format_json=False)
logger = get_logger(__name__)


@st.cache_resource
def init_tool_registry():
    """Inicializa el registro de herramientas (cached)."""
    registry = ToolRegistry()
    
    # Ejecutar en un bucle de eventos si no existe uno
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Registrar herramientas
    loop.run_until_complete(register_basic_tools(registry))
    
    return registry


def display_header():
    """Muestra el encabezado principal del dashboard."""
    st.title("🚀 MCP Deployment Manager")
    st.markdown("**Dashboard de Gestión de Despliegues para .NET Core + Angular**")
    st.markdown("---")


def display_environment_overview():
    """Muestra el overview de todos los entornos."""
    st.header("🌍 Vista General de Entornos")
    
    registry = st.session_state.get('registry')
    if not registry:
        st.error("Error: No se pudo cargar el registro de herramientas")
        return
    
    # Obtener estado de cada entorno
    environments = ["dev", "pre", "prod"]
    env_data = {}
    
    try:
        loop = asyncio.get_event_loop()
        
        for env in environments:
            result = loop.run_until_complete(
                registry.execute_tool("get_environment_status", {"environment": env})
            )
            
            # Parsear resultado
            if hasattr(result[0], 'text'):
                data = json.loads(result[0].text)
            else:
                continue
                
            if "error" not in data:
                env_data[env] = data
    
    except Exception as e:
        st.warning(f"Algunos entornos no tienen datos aún: {str(e)}")
    
    # Mostrar cards de entornos
    cols = st.columns(3)
    
    for i, env in enumerate(environments):
        with cols[i]:
            env_name = env.upper()
            icon = "🟢" if env == "prod" else "🟡" if env == "pre" else "🔵"
            
            if env in env_data:
                data = env_data[env]
                current_version = (
                    data.get("current_deployment", {}).get("version", "N/A")
                    if data.get("current_deployment") else "N/A"
                )
                health = data.get("metrics", {}).get("health_status", "unknown")
                success_rate = data.get("metrics", {}).get("success_rate_percentage", 0)
                
                # Determinar color del health status
                health_color = "🟢" if health == "healthy" else "🟡" if health == "warning" else "🔴"
                
                st.markdown(f"""
                <div class="environment-card">
                    <h3>{icon} {env_name}</h3>
                    <p><strong>Versión Actual:</strong> {current_version}</p>
                    <p><strong>Estado:</strong> {health_color} {health.title()}</p>
                    <p><strong>Success Rate:</strong> {success_rate}%</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="environment-card">
                    <h3>{icon} {env_name}</h3>
                    <p><strong>Estado:</strong> Sin datos</p>
                    <p><em>Crear versiones y despliegues</em></p>
                </div>
                """, unsafe_allow_html=True)


def display_deployment_management():
    """Sección para gestionar despliegues."""
    st.header("📦 Gestión de Despliegues")
    
    registry = st.session_state.get('registry')
    if not registry:
        st.error("Error: No se pudo cargar el registro de herramientas")
        return
    
    # Tabs para diferentes funciones
    tab1, tab2, tab3 = st.tabs(["🆕 Nuevo Despliegue", "📋 Historial", "🔄 Estado"])
    
    with tab1:
        display_new_deployment_form(registry)
    
    with tab2:
        display_deployment_history(registry)
    
    with tab3:
        display_deployment_status_management(registry)


def display_new_deployment_form(registry):
    """Formulario para crear nuevo despliegue."""
    st.subheader("Registrar Nuevo Despliegue")
    
    col1, col2 = st.columns(2)
    
    with col1:
        environment = st.selectbox(
            "Entorno de Despliegue",
            ["dev", "pre", "prod"],
            key="new_deploy_env"
        )
        
        version = st.text_input(
            "Versión a Desplegar",
            placeholder="ej: 1.2.3",
            key="new_deploy_version"
        )
        
    with col2:
        deployed_by = st.text_input(
            "Responsable del Despliegue",
            placeholder="ej: DevOps Team",
            key="new_deploy_by"
        )
        
        branch = st.text_input(
            "Rama de Git (opcional)",
            placeholder="ej: main, release/1.2.3",
            key="new_deploy_branch"
        )
    
    notes = st.text_area(
        "Notas del Despliegue",
        placeholder="Descripción, cambios importantes, instrucciones especiales...",
        key="new_deploy_notes"
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if st.button("🚀 Iniciar Despliegue", type="primary"):
            if version and deployed_by:
                # Primero verificar si la versión existe, si no crearla
                try:
                    loop = asyncio.get_event_loop()
                    
                    # Intentar crear la versión si no existe
                    loop.run_until_complete(
                        registry.execute_tool("create_sample_version", {
                            "environment": environment,
                            "version": version,
                            "branch": branch or "main"
                        })
                    )
                    
                    # Registrar el despliegue
                    result = loop.run_until_complete(
                        registry.execute_tool("register_deployment", {
                            "environment": environment,
                            "version": version,
                            "deployed_by": deployed_by,
                            "notes": notes
                        })
                    )
                    
                    # Mostrar resultado
                    data = json.loads(result[0].text if hasattr(result[0], 'text') else result[0])
                    
                    if "error" in data:
                        st.error(f"❌ Error: {data['error']}")
                    else:
                        st.success(f"✅ Despliegue iniciado: {data['deployment_id'][:8]}...")
                        st.info(f"📝 {data['message']}")
                        
                        # Limpiar formulario
                        st.rerun()
                
                except Exception as e:
                    st.error(f"❌ Error iniciando despliegue: {str(e)}")
            else:
                st.warning("⚠️ Por favor completa versión y responsable")


def display_deployment_history(registry):
    """Muestra el historial de despliegues."""
    st.subheader("Historial de Despliegues")
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        filter_env = st.selectbox(
            "Filtrar por Entorno",
            ["Todos", "dev", "pre", "prod"],
            key="history_filter_env"
        )
        
        limit = st.slider(
            "Número de Despliegues",
            min_value=5,
            max_value=50,
            value=10,
            key="history_limit"
        )
    
    try:
        loop = asyncio.get_event_loop()
        
        # Parámetros para el filtro
        params = {"limit": limit}
        if filter_env != "Todos":
            params["environment"] = filter_env
        
        result = loop.run_until_complete(
            registry.execute_tool("get_deployment_history", params)
        )
        
        data = json.loads(result[0].text if hasattr(result[0], 'text') else result[0])
        
        if "error" in data:
            st.error(f"❌ Error: {data['error']}")
            return
        
        deployments = data.get("deployments", [])
        
        if not deployments:
            st.info("📭 No hay despliegues registrados aún")
            return
        
        # Crear DataFrame para mostrar
        df_data = []
        for dep in deployments:
            df_data.append({
                "ID": dep["deployment_id"][:8] + "...",
                "Entorno": dep["environment"].upper(),
                "Versión": dep["version"],
                "Estado": dep["status"],
                "Responsable": dep["deployed_by"],
                "Fecha": datetime.fromisoformat(dep["deployed_at"]).strftime("%d/%m/%Y %H:%M"),
                "Duración (min)": round(dep["duration_minutes"], 1) if dep["duration_minutes"] else "En progreso"
            })
        
        df = pd.DataFrame(df_data)
        
        # Mostrar métricas rápidas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total", len(deployments))
        
        with col2:
            successful = len([d for d in deployments if d["status"] == "success"])
            st.metric("Exitosos", successful)
        
        with col3:
            failed = len([d for d in deployments if d["status"] == "failed"])
            st.metric("Fallidos", failed, delta=f"-{failed}")
        
        with col4:
            in_progress = len([d for d in deployments if d["status"] == "in_progress"])
            st.metric("En Progreso", in_progress)
        
        # Tabla de despliegues con estilo
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
        
        # Gráfico de tendencias
        if len(deployments) > 1:
            st.subheader("📈 Tendencias de Despliegue")
            
            # Preparar datos para gráfico
            chart_data = []
            for dep in deployments:
                chart_data.append({
                    "Fecha": datetime.fromisoformat(dep["deployed_at"]).date(),
                    "Estado": dep["status"],
                    "Entorno": dep["environment"]
                })
            
            chart_df = pd.DataFrame(chart_data)
            
            # Gráfico de despliegues por día
            daily_counts = chart_df.groupby(["Fecha", "Estado"]).size().reset_index(name="Cantidad")
            
            fig = px.bar(
                daily_counts,
                x="Fecha",
                y="Cantidad",
                color="Estado",
                title="Despliegues por Día y Estado",
                color_discrete_map={
                    "success": "#2ca02c",
                    "failed": "#d62728",
                    "in_progress": "#ff7f0e"
                }
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"❌ Error obteniendo historial: {str(e)}")


def display_deployment_status_management(registry):
    """Gestión de estados de despliegue."""
    st.subheader("Gestionar Estados de Despliegue")
    
    # Obtener despliegues en progreso
    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            registry.execute_tool("get_deployment_history", {"limit": 20})
        )
        
        data = json.loads(result[0].text if hasattr(result[0], 'text') else result[0])
        deployments = data.get("deployments", [])
        
        # Filtrar despliegues en progreso o que se pueden actualizar
        active_deployments = [
            d for d in deployments 
            if d["status"] in ["in_progress", "pending"]
        ]
        
        if not active_deployments:
            st.info("📭 No hay despliegues activos para gestionar")
            return
        
        st.write(f"**{len(active_deployments)} despliegue(s) activo(s)**")
        
        for dep in active_deployments:
            with st.expander(f"🔄 {dep['environment'].upper()} - {dep['version']} ({dep['deployment_id'][:8]}...)"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Responsable:** {dep['deployed_by']}")
                    st.write(f"**Iniciado:** {datetime.fromisoformat(dep['deployed_at']).strftime('%d/%m/%Y %H:%M')}")
                    st.write(f"**Estado Actual:** {dep['status']}")
                    
                    new_notes = st.text_area(
                        "Notas Adicionales",
                        key=f"notes_{dep['deployment_id']}"
                    )
                
                with col2:
                    new_status = st.selectbox(
                        "Nuevo Estado",
                        ["success", "failed", "rollback"],
                        key=f"status_{dep['deployment_id']}"
                    )
                    
                    if st.button(f"Actualizar", key=f"update_{dep['deployment_id']}"):
                        try:
                            result = loop.run_until_complete(
                                registry.execute_tool("update_deployment_status", {
                                    "deployment_id": dep["deployment_id"],
                                    "status": new_status,
                                    "notes": new_notes
                                })
                            )
                            
                            update_data = json.loads(result[0].text if hasattr(result[0], 'text') else result[0])
                            
                            if "error" in update_data:
                                st.error(f"❌ Error: {update_data['error']}")
                            else:
                                st.success(f"✅ Estado actualizado a: {new_status}")
                                st.rerun()
                        
                        except Exception as e:
                            st.error(f"❌ Error actualizando: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error cargando despliegues activos: {str(e)}")


def display_version_management():
    """Sección para gestionar versiones."""
    st.header("📋 Gestión de Versiones")
    
    registry = st.session_state.get('registry')
    if not registry:
        st.error("Error: No se pudo cargar el registro de herramientas")
        return
    
    tab1, tab2 = st.tabs(["📖 Ver Versiones", "🔍 Comparar Versiones"])
    
    with tab1:
        display_version_list(registry)
    
    with tab2:
        display_version_comparison(registry)


def display_version_list(registry):
    """Lista versiones por entorno."""
    st.subheader("Versiones por Entorno")
    
    environment = st.selectbox(
        "Seleccionar Entorno",
        ["dev", "pre", "prod"],
        key="version_list_env"
    )
    
    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            registry.execute_tool("list_versions", {"environment": environment})
        )
        
        data = json.loads(result[0].text if hasattr(result[0], 'text') else result[0])
        
        if "error" in data:
            st.error(f"❌ Error: {data['error']}")
            return
        
        versions = data.get("versions", [])
        
        if not versions:
            st.info(f"📭 No hay versiones en {environment.upper()}")
            st.write("💡 **Tip:** Crea una nueva versión usando el formulario de despliegue")
            return
        
        st.write(f"**{len(versions)} versión(es) encontrada(s) en {environment.upper()}**")
        
        # Mostrar versiones en cards
        for version in versions:
            with st.expander(f"📦 {version['version']} - {version['branch']} ({version['created_at'][:10]})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Commit:** `{version['commit_hash']}`")
                    st.write(f"**Build:** {version['build_number']}")
                    st.write(f"**Creado:** {datetime.fromisoformat(version['created_at']).strftime('%d/%m/%Y %H:%M')}")
                
                with col2:
                    st.write(f"**Features:** {version['features_count']}")
                    st.write(f"**Bug Fixes:** {version['bug_fixes_count']}")
                    st.write(f"**Commits:** {version['commits_count']}")
                
                if st.button(f"Ver Detalles", key=f"details_{version['version']}_{environment}"):
                    display_version_details(registry, environment, version['version'])
    
    except Exception as e:
        st.error(f"❌ Error listando versiones: {str(e)}")


def display_version_details(registry, environment, version):
    """Muestra detalles de una versión específica."""
    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            registry.execute_tool("get_version_details", {
                "environment": environment,
                "version": version
            })
        )
        
        data = json.loads(result[0].text if hasattr(result[0], 'text') else result[0])
        
        if "error" in data:
            st.error(f"❌ Error: {data['error']}")
            return
        
        st.subheader(f"📋 Detalles de {version}")
        
        # Información básica
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Versión:** {data['version']}")
            st.write(f"**Rama:** {data['branch']}")
            st.write(f"**Commit:** `{data['commit_hash']}`")
        
        with col2:
            st.write(f"**Build:** {data['build_number']}")
            st.write(f"**Creado:** {datetime.fromisoformat(data['created_at']).strftime('%d/%m/%Y %H:%M')}")
        
        # Features
        if data.get('features'):
            st.subheader("✨ Nuevas Funcionalidades")
            for feature in data['features']:
                st.write(f"• {feature}")
        
        # Bug fixes
        if data.get('bug_fixes'):
            st.subheader("🐛 Correcciones")
            for fix in data['bug_fixes']:
                st.write(f"• {fix}")
        
        # Breaking changes
        if data.get('breaking_changes'):
            st.subheader("⚠️ Cambios Incompatibles")
            for change in data['breaking_changes']:
                st.write(f"• {change}")
        
        # Commits
        if data.get('commits'):
            st.subheader("📝 Commits Incluidos")
            
            commits_df = pd.DataFrame([
                {
                    "Hash": commit['hash'],
                    "Autor": commit['author'],
                    "Fecha": datetime.fromisoformat(commit['date']).strftime('%d/%m %H:%M'),
                    "Mensaje": commit['message'][:60] + "..." if len(commit['message']) > 60 else commit['message'],
                    "Archivos": commit['files_changed']
                }
                for commit in data['commits']
            ])
            
            st.dataframe(commits_df, hide_index=True, use_container_width=True)
    
    except Exception as e:
        st.error(f"❌ Error obteniendo detalles: {str(e)}")


def display_version_comparison(registry):
    """Comparar dos versiones."""
    st.subheader("Comparar Versiones")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        environment = st.selectbox(
            "Entorno",
            ["dev", "pre", "prod"],
            key="compare_env"
        )
    
    with col2:
        version1 = st.text_input(
            "Versión 1",
            placeholder="ej: 1.0.0",
            key="compare_v1"
        )
    
    with col3:
        version2 = st.text_input(
            "Versión 2",
            placeholder="ej: 1.1.0",
            key="compare_v2"
        )
    
    if st.button("🔍 Comparar Versiones") and version1 and version2:
        try:
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(
                registry.execute_tool("compare_versions", {
                    "environment": environment,
                    "version1": version1,
                    "version2": version2
                })
            )
            
            data = json.loads(result[0].text if hasattr(result[0], 'text') else result[0])
            
            if "error" in data:
                st.error(f"❌ Error: {data['error']}")
                return
            
            st.subheader(f"📊 Comparación: {version1} → {version2}")
            
            # Métricas de diferencias
            col1, col2, col3, col4 = st.columns(4)
            
            differences = data.get("differences", {})
            
            with col1:
                new_features = len(differences.get("new_features", []))
                st.metric("Nuevas Features", new_features, delta=new_features)
            
            with col2:
                new_fixes = len(differences.get("new_bug_fixes", []))
                st.metric("Bug Fixes", new_fixes, delta=new_fixes)
            
            with col3:
                breaking_changes = len(differences.get("new_breaking_changes", []))
                st.metric("Breaking Changes", breaking_changes, delta=breaking_changes if breaking_changes > 0 else None)
            
            with col4:
                commit_diff = differences.get("commits_difference", 0)
                st.metric("Diff. Commits", commit_diff, delta=commit_diff)
            
            # Detalles de las diferencias
            col1, col2 = st.columns(2)
            
            with col1:
                if differences.get("new_features"):
                    st.subheader("✨ Nuevas Funcionalidades")
                    for feature in differences["new_features"]:
                        st.write(f"• {feature}")
                
                if differences.get("new_bug_fixes"):
                    st.subheader("🐛 Nuevas Correcciones")
                    for fix in differences["new_bug_fixes"]:
                        st.write(f"• {fix}")
            
            with col2:
                if differences.get("new_breaking_changes"):
                    st.subheader("⚠️ Cambios Incompatibles")
                    for change in differences["new_breaking_changes"]:
                        st.write(f"• {change}")
                
                # Información de las versiones
                st.subheader("📋 Información de Versiones")
                version_details = data.get("version_details", {})
                
                if version1 in version_details:
                    v1_info = version_details[version1]
                    st.write(f"**{version1}:** {v1_info['commit_hash']} ({v1_info['branch']})")
                
                if version2 in version_details:
                    v2_info = version_details[version2]
                    st.write(f"**{version2}:** {v2_info['commit_hash']} ({v2_info['branch']})")
        
        except Exception as e:
            st.error(f"❌ Error comparando versiones: {str(e)}")


def main():
    """Función principal de la aplicación Streamlit."""
    
    # Inicializar estado de sesión
    if 'registry' not in st.session_state:
        try:
            st.session_state.registry = init_tool_registry()
            logger.info("Tool registry initialized in Streamlit session")
        except Exception as e:
            st.error(f"Error inicializando registro de herramientas: {str(e)}")
            st.session_state.registry = None
    
    # Mostrar encabezado
    display_header()
    
    # Sidebar para navegación
    st.sidebar.title("🧭 Navegación")
    page = st.sidebar.selectbox(
        "Selecciona una sección:",
        [
            "🌍 Vista General",
            "🚀 Gestión de Despliegues", 
            "📋 Gestión de Versiones",
            "📊 Métricas y Reports",
            "⚙️ Configuración"
        ]
    )
    
    # Mostrar contenido según la página seleccionada
    if page == "🌍 Vista General":
        display_environment_overview()
        
        st.markdown("---")
        st.subheader("🚀 Acciones Rápidas")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📦 Nuevo Despliegue", use_container_width=True):
                st.session_state['nav_to'] = "🚀 Gestión de Despliegues"
                st.rerun()
        
        with col2:
            if st.button("📋 Ver Versiones", use_container_width=True):
                st.session_state['nav_to'] = "📋 Gestión de Versiones"
                st.rerun()
        
        with col3:
            if st.button("📊 Ver Métricas", use_container_width=True):
                st.session_state['nav_to'] = "📊 Métricas y Reports"
                st.rerun()
    
    elif page == "🚀 Gestión de Despliegues":
        display_deployment_management()
    
    elif page == "📋 Gestión de Versiones":
        display_version_management()
    
    elif page == "📊 Métricas y Reports":
        st.header("📊 Métricas y Reports")
        st.info("🚧 Panel de métricas avanzadas en desarrollo")
        
        # Placeholder para métricas futuras
        st.subheader("📈 Próximas Funcionalidades")
        st.write("• Dashboard de performance de despliegues")
        st.write("• Reportes automáticos de release notes")
        st.write("• Análisis de tendencias por entorno")
        st.write("• Integración con métricas de aplicación")
    
    elif page == "⚙️ Configuración":
        st.header("⚙️ Configuración del Sistema")
        st.info("🚧 Panel de configuración en desarrollo")
        
        st.subheader("🔧 Configuraciones Disponibles")
        st.write("• Configuración de entornos")
        st.write("• Integración con repositorios Git")
        st.write("• Configuración de notificaciones")
        st.write("• Gestión de usuarios y permisos")
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🚀 MCP Deployment Manager v1.0.0**")
    st.sidebar.markdown("Gestión Profesional de Despliegues")
    
    # Info del sistema
    registry = st.session_state.get('registry')
    if registry:
        st.sidebar.write(f"🛠️ Herramientas: {registry.get_tools_count()}")
    
    st.sidebar.markdown("Creado con ❤️ usando Streamlit + MCP")


if __name__ == "__main__":
    main()