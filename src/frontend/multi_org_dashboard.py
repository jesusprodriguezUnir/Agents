"""
Dashboard Multi-Organización para MCP Deployment Manager.

Nueva interfaz que soporta múltiples organizaciones y entornos flexibles.
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime
from typing import Dict, List, Any


# Configuración de página
st.set_page_config(
    page_title="🚀 MCP Multi-Organization Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATABASE_PATH = "data/deployments.db"


def get_db_connection():
    """Obtiene una conexión a la base de datos."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_organizations():
    """Obtiene todas las organizaciones, incluyendo display_name si existe."""
    with get_db_connection() as conn:
        # Verificar si la columna display_name existe en la tabla organizations
        columns = [row[1] for row in conn.execute("PRAGMA table_info(organizations)").fetchall()]
        has_display_name = "display_name" in columns
        select_display = ", o.display_name" if has_display_name else ""
        group_display = ", o.display_name" if has_display_name else ""
        sql = f"""
            SELECT
                o.id,
                o.name{select_display},
                o.description,
                COUNT(DISTINCT e.id) as environment_count,
                COUNT(DISTINCT d.id) as deployment_count
            FROM organizations o
            LEFT JOIN environments e ON o.id = e.organization_id
            LEFT JOIN deployments d ON e.name = d.environment
            GROUP BY o.id, o.name{group_display}, o.description
            ORDER BY o.name
        """
        result = conn.execute(sql).fetchall()
        return [dict(row) for row in result]


def get_environments_by_org(org_id):
    """Obtiene entornos por organización."""
    with get_db_connection() as conn:
        result = conn.execute("""
            SELECT 
                e.id,
                e.name,
                e.description,
                COUNT(DISTINCT d.id) as deployment_count,
                MAX(d.deployed_at) as last_deployment
            FROM environments e
            LEFT JOIN deployments d ON e.id = d.environment_id
            WHERE e.organization_id = ?
            GROUP BY e.id, e.name, e.description
            ORDER BY e.name
        """, (org_id,)).fetchall()
        
        return [dict(row) for row in result]


def get_applications():
    """Obtiene todas las aplicaciones."""
    with get_db_connection() as conn:
        result = conn.execute("""
            SELECT 
                a.id,
                a.name,
                a.description,
                COUNT(DISTINCT ac.id) as component_count,
                COUNT(DISTINCT v.id) as version_count,
                COUNT(DISTINCT d.id) as deployment_count
            FROM applications a
            LEFT JOIN application_components ac ON a.id = ac.application_id
            LEFT JOIN versions v ON ac.id = v.component_id
            LEFT JOIN deployments d ON v.id = d.version_id
            GROUP BY a.id, a.name, a.description
            ORDER BY a.name
        """).fetchall()
        
        return [dict(row) for row in result]


def get_components_by_app(app_id):
    """Obtiene componentes por aplicación."""
    with get_db_connection() as conn:
        result = conn.execute("""
            SELECT 
                ac.id,
                ac.name,
                ac.type,
                ac.repository_url,
                COUNT(DISTINCT v.id) as version_count,
                COUNT(DISTINCT d.id) as deployment_count
            FROM application_components ac
            LEFT JOIN versions v ON ac.id = v.component_id
            LEFT JOIN deployments d ON v.id = d.version_id
            WHERE ac.application_id = ?
            GROUP BY ac.id, ac.name, ac.type, ac.repository_url
            ORDER BY ac.name
        """, (app_id,)).fetchall()
        
        return [dict(row) for row in result]


def create_application(name, description):
    """Crea una nueva aplicación."""
    with get_db_connection() as conn:
        try:
            conn.execute("""
                INSERT INTO applications (name, description)
                VALUES (?, ?)
            """, (name, description))
            conn.commit()
            return True, "Aplicación creada exitosamente"
        except sqlite3.IntegrityError:
            return False, "Ya existe una aplicación con ese nombre"
        except Exception as e:
            return False, f"Error al crear aplicación: {str(e)}"


def update_application(app_id, name, description):
    """Actualiza una aplicación existente."""
    with get_db_connection() as conn:
        try:
            cursor = conn.execute("""
                UPDATE applications 
                SET name = ?, description = ?
                WHERE id = ?
            """, (name, description, app_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                return True, "Aplicación actualizada exitosamente"
            else:
                return False, "Aplicación no encontrada"
        except sqlite3.IntegrityError:
            return False, "Ya existe una aplicación con ese nombre"
        except Exception as e:
            return False, f"Error al actualizar aplicación: {str(e)}"


def delete_application(app_id):
    """Elimina una aplicación (si no tiene componentes)."""
    with get_db_connection() as conn:
        try:
            # Verificar si tiene componentes
            components = conn.execute(
                "SELECT COUNT(*) as count FROM application_components WHERE application_id = ?", 
                (app_id,)
            ).fetchone()
            
            if components['count'] > 0:
                return False, f"No se puede eliminar. La aplicación tiene {components['count']} componentes asociados"
            
            cursor = conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                return True, "Aplicación eliminada exitosamente"
            else:
                return False, "Aplicación no encontrada"
        except Exception as e:
            return False, f"Error al eliminar aplicación: {str(e)}"


def create_component(app_id, name, component_type, repository_url=""):
    """Crea un nuevo componente."""
    with get_db_connection() as conn:
        try:
            conn.execute("""
                INSERT INTO application_components (application_id, name, type, repository_url)
                VALUES (?, ?, ?, ?)
            """, (app_id, name, component_type, repository_url))
            conn.commit()
            return True, "Componente creado exitosamente"
        except sqlite3.IntegrityError:
            return False, "Ya existe un componente con ese nombre en esta aplicación"
        except Exception as e:
            return False, f"Error al crear componente: {str(e)}"


def update_component(component_id, name, component_type, repository_url=""):
    """Actualiza un componente existente."""
    with get_db_connection() as conn:
        try:
            cursor = conn.execute("""
                UPDATE application_components 
                SET name = ?, type = ?, repository_url = ?
                WHERE id = ?
            """, (name, component_type, repository_url, component_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                return True, "Componente actualizado exitosamente"
            else:
                return False, "Componente no encontrado"
        except sqlite3.IntegrityError:
            return False, "Ya existe un componente con ese nombre en esta aplicación"
        except Exception as e:
            return False, f"Error al actualizar componente: {str(e)}"


def delete_component(component_id):
    """Elimina un componente (si no tiene versiones)."""
    with get_db_connection() as conn:
        try:
            # Verificar si tiene versiones
            versions = conn.execute(
                "SELECT COUNT(*) as count FROM versions WHERE component_id = ?", 
                (component_id,)
            ).fetchone()
            
            if versions['count'] > 0:
                return False, f"No se puede eliminar. El componente tiene {versions['count']} versiones asociadas"
            
            cursor = conn.execute("DELETE FROM application_components WHERE id = ?", (component_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                return True, "Componente eliminado exitosamente"
            else:
                return False, "Componente no encontrado"
        except Exception as e:
            return False, f"Error al eliminar componente: {str(e)}"


def get_deployments_data(org_id=None, env_id=None, days=30):
    """Obtiene datos de despliegues con filtros."""
    with get_db_connection() as conn:
        query = """
            SELECT 
                d.id,
                d.status,
                d.deployed_by,
                d.deployed_at,
                d.notes,
                o.name as organization,
                e.name as environment,
                a.name as application,
                ac.name as component,
                v.version
            FROM deployments d
            JOIN environments e ON d.environment_id = e.id
            JOIN organizations o ON e.organization_id = o.id
            JOIN versions v ON d.version_id = v.id
            JOIN application_components ac ON v.component_id = ac.id
            JOIN applications a ON ac.application_id = a.id
            WHERE d.deployed_at >= datetime('now', '-{} days')
        """.format(days)
        
        params = []
        if org_id:
            query += " AND o.id = ?"
            params.append(org_id)
        if env_id:
            query += " AND e.id = ?"
            params.append(env_id)
            
        query += " ORDER BY d.deployed_at DESC"
        
        result = conn.execute(query, params).fetchall()
        return [dict(row) for row in result]


def render_sidebar():
    """Renderiza la barra lateral con filtros."""
    st.sidebar.title("🏢 Filtros Multi-Org")
    
    # Obtener organizaciones
    organizations = get_organizations()
    org_options = {org['name']: org['id'] for org in organizations}
    org_options = {"Todas las organizaciones": None, **org_options}
    
    selected_org_name = st.sidebar.selectbox(
        "Organización",
        options=list(org_options.keys()),
        index=0
    )
    selected_org_id = org_options[selected_org_name]
    
    # Filtro de entornos (solo si hay organización seleccionada)
    selected_env_id = None
    if selected_org_id:
        environments = get_environments_by_org(selected_org_id)
        if environments:
            env_options = {env['name']: env['id'] for env in environments}
            env_options = {"Todos los entornos": None, **env_options}
            
            selected_env_name = st.sidebar.selectbox(
                "Entorno",
                options=list(env_options.keys()),
                index=0
            )
            selected_env_id = env_options[selected_env_name]
    
    # Filtro de días
    days = st.sidebar.slider(
        "Días de histórico",
        min_value=1,
        max_value=365,
        value=30,
        step=1
    )
    
    return selected_org_id, selected_env_id, days


def render_organization_overview():
    """Renderiza vista general de organizaciones."""
    st.header("🏢 Vista General de Organizaciones")
    
    organizations = get_organizations()
    
    if not organizations:
        st.warning("No hay organizaciones configuradas.")
        return
    
    # Crear métricas por organización
    cols = st.columns(len(organizations))
    
    for i, org in enumerate(organizations):
        with cols[i]:
            st.metric(
                label=f"📊 {org['name'].upper()}",
                value=f"{org['deployment_count']} despliegues",
                delta=f"{org['environment_count']} entornos"
            )
    
    # Gráfico de distribución de despliegues por organización
    org_data = pd.DataFrame(organizations)
    
    if not org_data.empty:
        fig = px.pie(
            org_data, 
            values='deployment_count', 
            names='name',
            title="📊 Distribución de Despliegues por Organización"
        )
        st.plotly_chart(fig, use_container_width=True)


def render_deployment_metrics(org_id, env_id, days):
    """Renderiza métricas de despliegues."""
    deployments = get_deployments_data(org_id, env_id, days)
    
    if not deployments:
        st.warning("No hay datos de despliegues para los filtros seleccionados.")
        return
    
    df = pd.DataFrame(deployments)
    
    # Métricas principales
    st.header("📊 Métricas de Despliegues")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_deployments = len(deployments)
        st.metric("Total Despliegues", total_deployments)
    
    with col2:
        success_rate = len(df[df['status'] == 'success']) / len(df) * 100 if len(df) > 0 else 0
        st.metric("Tasa de Éxito", f"{success_rate:.1f}%")
    
    with col3:
        unique_apps = df['application'].nunique()
        st.metric("Aplicaciones", unique_apps)
    
    with col4:
        unique_users = df['deployed_by'].nunique()
        st.metric("Usuarios Activos", unique_users)
    
    # Gráfico de despliegues por día
    df['date'] = pd.to_datetime(df['deployed_at']).dt.date
    daily_deployments = df.groupby(['date', 'status']).size().reset_index(name='count')
    
    fig = px.bar(
        daily_deployments,
        x='date',
        y='count',
        color='status',
        title="📈 Despliegues por Día",
        color_discrete_map={'success': 'green', 'failed': 'red'}
    )
    st.plotly_chart(fig, use_container_width=True)


def render_environment_status(org_id, env_id):
    """Renderiza estado de entornos."""
    st.header("🌍 Estado de Entornos")
    
    if org_id:
        environments = get_environments_by_org(org_id)
        
        if environments:
            env_df = pd.DataFrame(environments)
            
            # Convertir fecha de último despliegue
            env_df['last_deployment'] = pd.to_datetime(env_df['last_deployment'])
            env_df['days_since_last'] = (datetime.now() - env_df['last_deployment']).dt.days
            
            # Mostrar tabla de entornos
            st.dataframe(
                env_df[['name', 'description', 'deployment_count', 'last_deployment', 'days_since_last']],
                column_config={
                    'name': 'Entorno',
                    'description': 'Descripción',
                    'deployment_count': 'Despliegues',
                    'last_deployment': 'Último Despliegue',
                    'days_since_last': 'Días desde último'
                },
                use_container_width=True
            )
        else:
            st.info("No hay entornos configurados para esta organización.")
    else:
        st.info("Selecciona una organización para ver sus entornos.")


def render_recent_deployments(org_id, env_id, days):
    """Renderiza tabla de despliegues recientes."""
    st.header("🚀 Despliegues Recientes")
    
    deployments = get_deployments_data(org_id, env_id, days)
    
    if deployments:
        df = pd.DataFrame(deployments)
        
        # Formatear datos para la tabla
        df['deployed_at'] = pd.to_datetime(df['deployed_at'])
        df = df.sort_values('deployed_at', ascending=False)
        
        # Mostrar tabla
        st.dataframe(
            df[['deployed_at', 'organization', 'environment', 'application', 'component', 'version', 'status', 'deployed_by']].head(20),
            column_config={
                'deployed_at': 'Fecha',
                'organization': 'Organización',
                'environment': 'Entorno',
                'application': 'Aplicación',
                'component': 'Componente',
                'version': 'Versión',
                'status': 'Estado',
                'deployed_by': 'Desplegado por'
            },
            use_container_width=True
        )
    else:
        st.info("No hay despliegues recientes para mostrar.")


def render_applications_management():
    """Renderiza la gestión de aplicaciones y componentes."""
    st.header("📱 Gestión de Aplicaciones y Componentes")
    
    # Crear pestañas para aplicaciones y componentes
    app_tab, comp_tab = st.tabs(["🏗️ Aplicaciones", "🧩 Componentes"])
    
    with app_tab:
        render_applications_tab()
    
    with comp_tab:
        render_components_tab()


def render_applications_tab():
    """Renderiza la pestaña de gestión de aplicaciones."""
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.subheader("➕ Nueva Aplicación")
        
        with st.form("new_application_form"):
            new_app_name = st.text_input("Nombre de la aplicación")
            new_app_description = st.text_area("Descripción")
            
            submitted = st.form_submit_button("Crear Aplicación")
            
            if submitted:
                if new_app_name.strip():
                    success, message = create_application(
                        new_app_name.strip(), 
                        new_app_description.strip()
                    )
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("El nombre de la aplicación es obligatorio")
    
    with col1:
        st.subheader("📋 Aplicaciones Existentes")
        
        applications = get_applications()
        
        if applications:
            for app in applications:
                with st.expander(f"📱 {app['name']}", expanded=False):
                    
                    # Información de la aplicación
                    st.write(f"**Descripción:** {app['description'] or 'Sin descripción'}")
                    
                    # Métricas
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Componentes", app['component_count'])
                    with col_b:
                        st.metric("Versiones", app['version_count'])
                    with col_c:
                        st.metric("Despliegues", app['deployment_count'])
                    
                    # Botones de acción
                    col_edit, col_delete = st.columns(2)
                    
                    with col_edit:
                        if st.button(f"✏️ Editar", key=f"edit_app_{app['id']}"):
                            st.session_state[f"editing_app_{app['id']}"] = True
                    
                    with col_delete:
                        if st.button(f"🗑️ Eliminar", key=f"delete_app_{app['id']}"):
                            success, message = delete_application(app['id'])
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                    
                    # Formulario de edición
                    if st.session_state.get(f"editing_app_{app['id']}", False):
                        with st.form(f"edit_app_form_{app['id']}"):
                            edit_name = st.text_input("Nombre", value=app['name'])
                            edit_description = st.text_area("Descripción", value=app['description'] or "")
                            
                            col_save, col_cancel = st.columns(2)
                            
                            with col_save:
                                save_clicked = st.form_submit_button("💾 Guardar")
                            
                            with col_cancel:
                                cancel_clicked = st.form_submit_button("❌ Cancelar")
                            
                            if save_clicked:
                                success, message = update_application(
                                    app['id'], 
                                    edit_name.strip(), 
                                    edit_description.strip()
                                )
                                if success:
                                    st.success(message)
                                    st.session_state[f"editing_app_{app['id']}"] = False
                                    st.rerun()
                                else:
                                    st.error(message)
                            
                            if cancel_clicked:
                                st.session_state[f"editing_app_{app['id']}"] = False
                                st.rerun()
        else:
            st.info("No hay aplicaciones registradas.")


def render_components_tab():
    """Renderiza la pestaña de gestión de componentes."""
    
    # Selector de aplicación
    applications = get_applications()
    
    if not applications:
        st.warning("Primero debes crear al menos una aplicación.")
        return
    
    app_options = {app['name']: app['id'] for app in applications}
    selected_app_name = st.selectbox(
        "Selecciona una aplicación para gestionar sus componentes:",
        options=list(app_options.keys())
    )
    selected_app_id = app_options[selected_app_name]
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.subheader("➕ Nuevo Componente")
        
        with st.form("new_component_form"):
            new_comp_name = st.text_input("Nombre del componente")
            new_comp_type = st.selectbox(
                "Tipo de componente",
                ["frontend", "backend", "api", "database", "service", "other"]
            )
            new_comp_repo = st.text_input("URL del repositorio (opcional)")
            
            submitted = st.form_submit_button("Crear Componente")
            
            if submitted:
                if new_comp_name.strip():
                    success, message = create_component(
                        selected_app_id,
                        new_comp_name.strip(),
                        new_comp_type,
                        new_comp_repo.strip()
                    )
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("El nombre del componente es obligatorio")
    
    with col1:
        st.subheader(f"🧩 Componentes de {selected_app_name}")
        
        components = get_components_by_app(selected_app_id)
        
        if components:
            for comp in components:
                with st.expander(f"🧩 {comp['name']} ({comp['type']})", expanded=False):
                    
                    # Información del componente
                    if comp['repository_url']:
                        st.write(f"**Repositorio:** [{comp['repository_url']}]({comp['repository_url']})")
                    
                    # Métricas
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Versiones", comp['version_count'])
                    with col_b:
                        st.metric("Despliegues", comp['deployment_count'])
                    
                    # Botones de acción
                    col_edit, col_delete = st.columns(2)
                    
                    with col_edit:
                        if st.button(f"✏️ Editar", key=f"edit_comp_{comp['id']}"):
                            st.session_state[f"editing_comp_{comp['id']}"] = True
                    
                    with col_delete:
                        if st.button(f"🗑️ Eliminar", key=f"delete_comp_{comp['id']}"):
                            success, message = delete_component(comp['id'])
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                    
                    # Formulario de edición
                    if st.session_state.get(f"editing_comp_{comp['id']}", False):
                        with st.form(f"edit_comp_form_{comp['id']}"):
                            edit_name = st.text_input("Nombre", value=comp['name'])
                            edit_type = st.selectbox(
                                "Tipo",
                                ["frontend", "backend", "api", "database", "service", "other"],
                                index=["frontend", "backend", "api", "database", "service", "other"].index(comp['type'])
                            )
                            edit_repo = st.text_input("URL del repositorio", value=comp['repository_url'] or "")
                            
                            col_save, col_cancel = st.columns(2)
                            
                            with col_save:
                                save_clicked = st.form_submit_button("💾 Guardar")
                            
                            with col_cancel:
                                cancel_clicked = st.form_submit_button("❌ Cancelar")
                            
                            if save_clicked:
                                success, message = update_component(
                                    comp['id'],
                                    edit_name.strip(),
                                    edit_type,
                                    edit_repo.strip()
                                )
                                if success:
                                    st.success(message)
                                    st.session_state[f"editing_comp_{comp['id']}"] = False
                                    st.rerun()
                                else:
                                    st.error(message)
                            
                            if cancel_clicked:
                                st.session_state[f"editing_comp_{comp['id']}"] = False
                                st.rerun()
        else:
            st.info(f"No hay componentes registrados para {selected_app_name}.")


def main():
    """Función principal del dashboard."""
    st.title("🚀 MCP Multi-Organization Deployment Dashboard")
    st.markdown("---")
    
    # Renderizar barra lateral
    org_id, env_id, days = render_sidebar()
    
    # Crear pestañas
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏢 Organizaciones", 
        "📊 Métricas", 
        "🌍 Entornos", 
        "🚀 Despliegues",
        "📱 Aplicaciones"
    ])
    
    with tab1:
        render_organization_overview()
    
    with tab2:
        render_deployment_metrics(org_id, env_id, days)
    
    with tab3:
        render_environment_status(org_id, env_id)
    
    with tab4:
        render_recent_deployments(org_id, env_id, days)
    
    with tab5:
        render_applications_management()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "🚀 MCP Multi-Organization Dashboard | "
        f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()