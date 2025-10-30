"""
Dashboard de gestión de despliegues multi-aplicación.

Interfaz Streamlit actualizada para soportar múltiples aplicaciones
por entorno y gestión granular de versiones y despliegues.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
import json
from typing import Dict, List, Any

# Importar herramientas del dashboard
from dashboard_tools import dashboard_tools

# Configuración de página
st.set_page_config(
    page_title="MCP Deployment Manager",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🚀 MCP Deployment Manager")
st.markdown("**Sistema de Gestión de Despliegues Multi-Aplicación**")

# Conexión a la base de datos
@st.cache_resource
def get_database_connection():
    """Obtiene conexión a la base de datos."""
    return sqlite3.connect("data/deployments.db", check_same_thread=False)

def load_applications():
    """Carga todas las aplicaciones."""
    conn = get_database_connection()
    df = pd.read_sql_query("""
        SELECT id, name, type, description, owner_team, 
               tech_stack, created_at
        FROM applications 
        ORDER BY name
    """, conn)
    return df

def load_app_versions(app_id: str = None):
    """Carga versiones por aplicación."""
    conn = get_database_connection()
    
    if app_id:
        query = """
            SELECT v.*, a.name as app_name
            FROM versions v
            JOIN applications a ON v.application_id = a.id
            WHERE v.application_id = ?
            ORDER BY v.created_at DESC
        """
        df = pd.read_sql_query(query, conn, params=[app_id])
    else:
        query = """
            SELECT v.*, a.name as app_name
            FROM versions v
            JOIN applications a ON v.application_id = a.id
            ORDER BY v.created_at DESC
        """
        df = pd.read_sql_query(query, conn)
    
    return df

def load_deployments_by_app(app_id: str = None, environment: str = None):
    """Carga despliegues filtrados por aplicación y entorno."""
    conn = get_database_connection()
    
    query = """
        SELECT d.*, v.version, a.name as app_name
        FROM deployments d
        JOIN versions v ON d.version_id = v.id
        JOIN applications a ON d.application_id = a.id
    """
    
    params = []
    conditions = []
    
    if app_id:
        conditions.append("d.application_id = ?")
        params.append(app_id)
    
    if environment:
        conditions.append("d.environment = ?")
        params.append(environment)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY d.deployed_at DESC"
    
    df = pd.read_sql_query(query, conn, params=params)
    return df

def load_environment_overview():
    """Carga vista general de todos los entornos."""
    conn = get_database_connection()
    
    # Obtener aplicaciones con su último despliegue por entorno
    query = """
        WITH latest_deployments AS (
            SELECT 
                d.application_id,
                d.environment,
                d.status,
                v.version,
                d.deployed_at,
                ROW_NUMBER() OVER (
                    PARTITION BY d.application_id, d.environment 
                    ORDER BY d.deployed_at DESC
                ) as rn
            FROM deployments d
            JOIN versions v ON d.version_id = v.id
        )
        SELECT 
            a.id as app_id,
            a.name as app_name,
            a.type as app_type,
            ld.environment,
            ld.version as current_version,
            ld.status as last_status,
            ld.deployed_at as last_deployment
        FROM applications a
        LEFT JOIN latest_deployments ld ON a.id = ld.application_id AND ld.rn = 1
        ORDER BY a.name, 
                 CASE ld.environment 
                     WHEN 'dev' THEN 1 
                     WHEN 'pre' THEN 2 
                     WHEN 'prod' THEN 3 
                 END
    """
    
    df = pd.read_sql_query(query, conn)
    return df

# Sidebar para filtros
st.sidebar.header("🎛️ Filtros")

# Cargar aplicaciones para el filtro
apps_df = load_applications()
app_options = ["Todas las aplicaciones"] + apps_df['name'].tolist()
selected_app_name = st.sidebar.selectbox("Aplicación", app_options)

selected_app_id = None
if selected_app_name != "Todas las aplicaciones":
    selected_app_id = apps_df[apps_df['name'] == selected_app_name]['id'].iloc[0]

# Filtro de entorno
environment_options = ["Todos los entornos", "dev", "pre", "prod"]
selected_environment = st.sidebar.selectbox("Entorno", environment_options)
if selected_environment == "Todos los entornos":
    selected_environment = None

# Tabs principales
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏠 Vista General", 
    "📱 Aplicaciones", 
    "🏷️ Versiones", 
    "🚀 Despliegues",
    "📊 Métricas",
    "➕ Crear Nuevo"
])

with tab1:
    st.header("Vista General de Entornos")
    
    # Cargar datos de vista general
    overview_df = load_environment_overview()
    
    if not overview_df.empty:
        # Crear una tabla pivote para mostrar el estado por entorno
        col1, col2, col3 = st.columns(3)
        
        # Métricas por entorno
        environments = ['dev', 'pre', 'prod']
        env_names = {'dev': 'Desarrollo', 'pre': 'Pre-producción', 'prod': 'Producción'}
        
        for i, env in enumerate(environments):
            with [col1, col2, col3][i]:
                env_data = overview_df[overview_df['environment'] == env]
                
                total_apps = len(apps_df)
                deployed_apps = len(env_data)
                success_deployments = len(env_data[env_data['last_status'] == 'success'])
                
                st.metric(
                    label=f"🌍 {env_names[env]}",
                    value=f"{deployed_apps}/{total_apps}",
                    delta=f"{success_deployments} exitosos"
                )
                
                # Estado de aplicaciones en este entorno
                if not env_data.empty:
                    st.markdown("**Aplicaciones:**")
                    for _, app in env_data.iterrows():
                        status_icon = {
                            'success': '✅',
                            'failed': '❌',
                            'in_progress': '🔄',
                            'rollback': '↩️'
                        }.get(app['last_status'], '❓')
                        
                        st.markdown(f"{status_icon} {app['app_name']} `{app['current_version']}`")
                else:
                    st.markdown("*Sin despliegues*")
        
        # Tabla detallada de estado por aplicación y entorno
        st.subheader("Estado Detallado por Aplicación")
        
        # Crear tabla pivote
        if not overview_df.empty:
            pivot_data = []
            
            for app_name in apps_df['name'].unique():
                row = {"Aplicación": app_name}
                app_data = overview_df[overview_df['app_name'] == app_name]
                
                for env in environments:
                    env_app_data = app_data[app_data['environment'] == env]
                    if not env_app_data.empty:
                        status = env_app_data.iloc[0]['last_status']
                        version = env_app_data.iloc[0]['current_version']
                        status_icon = {
                            'success': '✅',
                            'failed': '❌', 
                            'in_progress': '🔄',
                            'rollback': '↩️'
                        }.get(status, '❓')
                        row[env_names[env]] = f"{status_icon} {version}"
                    else:
                        row[env_names[env]] = "⚪ Sin despliegue"
                
                pivot_data.append(row)
            
            pivot_df = pd.DataFrame(pivot_data)
            st.dataframe(pivot_df, width='stretch')

with tab2:
    st.header("📱 Gestión de Aplicaciones")
    
    # Mostrar aplicaciones
    if not apps_df.empty:
        for _, app in apps_df.iterrows():
            with st.expander(f"🔧 {app['name']} ({app['type']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**ID:** `{app['id']}`")
                    st.markdown(f"**Descripción:** {app['description']}")
                    st.markdown(f"**Equipo:** {app['owner_team']}")
                
                with col2:
                    # Cargar stack tecnológico
                    try:
                        tech_stack = json.loads(app['tech_stack'])
                        st.markdown("**Stack Tecnológico:**")
                        for tech in tech_stack:
                            st.markdown(f"• {tech}")
                    except:
                        st.markdown("**Stack Tecnológico:** No especificado")
                
                # Estadísticas de la aplicación
                app_versions = load_app_versions(app['id'])
                app_deployments = load_deployments_by_app(app['id'])
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Versiones", len(app_versions))
                col2.metric("Despliegues", len(app_deployments))
                col3.metric("Últimos 30 días", len(app_deployments[
                    pd.to_datetime(app_deployments['deployed_at']) > 
                    (datetime.now() - timedelta(days=30))
                ]) if not app_deployments.empty else 0)

with tab3:
    st.header("🏷️ Gestión de Versiones")
    
    # Cargar versiones según filtros
    versions_df = load_app_versions(selected_app_id)
    
    if not versions_df.empty:
        # Filtros adicionales
        col1, col2 = st.columns(2)
        with col1:
            if selected_app_id:
                st.info(f"Mostrando versiones de: **{selected_app_name}**")
            else:
                st.info("Mostrando versiones de todas las aplicaciones")
        
        # Tabla de versiones
        display_df = versions_df[['app_name', 'version', 'branch', 'commit_hash', 'build_number', 'created_at']].copy()
        display_df['commit_hash'] = display_df['commit_hash'].str[:8]
        display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        
        st.dataframe(display_df, width='stretch')
        
        # Gráfico de versiones por aplicación
        if not selected_app_id:  # Solo si vemos todas las apps
            st.subheader("Distribución de Versiones por Aplicación")
            version_counts = versions_df.groupby('app_name').size().reset_index(name='count')
            
            fig = px.bar(
                version_counts, 
                x='app_name', 
                y='count',
                title="Número de Versiones por Aplicación",
                labels={'app_name': 'Aplicación', 'count': 'Número de Versiones'}
            )
            st.plotly_chart(fig, width='stretch')

with tab4:
    st.header("🚀 Gestión de Despliegues")
    
    # Cargar despliegues según filtros
    deployments_df = load_deployments_by_app(selected_app_id, selected_environment)
    
    if not deployments_df.empty:
        # Información de filtros aplicados
        filter_info = []
        if selected_app_id:
            filter_info.append(f"Aplicación: **{selected_app_name}**")
        if selected_environment:
            filter_info.append(f"Entorno: **{selected_environment}**")
        
        if filter_info:
            st.info(" | ".join(filter_info))
        
        # Métricas de despliegues
        col1, col2, col3, col4 = st.columns(4)
        
        total_deployments = len(deployments_df)
        successful = len(deployments_df[deployments_df['status'] == 'success'])
        failed = len(deployments_df[deployments_df['status'] == 'failed'])
        in_progress = len(deployments_df[deployments_df['status'] == 'in_progress'])
        
        col1.metric("Total", total_deployments)
        col2.metric("Exitosos", successful, f"{successful/total_deployments*100:.1f}%")
        col3.metric("Fallidos", failed, f"{failed/total_deployments*100:.1f}%")
        col4.metric("En Progreso", in_progress)
        
        # Tabla de despliegues
        st.subheader("Historial de Despliegues")
        
        display_df = deployments_df[[
            'app_name', 'environment', 'version', 'status', 
            'deployed_by', 'deployed_at', 'notes'
        ]].copy()
        
        display_df['deployed_at'] = pd.to_datetime(display_df['deployed_at']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Colorear por estado
        def color_status(val):
            colors = {
                'success': 'background-color: #d4edda',
                'failed': 'background-color: #f8d7da',
                'in_progress': 'background-color: #d1ecf1',
                'rollback': 'background-color: #fff3cd'
            }
            return colors.get(val, '')
        
        styled_df = display_df.style.map(color_status, subset=['status'])
        st.dataframe(styled_df, width='stretch')
        
        # Sección para actualizar estado de despliegues
        if not deployments_df.empty:
            st.subheader("🔄 Actualizar Estado de Despliegue")
            
            with st.form("update_deployment_status"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Obtener despliegues en progreso o pendientes
                    active_deployments = deployments_df[
                        deployments_df['status'].isin(['pending', 'in_progress'])
                    ]
                    
                    if not active_deployments.empty:
                        deployment_options = []
                        for _, deploy in active_deployments.iterrows():
                            label = f"{deploy['app_name']} v{deploy['version']} ({deploy['environment']}) - {deploy['status']}"
                            deployment_options.append((deploy['id'], label))
                        
                        selected_deployment = st.selectbox(
                            "Despliegue a Actualizar",
                            options=[opt[0] for opt in deployment_options],
                            format_func=lambda x: next(opt[1] for opt in deployment_options if opt[0] == x)
                        )
                    else:
                        st.info("No hay despliegues activos para actualizar")
                        selected_deployment = None
                
                with col2:
                    new_status = st.selectbox(
                        "Nuevo Estado",
                        options=['in_progress', 'success', 'failed', 'rollback'],
                        format_func=lambda x: {
                            'in_progress': '🔄 En Progreso',
                            'success': '✅ Exitoso',
                            'failed': '❌ Fallido',
                            'rollback': '↩️ Rollback'
                        }.get(x, x)
                    )
                
                with col3:
                    update_notes = st.text_area(
                        "Notas de Actualización",
                        help="Información sobre el cambio de estado"
                    )
                
                submitted = st.form_submit_button("🔄 Actualizar Estado", type="secondary")
                
                if submitted and selected_deployment:
                    result = dashboard_tools.update_deployment_status(
                        deployment_id=selected_deployment,
                        status=new_status,
                        notes=update_notes
                    )
                    
                    if result["success"]:
                        st.success(f"✅ {result['message']}")
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")
        
    else:
        st.info("No se encontraron despliegues con los filtros aplicados.")

with tab5:
    st.header("📊 Métricas y Análisis")
    
    # Cargar todos los despliegues para métricas
    all_deployments_df = load_deployments_by_app()
    
    if not all_deployments_df.empty:
        # Preparar datos
        all_deployments_df['deployed_at'] = pd.to_datetime(all_deployments_df['deployed_at'])
        all_deployments_df['date'] = all_deployments_df['deployed_at'].dt.date
        
        # Métricas temporales
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Despliegues por Día")
            daily_deployments = all_deployments_df.groupby('date').size().reset_index(name='count')
            daily_deployments['date'] = pd.to_datetime(daily_deployments['date'])
            
            fig = px.line(
                daily_deployments,
                x='date',
                y='count',
                title="Tendencia de Despliegues Diarios"
            )
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            st.subheader("Despliegues por Estado")
            status_counts = all_deployments_df['status'].value_counts()
            
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Distribución de Estados de Despliegue"
            )
            st.plotly_chart(fig, width='stretch')
        
        # Métricas por aplicación y entorno
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Despliegues por Aplicación")
            app_counts = all_deployments_df['app_name'].value_counts().head(10)
            
            fig = px.bar(
                x=app_counts.values,
                y=app_counts.index,
                orientation='h',
                title="Top 10 Aplicaciones por Número de Despliegues"
            )
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            st.subheader("Despliegues por Entorno")
            env_counts = all_deployments_df['environment'].value_counts()
            
            fig = px.bar(
                x=env_counts.index,
                y=env_counts.values,
                title="Despliegues por Entorno"
            )
            st.plotly_chart(fig, width='stretch')
        
        # Tabla de rendimiento por aplicación
        st.subheader("Rendimiento por Aplicación")
        
        app_performance = all_deployments_df.groupby('app_name').agg({
            'id': 'count',
            'status': lambda x: (x == 'success').sum(),
            'deployed_at': 'max'
        }).reset_index()
        
        app_performance.columns = ['Aplicación', 'Total Despliegues', 'Exitosos', 'Último Despliegue']
        app_performance['Tasa Éxito (%)'] = (
            app_performance['Exitosos'] / app_performance['Total Despliegues'] * 100
        ).round(1)
        app_performance['Último Despliegue'] = pd.to_datetime(
            app_performance['Último Despliegue']
        ).dt.strftime('%Y-%m-%d')
        
        st.dataframe(app_performance, width='stretch')

with tab6:
    st.header("➕ Crear Nuevo")
    
    # Sub-tabs para diferentes tipos de creación
    create_tab1, create_tab2, create_tab3 = st.tabs([
        "📱 Nueva Aplicación",
        "🏷️ Nueva Versión", 
        "🚀 Nuevo Despliegue"
    ])
    
    with create_tab1:
        st.subheader("📱 Crear Nueva Aplicación")
        
        with st.form("create_application_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                app_id = st.text_input(
                    "ID de Aplicación*",
                    help="Identificador único (ej: payment-service, user-api)"
                )
                app_name = st.text_input(
                    "Nombre de Aplicación*",
                    help="Nombre descriptivo (ej: Payment Service)"
                )
                app_type = st.selectbox(
                    "Tipo de Aplicación*",
                    options=dashboard_tools.get_application_type_choices(),
                    format_func=lambda x: {
                        'frontend': '🌐 Frontend (Angular, React)',
                        'backend': '⚙️ Backend (API, Servidor)',
                        'microservice': '🔧 Microservicio',
                        'database': '💾 Base de Datos',
                        'infrastructure': '🏗️ Infraestructura'
                    }.get(x, x)
                )
            
            with col2:
                owner_team = st.text_input(
                    "Equipo Responsable*",
                    help="Equipo que mantiene la aplicación"
                )
                repository_url = st.text_input(
                    "URL del Repositorio",
                    help="Enlace al repositorio Git (opcional)"
                )
                health_check_url = st.text_input(
                    "URL de Health Check",
                    help="Endpoint para verificar salud (opcional)"
                )
            
            description = st.text_area(
                "Descripción",
                help="Descripción detallada de la aplicación"
            )
            
            tech_stack = st.text_input(
                "Stack Tecnológico",
                help="Tecnologías separadas por comas (ej: .NET Core 7, SQL Server, Redis)"
            )
            
            submitted = st.form_submit_button("🚀 Crear Aplicación", type="primary")
            
            if submitted:
                if app_id and app_name and app_type and owner_team:
                    # Procesar tech stack
                    tech_list = [tech.strip() for tech in tech_stack.split(',') if tech.strip()] if tech_stack else []
                    
                    # Crear aplicación
                    result = dashboard_tools.create_application(
                        app_id=app_id,
                        name=app_name,
                        app_type=app_type,
                        description=description,
                        repository_url=repository_url,
                        tech_stack=tech_list,
                        owner_team=owner_team,
                        health_check_url=health_check_url
                    )
                    
                    if result["success"]:
                        st.success(f"✅ {result['message']}")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")
                else:
                    st.error("❌ Por favor complete todos los campos marcados con *")
    
    with create_tab2:
        st.subheader("🏷️ Crear Nueva Versión")
        
        # Verificar que hay aplicaciones
        app_choices = dashboard_tools.get_application_choices()
        if not app_choices:
            st.warning("⚠️ Primero debe crear al menos una aplicación")
        else:
            with st.form("create_version_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    selected_app = st.selectbox(
                        "Aplicación*",
                        options=[choice[0] for choice in app_choices],
                        format_func=lambda x: next(choice[1] for choice in app_choices if choice[0] == x)
                    )
                    
                    version = st.text_input(
                        "Número de Versión*",
                        help="Formato semántico recomendado (ej: 2.1.0)"
                    )
                    
                    branch = st.text_input(
                        "Rama de Git*",
                        value="main",
                        help="Rama desde la cual se creó la versión"
                    )
                
                with col2:
                    commit_hash = st.text_input(
                        "Hash del Commit*",
                        help="Hash del commit de Git (8 caracteres)"
                    )
                    
                    build_number = st.text_input(
                        "Número de Build*",
                        help="Número de build del CI/CD (ej: build-1234)"
                    )
                
                features = st.text_area(
                    "Nuevas Funcionalidades",
                    help="Una funcionalidad por línea"
                )
                
                bug_fixes = st.text_area(
                    "Correcciones de Errores",
                    help="Una corrección por línea"
                )
                
                breaking_changes = st.text_area(
                    "Cambios Incompatibles",
                    help="Cambios que rompen compatibilidad (una por línea)"
                )
                
                submitted = st.form_submit_button("🏷️ Crear Versión", type="primary")
                
                if submitted:
                    if selected_app and version and branch and commit_hash and build_number:
                        # Procesar listas
                        features_list = [f.strip() for f in features.split('\n') if f.strip()] if features else []
                        bug_fixes_list = [f.strip() for f in bug_fixes.split('\n') if f.strip()] if bug_fixes else []
                        breaking_list = [f.strip() for f in breaking_changes.split('\n') if f.strip()] if breaking_changes else []
                        
                        # Crear versión
                        result = dashboard_tools.create_version(
                            application_id=selected_app,
                            version=version,
                            branch=branch,
                            commit_hash=commit_hash,
                            build_number=build_number,
                            features=features_list,
                            bug_fixes=bug_fixes_list,
                            breaking_changes=breaking_list
                        )
                        
                        if result["success"]:
                            st.success(f"✅ {result['message']}")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ {result['message']}")
                    else:
                        st.error("❌ Por favor complete todos los campos marcados con *")
    
    with create_tab3:
        st.subheader("🚀 Crear Nuevo Despliegue")
        
        # Verificar que hay aplicaciones
        app_choices = dashboard_tools.get_application_choices()
        if not app_choices:
            st.warning("⚠️ Primero debe crear al menos una aplicación")
        else:
            with st.form("create_deployment_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    selected_app = st.selectbox(
                        "Aplicación*",
                        options=[choice[0] for choice in app_choices],
                        format_func=lambda x: next(choice[1] for choice in app_choices if choice[0] == x),
                        key="deploy_app_select"
                    )
                    
                    # Obtener versiones de la aplicación seleccionada
                    if selected_app:
                        version_choices = dashboard_tools.get_version_choices(selected_app)
                        if version_choices:
                            selected_version = st.selectbox(
                                "Versión*",
                                options=version_choices,
                                index=0  # Seleccionar la primera (más reciente)
                            )
                        else:
                            st.warning("⚠️ Esta aplicación no tiene versiones. Cree una versión primero.")
                            selected_version = None
                    else:
                        selected_version = None
                
                with col2:
                    environment = st.selectbox(
                        "Entorno de Destino*",
                        options=dashboard_tools.get_environment_choices(),
                        format_func=lambda x: {
                            'dev': '🔧 Desarrollo',
                            'pre': '🧪 Pre-producción',
                            'prod': '🌟 Producción'
                        }.get(x, x)
                    )
                    
                    deployed_by = st.text_input(
                        "Desplegado por*",
                        help="Usuario que realiza el despliegue"
                    )
                
                notes = st.text_area(
                    "Notas del Despliegue",
                    help="Información adicional sobre este despliegue"
                )
                
                submitted = st.form_submit_button("🚀 Iniciar Despliegue", type="primary")
                
                if submitted:
                    if selected_app and selected_version and environment and deployed_by:
                        # Crear despliegue
                        result = dashboard_tools.create_deployment(
                            application_id=selected_app,
                            environment=environment,
                            version=selected_version,
                            deployed_by=deployed_by,
                            notes=notes
                        )
                        
                        if result["success"]:
                            st.success(f"✅ {result['message']}")
                            st.info(f"🆔 ID del despliegue: `{result['data']['deployment_id']}`")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ {result['message']}")
                    else:
                        st.error("❌ Por favor complete todos los campos marcados con *")
                        if not selected_version:
                            st.error("❌ La aplicación seleccionada no tiene versiones disponibles")
    
    # Información adicional
    st.markdown("---")
    st.markdown("### 💡 Consejos")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📱 Aplicaciones:**
        - Use IDs descriptivos y únicos
        - Seleccione el tipo correcto
        - Incluya URL de repositorio para rastreo
        """)
    
    with col2:
        st.markdown("""
        **🏷️ Versiones:**
        - Use versionado semántico (X.Y.Z)
        - Incluya hash de commit completo
        - Documente cambios importantes
        """)
    
    with col3:
        st.markdown("""
        **🚀 Despliegues:**
        - Verifique la versión correcta
        - Use entorno apropiado
        - Agregue notas descriptivas
        """)

# Footer
st.markdown("---")
st.markdown(
    "🚀 **MCP Deployment Manager** - Sistema de gestión de despliegues multi-aplicación | "
    "🏗️ Arquitectura: Entorno → Aplicación → Versión → Despliegue"
)