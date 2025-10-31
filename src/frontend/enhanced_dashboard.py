"""
Dashboard mejorado con funcionalidades de edición y resumen de entornos.
Incluye exportación a PDF y gestión completa de aplicaciones, componentes y versiones.
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any
import base64
from io import BytesIO

# Importar herramientas del dashboard
from dashboard_tools import dashboard_tools

# Configuración de página
st.set_page_config(
    page_title="🚀 MCP Deployment Manager - Enhanced",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS mejorados
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
    .environment-card {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    }
    .environment-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .dev-env {
        border-left: 4px solid #17a2b8;
        background: linear-gradient(135deg, #f8f9fa 0%, #e3f2fd 100%);
    }
    .pre-env {
        border-left: 4px solid #ffc107;
        background: linear-gradient(135deg, #f8f9fa 0%, #fff3cd 100%);
    }
    .prod-env {
        border-left: 4px solid #28a745;
        background: linear-gradient(135deg, #f8f9fa 0%, #d4edda 100%);
    }
    }
    .dev-env { border-left: 4px solid #17a2b8; }
    .pre-env { border-left: 4px solid #ffc107; }
    .prod-env { border-left: 4px solid #28a745; }
    .edit-button {
        background: #6c757d;
        color: white;
        border: none;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        cursor: pointer;
    }
    @media print {
        .no-print { display: none !important; }
        .print-only { display: block !important; }
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

def get_environment_summary():
    """Obtiene resumen de todos los entornos."""
    conn = get_database_connection()
    
    # Obtener último despliegue exitoso por componente y entorno
    df = pd.read_sql_query("""
        WITH latest_deployments AS (
            SELECT 
                d.component_id,
                d.environment,
                MAX(d.deployed_at) as last_deployed
            FROM deployments d
            WHERE d.status = 'success'
            GROUP BY d.component_id, d.environment
        )
        SELECT 
            d.environment,
            a.name as application_name,
            ac.type as component_type,
            ac.name as component_name,
            v.version,
            d.deployed_at,
            d.deployed_by,
            ac.repository_url
        FROM deployments d
        JOIN latest_deployments ld ON d.component_id = ld.component_id 
            AND d.environment = ld.environment 
            AND d.deployed_at = ld.last_deployed
        JOIN versions v ON d.version_id = v.id
        JOIN application_components ac ON d.component_id = ac.id
        JOIN applications a ON ac.application_id = a.id
        WHERE d.status = 'success'
        ORDER BY d.environment, a.name, ac.type
    """, conn)
    
    conn.close()
    return df

def get_compact_environment_summary():
    """Obtiene resumen compacto agrupado por aplicación y entorno."""
    env_summary = get_environment_summary()
    
    if env_summary.empty:
        return {}
    
    # Filtrar aplicaciones específicas (excluir Cargos Funcionales)
    excluded_apps = ['Cargos Funcionales']
    env_summary = env_summary[~env_summary['application_name'].isin(excluded_apps)]
    
    # Agrupar por entorno y aplicación
    compact_summary = {}
    
    for env in ['dev', 'pre', 'prod']:
        env_data = env_summary[env_summary['environment'] == env]
        compact_summary[env] = {}
        
        for app_name in env_data['application_name'].unique():
            app_data = env_data[env_data['application_name'] == app_name]
            
            compact_summary[env][app_name] = {
                'frontend': None,
                'backend': None,
                'last_deploy': None
            }
            
            for _, row in app_data.iterrows():
                component_type = row['component_type']
                compact_summary[env][app_name][component_type] = {
                    'version': row['version'],
                    'deployed_at': row['deployed_at']
                }
                
                # Mantener la fecha más reciente
                if compact_summary[env][app_name]['last_deploy'] is None or \
                   (row['deployed_at'] and row['deployed_at'] > compact_summary[env][app_name]['last_deploy']):
                    compact_summary[env][app_name]['last_deploy'] = row['deployed_at']
    
    return compact_summary

def create_executive_excel_report():
    """Genera un reporte Excel ejecutivo con múltiples hojas."""
    try:
        # Obtener datos
        compact_summary = get_compact_environment_summary()
        apps_df = load_applications()
        deployments_df = load_deployments()
        
        # Crear buffer de memoria para Excel
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            
            # HOJA 1: Resumen Ejecutivo
            executive_data = []
            
            for env in ['dev', 'pre', 'prod']:
                env_apps = compact_summary.get(env, {})
                
                for app_name, app_data in env_apps.items():
                    frontend_version = app_data['frontend']['version'] if app_data['frontend'] else 'N/A'
                    backend_version = app_data['backend']['version'] if app_data['backend'] else 'N/A'
                    last_deploy = app_data['last_deploy'][:10] if app_data['last_deploy'] else 'N/A'
                    
                    has_both = app_data['frontend'] and app_data['backend']
                    status = "Completo" if has_both else "Incompleto"
                    
                    executive_data.append({
                        'Entorno': env.upper(),
                        'Aplicación': app_name,
                        'Frontend': f"v{frontend_version}",
                        'Backend': f"v{backend_version}",
                        'Estado': status,
                        'Último Despliegue': last_deploy
                    })
            
            executive_df = pd.DataFrame(executive_data)
            executive_df.to_excel(writer, sheet_name='Resumen Ejecutivo', index=False)
            
            # HOJA 2: Aplicaciones
            apps_summary = apps_df[['name', 'description', 'owner_team']].copy()
            apps_summary.columns = ['Aplicación', 'Descripción', 'Equipo Propietario']
            apps_summary.to_excel(writer, sheet_name='Aplicaciones', index=False)
            
            # HOJA 3: Últimos Despliegues (top 50)
            recent_deployments = deployments_df.head(50)[
                ['application_name', 'component_name', 'component_type', 'version', 
                 'environment', 'status', 'deployed_by', 'deployed_at']
            ].copy()
            recent_deployments.columns = [
                'Aplicación', 'Componente', 'Tipo', 'Versión', 
                'Entorno', 'Estado', 'Desplegado Por', 'Fecha'
            ]
            recent_deployments.to_excel(writer, sheet_name='Últimos Despliegues', index=False)
            
            # HOJA 4: Estadísticas
            stats_data = []
            
            # Estadísticas generales
            total_apps = len(apps_df)
            total_deployments = len(deployments_df)
            success_rate = (deployments_df['status'] == 'success').mean() * 100
            
            # Por entorno
            for env in ['dev', 'pre', 'prod']:
                env_deployments = deployments_df[deployments_df['environment'] == env]
                env_success_rate = (env_deployments['status'] == 'success').mean() * 100 if len(env_deployments) > 0 else 0
                
                stats_data.append({
                    'Métrica': f'Despliegues en {env.upper()}',
                    'Valor': len(env_deployments),
                    'Porcentaje Éxito': f"{env_success_rate:.1f}%"
                })
            
            # Agregar estadísticas generales
            stats_data.insert(0, {
                'Métrica': 'Total Aplicaciones',
                'Valor': total_apps,
                'Porcentaje Éxito': 'N/A'
            })
            
            stats_data.insert(1, {
                'Métrica': 'Total Despliegues',
                'Valor': total_deployments,
                'Porcentaje Éxito': f"{success_rate:.1f}%"
            })
            
            stats_df = pd.DataFrame(stats_data)
            stats_df.to_excel(writer, sheet_name='Estadísticas', index=False)
        
        output.seek(0)
        return output.getvalue()
    
    except Exception as e:
        st.error(f"Error generando reporte Excel: {str(e)}")
        return None

def create_executive_pdf_report():
    """Genera un reporte PDF ejecutivo para dirección."""
    try:
        compact_summary = get_compact_environment_summary()
        apps_df = load_applications()
        deployments_df = load_deployments()
        
        # Estadísticas ejecutivas
        total_apps = len(apps_df)
        total_deployments = len(deployments_df)
        success_rate = (deployments_df['status'] == 'success').mean() * 100
        
        # Último mes de actividad
        recent_deployments = deployments_df[
            pd.to_datetime(deployments_df['deployed_at']) >= (datetime.now() - timedelta(days=30))
        ]
        
        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte Ejecutivo - Sistema de Despliegues</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            line-height: 1.6;
            color: #333;
        }}
        .header {{
            text-align: center;
            border-bottom: 4px solid #667eea;
            padding-bottom: 30px;
            margin-bottom: 40px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e3f2fd 100%);
            padding: 30px;
            border-radius: 10px;
        }}
        .header h1 {{
            color: #667eea;
            margin: 0;
            font-size: 2.8em;
            font-weight: bold;
        }}
        .header h2 {{
            color: #666;
            margin: 10px 0 0 0;
            font-size: 1.2em;
            font-weight: normal;
        }}
        .executive-summary {{
            background: #f8f9fa;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            border-left: 5px solid #28a745;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            border-top: 4px solid #667eea;
        }}
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin: 0;
        }}
        .stat-label {{
            color: #666;
            font-size: 1.1em;
            margin-top: 5px;
        }}
        .environment-section {{
            margin: 30px 0;
            page-break-inside: avoid;
        }}
        .env-header {{
            background: linear-gradient(90deg, #667eea, #764ba2);
            color: white;
            padding: 15px 20px;
            font-size: 1.5em;
            font-weight: bold;
            border-radius: 8px 8px 0 0;
        }}
        .env-content {{
            background: white;
            border: 1px solid #ddd;
            border-top: none;
            border-radius: 0 0 8px 8px;
        }}
        .app-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            padding: 20px;
        }}
        .app-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .app-name {{
            font-weight: bold;
            font-size: 1.1em;
            color: #333;
            margin-bottom: 8px;
        }}
        .version-info {{
            display: flex;
            justify-content: space-between;
            margin: 5px 0;
        }}
        .version-label {{
            color: #666;
        }}
        .version-value {{
            font-weight: bold;
        }}
        .status-complete {{
            color: #28a745;
            font-weight: bold;
        }}
        .status-incomplete {{
            color: #dc3545;
            font-weight: bold;
        }}
        .footer {{
            margin-top: 50px;
            text-align: center;
            font-size: 0.9em;
            color: #666;
            border-top: 1px solid #eee;
            padding-top: 20px;
        }}
        @media print {{
            body {{ margin: 0; font-size: 12px; }}
            .environment-section {{ page-break-inside: avoid; }}
            .stats-grid {{ page-break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Reporte Ejecutivo</h1>
        <h2>Sistema de Gestión de Despliegues UNIR</h2>
        <p>Generado el {datetime.now().strftime('%d de %B de %Y a las %H:%M')}</p>
    </div>
    
    <div class="executive-summary">
        <h2>🎯 Resumen Ejecutivo</h2>
        <p>Este reporte presenta el estado actual de los despliegues en el ecosistema de aplicaciones académicas de UNIR, 
        incluyendo métricas de rendimiento, estado por entornos y análisis de actividad reciente.</p>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{total_apps}</div>
                <div class="stat-label">Aplicaciones Activas</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_deployments}</div>
                <div class="stat-label">Despliegues Totales</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{success_rate:.1f}%</div>
                <div class="stat-label">Tasa de Éxito</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(recent_deployments)}</div>
                <div class="stat-label">Despliegues (30 días)</div>
            </div>
        </div>
    </div>
"""
        
        # Sección por entornos
        env_names = {
            'dev': '🔧 Entorno de Desarrollo',
            'pre': '🧪 Entorno de Preproducción', 
            'prod': '🌟 Entorno de Producción'
        }
        
        for env, env_title in env_names.items():
            env_apps = compact_summary.get(env, {})
            
            html_content += f"""
    <div class="environment-section">
        <div class="env-header">{env_title}</div>
        <div class="env-content">"""
            
            if env_apps:
                html_content += '<div class="app-grid">'
                
                for app_name, app_data in env_apps.items():
                    frontend_version = app_data['frontend']['version'] if app_data['frontend'] else 'N/A'
                    backend_version = app_data['backend']['version'] if app_data['backend'] else 'N/A'
                    last_deploy = app_data['last_deploy'][:10] if app_data['last_deploy'] else 'N/A'
                    
                    has_both = app_data['frontend'] and app_data['backend']
                    status_class = "status-complete" if has_both else "status-incomplete"
                    status_text = "✅ Completo" if has_both else "⚠️ Incompleto"
                    
                    html_content += f"""
                    <div class="app-card">
                        <div class="app-name">{app_name}</div>
                        <div class="version-info">
                            <span class="version-label">🌐 Frontend:</span>
                            <span class="version-value">v{frontend_version}</span>
                        </div>
                        <div class="version-info">
                            <span class="version-label">⚙️ Backend:</span>
                            <span class="version-value">v{backend_version}</span>
                        </div>
                        <div class="version-info">
                            <span class="version-label">📅 Último:</span>
                            <span class="version-value">{last_deploy}</span>
                        </div>
                        <div class="version-info">
                            <span class="version-label">Estado:</span>
                            <span class="{status_class}">{status_text}</span>
                        </div>
                    </div>"""
                
                html_content += '</div>'
            else:
                html_content += '<p style="padding: 20px; text-align: center; color: #666;">Sin despliegues registrados</p>'
            
            html_content += '</div></div>'
        
        # Footer
        html_content += f"""
    <div class="footer">
        <p><strong>MCP Deployment Manager v2.0</strong> | UNIR - Universidad Internacional de La Rioja</p>
        <p>Arquitectura: Aplicaciones → Componentes → Versiones → Despliegues</p>
        <p>Reporte generado automáticamente el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
    </div>
</body>
</html>"""
        
        return html_content
    
    except Exception as e:
        st.error(f"Error generando reporte PDF: {str(e)}")
        return None

def create_pdf_report():
    """Genera un reporte HTML limpio del estado de los entornos."""
    try:
        env_summary = get_environment_summary()
        
        # Obtener estadísticas generales
        total_apps = env_summary['application_name'].nunique() if not env_summary.empty else 0
        total_components = env_summary['component_name'].nunique() if not env_summary.empty else 0
        
        # Crear HTML con formato limpio (sin etiquetas HTML en el contenido)
        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Entornos - {datetime.now().strftime('%Y-%m-%d %H:%M')}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            line-height: 1.6;
            color: #333;
            background-color: #fff;
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #667eea;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #667eea;
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            color: #666;
            margin: 10px 0 0 0;
            font-size: 1.1em;
        }}
        .summary {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            border-left: 5px solid #667eea;
        }}
        .summary h2 {{
            margin-top: 0;
            color: #333;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
        }}
        .stat-item {{
            text-align: center;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .environment {{
            margin: 30px 0;
            page-break-inside: avoid;
        }}
        .env-title {{
            background: linear-gradient(90deg, #667eea, #764ba2);
            color: white;
            padding: 15px;
            font-weight: bold;
            font-size: 1.3em;
            border-radius: 5px 5px 0 0;
        }}
        .app-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .app-table th, .app-table td {{
            border: 1px solid #ddd;
            padding: 12px 8px;
            text-align: left;
        }}
        .app-table th {{
            background-color: #f2f2f2;
            font-weight: bold;
            color: #333;
        }}
        .frontend {{
            background-color: #e3f2fd;
        }}
        .backend {{
            background-color: #f3e5f5;
        }}
        .footer {{
            margin-top: 40px;
            text-align: center;
            font-size: 0.9em;
            color: #666;
            border-top: 1px solid #eee;
            padding-top: 20px;
        }}
        @media print {{
            body {{ margin: 0; }}
            .environment {{ page-break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Reporte de Estado de Entornos</h1>
        <p>Sistema MCP Deployment Manager</p>
        <p>Generado el: {datetime.now().strftime('%d/%m/%Y a las %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <h2>Resumen Ejecutivo</h2>
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{total_apps}</div>
                <div>Aplicaciones</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{total_components}</div>
                <div>Componentes</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">3</div>
                <div>Entornos</div>
            </div>
        </div>
        <p><strong>Funcionalidades del sistema:</strong></p>
        <ul>
            <li>Edición en línea de aplicaciones y componentes</li>
            <li>Resumen completo de entornos</li>
            <li>Exportación de reportes PDF</li>
            <li>Gestión completa CRUD</li>
        </ul>
    </div>
"""
        
        # Generar contenido por entorno
        for env in ['dev', 'pre', 'prod']:
            env_data = env_summary[env_summary['environment'] == env]
            env_icon = {"dev": "🔧 DESARROLLO", "pre": "🧪 PREPRODUCCION", "prod": "🌟 PRODUCCION"}.get(env, f"📦 {env.upper()}")
            
            html_content += f"""
    <div class="environment">
        <div class="env-title">{env_icon}</div>"""
            
            if not env_data.empty:
                html_content += """
        <table class="app-table">
            <tr>
                <th>Aplicación</th>
                <th>Componente</th>
                <th>Tipo</th>
                <th>Versión</th>
                <th>Fecha Despliegue</th>
                <th>Desplegado Por</th>
            </tr>"""
                
                for _, row in env_data.iterrows():
                    css_class = row['component_type']
                    component_type_display = "Frontend" if row['component_type'] == 'frontend' else "Backend"
                    deployed_date = row['deployed_at'][:16] if row['deployed_at'] else 'N/A'
                    
                    html_content += f"""
            <tr class="{css_class}">
                <td>{row['application_name']}</td>
                <td>{row['component_name']}</td>
                <td>{component_type_display}</td>
                <td>v{row['version']}</td>
                <td>{deployed_date}</td>
                <td>{row['deployed_by'] or 'N/A'}</td>
            </tr>"""
                
                html_content += """
        </table>"""
            else:
                html_content += """
        <p style="padding: 20px; text-align: center; color: #666; font-style: italic;">
            No hay despliegues registrados en este entorno
        </p>"""
            
            html_content += """
    </div>"""
        
        # Footer
        html_content += f"""
    <div class="footer">
        <p>MCP Deployment Manager v2.0 | Arquitectura Jerárquica: Aplicaciones → Componentes → Versiones</p>
        <p>UNIR - Sistema de Gestión de Despliegues</p>
    </div>
</body>
</html>"""
        
        return html_content
    
    except Exception as e:
        st.error(f"Error generando reporte: {str(e)}")
        return None

def show_enhanced_overview():
    """Muestra el resumen mejorado con estado de entornos."""
    st.markdown('<div class="main-header"><h1>🎯 Resumen Ejecutivo</h1></div>', unsafe_allow_html=True)
    
    # Botones para generar reportes
    st.markdown("### 📊 Reportes Ejecutivos")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Reporte PDF Ejecutivo", key="executive_pdf_button"):
            html_report = create_executive_pdf_report()
            if html_report:
                st.success("✅ Reporte ejecutivo generado")
                st.download_button(
                    label="⬇️ Descargar PDF Ejecutivo",
                    data=html_report,
                    file_name=f"reporte_ejecutivo_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                    mime="text/html",
                    help="Reporte ejecutivo para dirección. Ábrelo en navegador e imprime como PDF."
                )
    
    with col2:
        if st.button("📊 Reporte Excel", key="excel_button"):
            excel_report = create_executive_excel_report()
            if excel_report:
                st.success("✅ Reporte Excel generado")
                st.download_button(
                    label="⬇️ Descargar Excel",
                    data=excel_report,
                    file_name=f"reporte_despliegues_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    help="Reporte completo con múltiples hojas: Resumen, Aplicaciones, Despliegues y Estadísticas."
                )
    
    with col3:
        if st.button("📋 Reporte HTML Técnico", key="technical_pdf_button"):
            html_report = create_pdf_report()
            if html_report:
                st.success("✅ Reporte técnico generado")
                st.download_button(
                    label="⬇️ Descargar Técnico",
                    data=html_report,
                    file_name=f"reporte_tecnico_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                    mime="text/html",
                    help="Reporte técnico detallado con información completa de entornos."
                )
    
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
    
    # Resumen por entornos
    st.markdown("## 🌍 Estado Actual de Entornos")
    
    compact_summary = get_compact_environment_summary()
    
    if compact_summary:
        col1, col2, col3 = st.columns(3)
        
        environments = [
            ("dev", "🔧 Desarrollo", "dev-env", col1),
            ("pre", "🧪 Preproducción", "pre-env", col2), 
            ("prod", "🌟 Producción", "prod-env", col3)
        ]
        
        for env_name, env_title, env_class, col in environments:
            with col:
                st.markdown(f"### {env_title}")
                env_apps = compact_summary.get(env_name, {})
                
                if env_apps:
                    for app_name, app_data in env_apps.items():
                        frontend_version = app_data['frontend']['version'] if app_data['frontend'] else 'N/A'
                        backend_version = app_data['backend']['version'] if app_data['backend'] else 'N/A'
                        last_deploy = app_data['last_deploy'][:10] if app_data['last_deploy'] else 'N/A'
                        
                        # Determinar estado visual
                        has_both = app_data['frontend'] and app_data['backend']
                        status_icon = "✅" if has_both else "⚠️"
                        
                        st.markdown(f"""
                        <div class="environment-card {env_class}" style="margin-bottom: 10px; padding: 12px; border-radius: 8px; border-left: 4px solid #667eea;">
                            <div style="font-weight: bold; font-size: 1.1em; margin-bottom: 5px;">
                                {status_icon} {app_name}
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                                <span style="color: #2196F3;">🌐 Frontend:</span>
                                <span style="font-weight: bold;">v{frontend_version}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span style="color: #9C27B0;">⚙️ Backend:</span>
                                <span style="font-weight: bold;">v{backend_version}</span>
                            </div>
                            <div style="font-size: 0.8em; color: #666; text-align: center;">
                                📅 {last_deploy}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Sin despliegues")

def show_applications_with_edit():
    """Muestra aplicaciones con opciones de edición."""
    st.markdown('<div class="main-header"><h1>🏢 Gestión de Aplicaciones</h1></div>', unsafe_allow_html=True)
    
    apps_df = load_applications()
    components_df = load_components()
    
    if apps_df.empty:
        st.warning("📝 No hay aplicaciones registradas")
        return
    
    # Lista de aplicaciones con edición
    st.subheader("📱 Lista de Aplicaciones")
    
    for _, app in apps_df.iterrows():
        col1, col2 = st.columns([5, 1])
        
        with col1:
            with st.expander(f"🏢 {app['name']}", expanded=False):
                # Información actual
                st.write(f"**ID:** {app['id']}")
                st.write(f"**Descripción:** {app['description']}")
                st.write(f"**Equipo:** {app['owner_team']}")
                st.write(f"**Creado:** {app['created_at'][:10] if app['created_at'] else 'N/A'}")
                
                # Componentes de esta aplicación
                app_components = components_df[components_df['application_id'] == app['id']]
                
                st.write("**Componentes:**")
                for _, comp in app_components.iterrows():
                    icon = "🌐" if comp['type'] == 'frontend' else "⚙️"
                    st.write(f"{icon} {comp['type'].capitalize()}")
                    if comp['repository_url']:
                        st.write(f"   📂 [{comp['repository_url'][:50]}...]({comp['repository_url']})")
        
        with col2:
            if st.button("✏️ Editar", key=f"edit_app_{app['id']}"):
                st.session_state[f"editing_app_{app['id']}"] = True
        
        # Formulario de edición
        if st.session_state.get(f"editing_app_{app['id']}", False):
            with st.form(f"edit_form_{app['id']}"):
                st.markdown(f"### ✏️ Editando: {app['name']}")
                
                new_name = st.text_input("Nombre", value=app['name'])
                new_description = st.text_area("Descripción", value=app['description'] or "")
                new_owner_team = st.text_input("Equipo Propietario", value=app['owner_team'] or "")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Guardar"):
                        result = dashboard_tools.update_application(
                            app['id'], new_name, new_description, new_owner_team
                        )
                        
                        if result["success"]:
                            st.success(f"✅ {result['message']}")
                            st.session_state[f"editing_app_{app['id']}"] = False
                            st.rerun()
                        else:
                            st.error(f"❌ {result['message']}")
                
                with col2:
                    if st.form_submit_button("❌ Cancelar"):
                        st.session_state[f"editing_app_{app['id']}"] = False
                        st.rerun()

def show_components_with_edit():
    """Muestra componentes con funcionalidad de edición."""
    st.markdown('<div class="main-header"><h1>📦 Gestión de Componentes</h1></div>', unsafe_allow_html=True)
    
    # Cargar componentes
    components = dashboard_tools.list_components()
    
    if not components:
        st.info("📦 No hay componentes registrados. Ve a 'Crear Nuevo' para agregar componentes.")
        return
    
    # Estadísticas rápidas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📦 Total Componentes", len(components))
    with col2:
        frontend_count = sum(1 for c in components if c['type'] == 'frontend')
        st.metric("🌐 Frontend", frontend_count)
    with col3:
        backend_count = sum(1 for c in components if c['type'] == 'backend')
        st.metric("⚙️ Backend", backend_count)
    with col4:
        other_count = len(components) - frontend_count - backend_count
        st.metric("🔧 Otros", other_count)
    
    st.markdown("---")
    
    # Agrupar componentes por aplicación
    apps_dict = {}
    for comp in components:
        app_name = comp['application_name']
        if app_name not in apps_dict:
            apps_dict[app_name] = []
        apps_dict[app_name].append(comp)
    
    # Mostrar componentes agrupados por aplicación
    for app_name, app_components in apps_dict.items():
        st.subheader(f"🏢 {app_name}")
        
        for comp in app_components:
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Información del componente
                    type_icon = {
                        'frontend': '🌐',
                        'backend': '⚙️',
                        'api': '🔌',
                        'database': '🗄️',
                        'microservice': '📡'
                    }.get(comp['type'], '📦')
                    
                    st.markdown(f"### {type_icon} {comp['name']}")
                    
                    # Información básica
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.markdown(f"**🏷️ ID:** `{comp['id']}`")
                        st.markdown(f"**📋 Tipo:** {comp['type'].capitalize()}")
                    with col_info2:
                        if comp['tech_stack']:
                            tech_list = comp['tech_stack'].split(',') if isinstance(comp['tech_stack'], str) else comp['tech_stack']
                            tech_badges = " ".join([f"`{tech.strip()}`" for tech in tech_list[:3]])
                            st.markdown(f"**💻 Stack:** {tech_badges}")
                        
                    # URLs si existen
                    if comp['repository_url']:
                        st.markdown(f"**📂 Repositorio:** [{comp['repository_url'][:50]}...]({comp['repository_url']})")
                    if comp['health_check_url']:
                        st.markdown(f"**🔍 Health Check:** [{comp['health_check_url'][:50]}...]({comp['health_check_url']})")
                
                with col2:
                    if st.button("✏️ Editar", key=f"edit_comp_{comp['id']}"):
                        st.session_state[f"editing_comp_{comp['id']}"] = True
                
                # Formulario de edición
                if st.session_state.get(f"editing_comp_{comp['id']}", False):
                    with st.form(f"edit_comp_form_{comp['id']}"):
                        st.markdown(f"### ✏️ Editando: {comp['name']}")
                        
                        new_name = st.text_input("Nombre", value=comp['name'])
                        new_repository_url = st.text_input("URL del Repositorio", value=comp['repository_url'] or "")
                        new_health_check_url = st.text_input("URL Health Check", value=comp['health_check_url'] or "")
                        
                        # Tech stack
                        current_tech = comp['tech_stack'] or ""
                        if isinstance(current_tech, str) and current_tech:
                            current_tech = current_tech.replace(',', ', ')
                        new_tech_stack = st.text_input("Stack Tecnológico (separado por comas)", value=current_tech)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Guardar"):
                                tech_list = [tech.strip() for tech in new_tech_stack.split(',')] if new_tech_stack else []
                                
                                result = dashboard_tools.update_component(
                                    comp['id'], 
                                    new_name, 
                                    new_repository_url,
                                    tech_list,
                                    new_health_check_url
                                )
                                
                                if result["success"]:
                                    st.success(f"✅ {result['message']}")
                                    st.session_state[f"editing_comp_{comp['id']}"] = False
                                    st.rerun()
                                else:
                                    st.error(f"❌ {result['message']}")
                        
                        with col2:
                            if st.form_submit_button("❌ Cancelar"):
                                st.session_state[f"editing_comp_{comp['id']}"] = False
                                st.rerun()
                
                st.markdown("---")

def show_create_forms():
    """Muestra formularios de creación mejorados."""
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
    
    with tab2:
        st.subheader("📦 Crear Nuevo Componente")
        st.markdown('<div class="info-box">💡 Un componente es una parte específica de una aplicación (frontend, backend, API, etc.).</div>', unsafe_allow_html=True)
        
        # Cargar aplicaciones disponibles
        applications = dashboard_tools.list_applications()
        app_options = [(app['id'], f"{app['name']} ({app['id']})") for app in applications]
        
        if not app_options:
            st.warning("⚠️ No hay aplicaciones disponibles. Crea una aplicación primero.")
        else:
            with st.form("create_component"):
                col1, col2 = st.columns(2)
                
                with col1:
                    selected_app = st.selectbox(
                        "Aplicación Padre*", 
                        options=[opt[0] for opt in app_options],
                        format_func=lambda x: next(opt[1] for opt in app_options if opt[0] == x)
                    )
                    component_id = st.text_input("ID del Componente*", placeholder="ej: frontend-web")
                    component_name = st.text_input("Nombre*", placeholder="ej: Frontend Web")
                    component_type = st.selectbox("Tipo*", ["frontend", "backend", "api", "database", "microservice"])
                
                with col2:
                    repository_url = st.text_input("URL del Repositorio", placeholder="https://github.com/user/repo")
                    health_check_url = st.text_input("URL Health Check", placeholder="https://api.domain.com/health")
                    tech_stack = st.text_input("Stack Tecnológico", placeholder="Angular 18, TypeScript (separado por comas)")
                
                submitted = st.form_submit_button("📦 Crear Componente")
                
                if submitted:
                    if component_id and component_name and selected_app:
                        try:
                            tech_list = [tech.strip() for tech in tech_stack.split(',')] if tech_stack else []
                            
                            result = dashboard_tools.create_component(
                                component_id=component_id,
                                application_id=selected_app,
                                name=component_name,
                                type=component_type,
                                repository_url=repository_url,
                                tech_stack=tech_list,
                                health_check_url=health_check_url
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
    
    with tab3:
        st.subheader("🔖 Crear Nueva Versión")
        st.markdown('<div class="info-box">💡 Una versión representa una release específica de un componente con información de despliegue.</div>', unsafe_allow_html=True)
        
        # Cargar componentes disponibles
        components = dashboard_tools.list_components()
        comp_options = [(comp['id'], f"{comp['application_name']} - {comp['name']} ({comp['type']})") for comp in components]
        
        if not comp_options:
            st.warning("⚠️ No hay componentes disponibles. Crea un componente primero.")
        else:
            with st.form("create_version"):
                col1, col2 = st.columns(2)
                
                with col1:
                    selected_component = st.selectbox(
                        "Componente*", 
                        options=[opt[0] for opt in comp_options],
                        format_func=lambda x: next(opt[1] for opt in comp_options if opt[0] == x)
                    )
                    version = st.text_input("Versión*", placeholder="ej: v1.2.3")
                    branch = st.text_input("Rama", placeholder="ej: main", value="main")
                    commit_hash = st.text_input("Commit Hash", placeholder="ej: abc123def456")
                
                with col2:
                    build_number = st.text_input("Build Number", placeholder="ej: 125")
                    features = st.text_area("Nuevas Funcionalidades", placeholder="Una funcionalidad por línea")
                    bug_fixes = st.text_area("Correcciones", placeholder="Una corrección por línea")
                
                submitted = st.form_submit_button("🔖 Crear Versión")
                
                if submitted:
                    if version and selected_component:
                        try:
                            features_list = [f.strip() for f in features.split('\n')] if features else []
                            bug_fixes_list = [f.strip() for f in bug_fixes.split('\n')] if bug_fixes else []
                            
                            result = dashboard_tools.create_version(
                                component_id=selected_component,
                                version=version,
                                branch=branch,
                                commit_hash=commit_hash,
                                build_number=build_number,
                                features=features_list,
                                bug_fixes=bug_fixes_list
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
    ["🎯 Resumen Ejecutivo", "🏢 Aplicaciones", "📦 Componentes", "🔖 Versiones", "🚀 Despliegues", "➕ Crear Nuevo"]
)

# Mostrar página seleccionada
if page == "🎯 Resumen Ejecutivo":
    show_enhanced_overview()
elif page == "🏢 Aplicaciones":
    show_applications_with_edit()
elif page == "📦 Componentes":
    show_components_with_edit()
elif page == "🔖 Versiones":
    # Reutilizar función anterior por ahora
    pass
elif page == "🚀 Despliegues":
    # Reutilizar función anterior por ahora
    pass
elif page == "➕ Crear Nuevo":
    show_create_forms()
    # Footer mejorado
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #f8f9fa 0%, #e3f2fd 100%); border-radius: 8px; margin: 1rem 0;'>
        <div style='color: #667eea; font-size: 1.1em; font-weight: bold; margin-bottom: 0.5rem;'>
            🚀 MCP Deployment Manager
        </div>
        <div style='color: #666; font-size: 0.9em; margin-bottom: 0.8rem;'>
            <strong>v2.0</strong>
        </div>
        
        <div style='background: white; padding: 0.8rem; border-radius: 6px; margin-bottom: 0.8rem; border-left: 3px solid #667eea;'>
            <div style='color: #333; font-weight: bold; margin-bottom: 0.3rem;'>
                📊 Estructura Jerárquica
            </div>
            <div style='color: #666; font-size: 0.85em; font-style: italic;'>
                Aplicaciones → Componentes → Versiones
            </div>
        </div>
        
        <div style='background: white; padding: 0.8rem; border-radius: 6px; border-left: 3px solid #28a745;'>
            <div style='color: #333; font-weight: bold; margin-bottom: 0.5rem;'>
                ✨ Funcionalidades
            </div>
            <div style='text-align: left; font-size: 0.8em; color: #666;'>
                <div style='margin-bottom: 0.2rem;'>• 📝 Edición en línea</div>
                <div style='margin-bottom: 0.2rem;'>• 🌍 Resumen de entornos</div>
                <div style='margin-bottom: 0.2rem;'>• 📄 Exportación PDF/Excel</div>
                <div style='margin-bottom: 0.2rem;'>• 🔧 Gestión completa CRUD</div>
                <div style='margin-bottom: 0.2rem;'>• 📊 Dashboard ejecutivo</div>
            </div>
        </div>
        
        <div style='margin-top: 0.8rem; font-size: 0.75em; color: #999;'>
            UNIR - Universidad Internacional de La Rioja
        </div>
    </div>
    """, unsafe_allow_html=True)