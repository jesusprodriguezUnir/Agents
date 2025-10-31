"""
Dashboard jerárquico para gestión de despliegues multi-aplicación.
Adaptado para la nueva estructura: aplicaciones -> componentes -> versiones -> despliegues
"""

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Importar herramientas del dashboard
from dashboard_tools import dashboard_tools

# Configuración de página
st.set_page_config(
    page_title="🚀 MCP Deployment Manager",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    .success-status { color: #28a745; font-weight: bold; }
    .failed-status { color: #dc3545; font-weight: bold; }
    .pending-status { color: #ffc107; font-weight: bold; }
    .info-box { 
        background: #e3f2fd; 
        padding: 1rem; 
        border-radius: 8px; 
        margin: 1rem 0;
        border-left: 4px solid #2196f3;
    }
</style>
""", unsafe_allow_html=True)

def get_database_connection():
    """Obtiene conexión a la base de datos."""
    return sqlite3.connect("data/deployments.db")

def load_applications():
    """Carga aplicaciones principales."""
    conn = get_database_connection()
    df = pd.read_sql_query("""
        SELECT id, name, description, owner_team, created_at
        FROM applications 
        ORDER BY name
    """, conn)
    conn.close()
    return df

def load_components():
    """Carga componentes con información de aplicación."""
    conn = get_database_connection()
    df = pd.read_sql_query("""
        SELECT 
            ac.*,
            a.name as application_name,
            a.description as application_description
        FROM application_components ac
        JOIN applications a ON ac.application_id = a.id
        ORDER BY a.name, ac.type
    """, conn)
    conn.close()
    return df

def load_versions():
    """Carga versiones con información completa."""
    conn = get_database_connection()
    df = pd.read_sql_query("""
        SELECT 
            v.*,
            ac.name as component_name,
            ac.type as component_type,
            a.name as application_name
        FROM versions v
        JOIN application_components ac ON v.component_id = ac.id
        JOIN applications a ON ac.application_id = a.id
        ORDER BY a.name, ac.type, v.created_at DESC
    """, conn)
    conn.close()
    return df

def load_deployments():
    """Carga despliegues con información completa."""
    conn = get_database_connection()
    df = pd.read_sql_query("""
        SELECT 
            d.*,
            v.version,
            ac.name as component_name,
            ac.type as component_type,
            a.name as application_name
        FROM deployments d
        JOIN versions v ON d.version_id = v.id
        JOIN application_components ac ON d.component_id = ac.id
        JOIN applications a ON ac.application_id = a.id
        ORDER BY d.deployed_at DESC
    """, conn)
    conn.close()
    return df

def show_overview():
    """Muestra el resumen general del sistema."""
    st.markdown('<div class="main-header"><h1>🎯 Resumen General</h1></div>', unsafe_allow_html=True)
    
    # Métricas principales
    apps_df = load_applications()
    components_df = load_components()
    versions_df = load_versions()
    deployments_df = load_deployments()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏢 Aplicaciones", len(apps_df))
    
    with col2:
        st.metric("📦 Componentes", len(components_df))
    
    with col3:
        st.metric("🔖 Versiones", len(versions_df))
    
    with col4:
        st.metric("🚀 Despliegues", len(deployments_df))
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Componentes por Aplicación")
        if not components_df.empty:
            comp_counts = components_df.groupby('application_name').size().reset_index(name='count')
            fig = px.bar(comp_counts, x='application_name', y='count', 
                        title="Componentes por Aplicación")
            fig.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Despliegues por Entorno")
        if not deployments_df.empty:
            env_counts = deployments_df['environment'].value_counts().reset_index()
            env_counts.columns = ['environment', 'count']
            fig = px.pie(env_counts, values='count', names='environment',
                        title="Distribución por Entorno")
            st.plotly_chart(fig, use_container_width=True)
    
    # Estado de despliegues
    st.subheader("📈 Estado de Despliegues Recientes")
    if not deployments_df.empty:
        status_counts = deployments_df['status'].value_counts().reset_index()
        status_counts.columns = ['status', 'count']
        
        colors = {'success': '#28a745', 'failed': '#dc3545', 'pending': '#ffc107'}
        fig = px.bar(status_counts, x='status', y='count',
                    color='status', color_discrete_map=colors,
                    title="Estado de Despliegues")
        st.plotly_chart(fig, use_container_width=True)

def show_applications():
    """Muestra la gestión de aplicaciones principales."""
    st.markdown('<div class="main-header"><h1>🏢 Aplicaciones Principales</h1></div>', unsafe_allow_html=True)
    
    apps_df = load_applications()
    components_df = load_components()
    
    if apps_df.empty:
        st.warning("📝 No hay aplicaciones registradas")
        return
    
    # Lista de aplicaciones
    st.subheader("📱 Lista de Aplicaciones")
    
    for _, app in apps_df.iterrows():
        with st.expander(f"🏢 {app['name']}", expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Descripción:** {app['description']}")
                st.write(f"**Equipo:** {app['owner_team']}")
                st.write(f"**Creado:** {app['created_at'][:10] if app['created_at'] else 'N/A'}")
            
            with col2:
                # Componentes de esta aplicación
                app_components = components_df[components_df['application_id'] == app['id']]
                
                st.write("**Componentes:**")
                for _, comp in app_components.iterrows():
                    icon = "🌐" if comp['type'] == 'frontend' else "⚙️"
                    st.write(f"{icon} {comp['type'].capitalize()}")
                    if comp['repository_url']:
                        st.write(f"   📂 [{comp['repository_url'][:50]}...]({comp['repository_url']})")

def show_components():
    """Muestra la gestión de componentes."""
    st.markdown('<div class="main-header"><h1>📦 Componentes</h1></div>', unsafe_allow_html=True)
    
    components_df = load_components()
    
    if components_df.empty:
        st.warning("📝 No hay componentes registrados")
        return
    
    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        app_filter = st.selectbox(
            "Filtrar por aplicación",
            ["Todas"] + list(components_df['application_name'].unique())
        )
    
    with col2:
        type_filter = st.selectbox(
            "Filtrar por tipo",
            ["Todos", "frontend", "backend"]
        )
    
    # Aplicar filtros
    filtered_df = components_df.copy()
    
    if app_filter != "Todas":
        filtered_df = filtered_df[filtered_df['application_name'] == app_filter]
    
    if type_filter != "Todos":
        filtered_df = filtered_df[filtered_df['type'] == type_filter]
    
    # Mostrar componentes
    for _, comp in filtered_df.iterrows():
        icon = "🌐" if comp['type'] == 'frontend' else "⚙️"
        
        with st.expander(f"{icon} {comp['name']}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Aplicación:** {comp['application_name']}")
                st.write(f"**Tipo:** {comp['type'].capitalize()}")
                
                if comp['tech_stack']:
                    tech_list = comp['tech_stack'].split(',')
                    st.write(f"**Tecnologías:** {', '.join(tech_list)}")
                
                if comp['repository_url']:
                    st.write(f"**Repositorio:** [{comp['repository_url']}]({comp['repository_url']})")
            
            with col2:
                if comp['health_check_url']:
                    st.write(f"**Health Check:** [🔗]({comp['health_check_url']})")

def show_versions():
    """Muestra la gestión de versiones."""
    st.markdown('<div class="main-header"><h1>🔖 Versiones</h1></div>', unsafe_allow_html=True)
    
    versions_df = load_versions()
    
    if versions_df.empty:
        st.warning("📝 No hay versiones registradas")
        return
    
    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        app_filter = st.selectbox(
            "Filtrar por aplicación",
            ["Todas"] + list(versions_df['application_name'].unique()),
            key="version_app_filter"
        )
    
    with col2:
        type_filter = st.selectbox(
            "Filtrar por tipo",
            ["Todos", "frontend", "backend"],
            key="version_type_filter"
        )
    
    # Aplicar filtros
    filtered_df = versions_df.copy()
    
    if app_filter != "Todas":
        filtered_df = filtered_df[filtered_df['application_name'] == app_filter]
    
    if type_filter != "Todos":
        filtered_df = filtered_df[filtered_df['component_type'] == type_filter]
    
    # Mostrar versiones
    for _, version in filtered_df.iterrows():
        icon = "🌐" if version['component_type'] == 'frontend' else "⚙️"
        
        with st.expander(f"{icon} {version['application_name']} ({version['component_type']}) - v{version['version']}", expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Componente:** {version['component_name']}")
                st.write(f"**Rama:** {version['branch']}")
                st.write(f"**Build:** {version['build_number']}")
                st.write(f"**Commit:** `{version['commit_hash'][:8]}...`")
                
                if version['features']:
                    features = version['features'].split(',')
                    st.write("**Características:**")
                    for feature in features:
                        st.write(f"  • {feature}")
            
            with col2:
                st.write(f"**Creado:** {version['created_at'][:10] if version['created_at'] else 'N/A'}")
                
                if version['bug_fixes']:
                    fixes = version['bug_fixes'].split(',')
                    st.write("**Correcciones:**")
                    for fix in fixes:
                        st.write(f"  🐛 {fix}")

def show_deployments():
    """Muestra la gestión de despliegues."""
    st.markdown('<div class="main-header"><h1>🚀 Despliegues</h1></div>', unsafe_allow_html=True)
    
    deployments_df = load_deployments()
    
    if deployments_df.empty:
        st.warning("📝 No hay despliegues registrados")
        return
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        app_filter = st.selectbox(
            "Filtrar por aplicación",
            ["Todas"] + list(deployments_df['application_name'].unique()),
            key="deploy_app_filter"
        )
    
    with col2:
        env_filter = st.selectbox(
            "Filtrar por entorno",
            ["Todos"] + list(deployments_df['environment'].unique()),
            key="deploy_env_filter"
        )
    
    with col3:
        status_filter = st.selectbox(
            "Filtrar por estado",
            ["Todos"] + list(deployments_df['status'].unique()),
            key="deploy_status_filter"
        )
    
    # Aplicar filtros
    filtered_df = deployments_df.copy()
    
    if app_filter != "Todas":
        filtered_df = filtered_df[filtered_df['application_name'] == app_filter]
    
    if env_filter != "Todos":
        filtered_df = filtered_df[filtered_df['environment'] == env_filter]
    
    if status_filter != "Todos":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    
    # Mostrar despliegues
    for _, deploy in filtered_df.iterrows():
        status_class = f"{deploy['status']}-status"
        icon = "🌐" if deploy['component_type'] == 'frontend' else "⚙️"
        env_icon = {"dev": "🔧", "pre": "🧪", "prod": "🌟"}.get(deploy['environment'], "📦")
        
        with st.expander(f"{icon} {deploy['application_name']} ({deploy['component_type']}) → {env_icon} {deploy['environment']} - v{deploy['version']}", expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Componente:** {deploy['component_name']}")
                st.write(f"**Versión:** {deploy['version']}")
                st.write(f"**Entorno:** {deploy['environment'].upper()}")
                st.markdown(f"**Estado:** <span class='{status_class}'>{deploy['status'].upper()}</span>", unsafe_allow_html=True)
                
                if deploy['notes']:
                    st.write(f"**Notas:** {deploy['notes']}")
            
            with col2:
                st.write(f"**Desplegado por:** {deploy['deployed_by']}")
                st.write(f"**Fecha:** {deploy['deployed_at'][:16] if deploy['deployed_at'] else 'N/A'}")

def show_create_forms():
    """Muestra formularios de creación."""
    st.markdown('<div class="main-header"><h1>➕ Crear Nuevo</h1></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🏢 Nueva Aplicación", "📦 Nuevo Componente", "🔖 Nueva Versión"])
    
    with tab1:
        st.subheader("🏢 Crear Nueva Aplicación")
        st.markdown('<div class="info-box">💡 Una aplicación es el contenedor principal que agrupa componentes frontend y backend relacionados.</div>', unsafe_allow_html=True)
        
        with st.form("create_application"):
            col1, col2 = st.columns(2)
            
            with col1:
                app_id = st.text_input("ID de Aplicación*", placeholder="ej: mi-aplicacion")
                app_name = st.text_input("Nombre*", placeholder="ej: Mi Aplicación")
                owner_team = st.text_input("Equipo Propietario", placeholder="ej: Equipo Backend")
            
            with col2:
                app_description = st.text_area("Descripción", placeholder="Describe el propósito de la aplicación...")
            
            submitted = st.form_submit_button("🏗️ Crear Aplicación")
            
            if submitted:
                if app_id and app_name:
                    try:
                        result = dashboard_tools.create_application(
                            app_id=app_id,
                            name=app_name,
                            app_type="",  # No aplicable en estructura jerárquica
                            description=app_description,
                            owner_team=owner_team
                        )
                        
                        if result["success"]:
                            st.success(f"✅ {result['message']}")
                            st.balloons()
                        else:
                            st.error(f"❌ {result['message']}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.error("❌ Por favor completa los campos obligatorios (*)")

# Configuración del sidebar
st.sidebar.header("🎛️ Navegación")

# Menú principal
page = st.sidebar.selectbox(
    "Selecciona una página",
    ["🎯 Resumen", "🏢 Aplicaciones", "📦 Componentes", "🔖 Versiones", "🚀 Despliegues", "➕ Crear Nuevo"]
)

# Mostrar página seleccionada
if page == "🎯 Resumen":
    show_overview()
elif page == "🏢 Aplicaciones":
    show_applications()
elif page == "📦 Componentes":
    show_components()
elif page == "🔖 Versiones":
    show_versions()
elif page == "🚀 Despliegues":
    show_deployments()
elif page == "➕ Crear Nuevo":
    show_create_forms()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8em;'>
    🚀 MCP Deployment Manager<br>
    Estructura Jerárquica<br>
    <em>Aplicaciones → Componentes → Versiones</em>
</div>
""", unsafe_allow_html=True)