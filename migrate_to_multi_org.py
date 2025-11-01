#!/usr/bin/env python3
"""
Script de migración de base de datos para sistema multi-organización.

Este script migra la base de datos actual a la nueva estructura que soporta:
- Múltiples organizaciones (proeduca, villanueva)
- Entornos flexibles por organización
- URLs específicas por entorno/componente

IMPORTANTE: Ejecutar backup antes de usar este script.
"""

import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
import json

class DatabaseMigration:
    def __init__(self, db_path="data/deployments.db"):
        self.db_path = Path(db_path)
        self.backup_path = None
        self.conn = None
        
    def create_backup(self):
        """Crear backup de la base de datos antes de migración."""
        if not self.db_path.exists():
            raise FileNotFoundError(f"Base de datos no encontrada: {self.db_path}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.db_path.parent / "backup"
        backup_dir.mkdir(exist_ok=True)
        
        self.backup_path = backup_dir / f"deployments_pre_migration_{timestamp}.db"
        shutil.copy2(self.db_path, self.backup_path)
        
        print(f"✅ Backup creado: {self.backup_path}")
        return self.backup_path
    
    def connect(self):
        """Conectar a la base de datos."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        return self.conn
    
    def close(self):
        """Cerrar conexión."""
        if self.conn:
            self.conn.close()
    
    def verify_current_schema(self):
        """Verificar el esquema actual antes de migración."""
        cursor = self.conn.cursor()
        
        # Verificar tablas existentes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['applications', 'application_components', 'versions', 'deployments']
        missing_tables = [t for t in expected_tables if t not in tables]
        
        if missing_tables:
            raise Exception(f"Tablas faltantes en esquema actual: {missing_tables}")
        
        # Verificar estructura de deployments
        cursor.execute("PRAGMA table_info(deployments)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'environment' not in columns:
            raise Exception("Columna 'environment' no encontrada en tabla deployments")
        
        print("✅ Esquema actual verificado correctamente")
        return True
    
    def create_new_tables(self):
        """Crear las nuevas tablas del esquema multi-organización."""
        cursor = self.conn.cursor()
        
        print("📋 Creando nuevas tablas...")
        
        # 1. Tabla organizations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS organizations (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                display_name TEXT NOT NULL,
                description TEXT,
                active BOOLEAN NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
        """)
        
        # 2. Tabla environments
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS environments (
                id TEXT PRIMARY KEY,
                organization_id TEXT NOT NULL,
                name TEXT NOT NULL,
                display_name TEXT NOT NULL,
                description TEXT,
                order_priority INTEGER DEFAULT 1,
                active BOOLEAN NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                FOREIGN KEY (organization_id) REFERENCES organizations (id),
                UNIQUE(organization_id, name)
            )
        """)
        
        # 3. Tabla environment_urls
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS environment_urls (
                id TEXT PRIMARY KEY,
                environment_id TEXT NOT NULL,
                component_id TEXT NOT NULL,
                url_type TEXT NOT NULL,
                url TEXT NOT NULL,
                description TEXT,
                active BOOLEAN NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                FOREIGN KEY (environment_id) REFERENCES environments (id),
                FOREIGN KEY (component_id) REFERENCES application_components (id),
                UNIQUE(environment_id, component_id, url_type)
            )
        """)
        
        print("✅ Nuevas tablas creadas")
    
    def insert_initial_data(self):
        """Insertar datos iniciales de organizaciones y entornos."""
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        print("📊 Insertando datos iniciales...")
        
        # Organizaciones
        organizations = [
            ('proeduca', 'proeduca', 'PROEDUCA', 'Organización principal PROEDUCA', 1, now, None),
            ('villanueva', 'villanueva', 'VILLANUEVA', 'Organización VILLANUEVA', 1, now, None)
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO organizations 
            (id, name, display_name, description, active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, organizations)
        
        # Entornos PROEDUCA
        proeduca_envs = [
            ('proeduca-des', 'proeduca', 'des', 'Desarrollo', 'Entorno de desarrollo PROEDUCA', 1, 1, now),
            ('proeduca-pre', 'proeduca', 'pre', 'Preproducción', 'Entorno de preproducción PROEDUCA', 2, 1, now),
            ('proeduca-test', 'proeduca', 'test', 'Test', 'Entorno de testing PROEDUCA', 3, 1, now),
            ('proeduca-pro', 'proeduca', 'pro', 'Producción', 'Entorno de producción PROEDUCA', 4, 1, now)
        ]
        
        # Entornos VILLANUEVA
        villanueva_envs = [
            ('villanueva-pre', 'villanueva', 'pre', 'Preproducción', 'Entorno de preproducción VILLANUEVA', 1, 1, now),
            ('villanueva-pro', 'villanueva', 'pro', 'Producción', 'Entorno de producción VILLANUEVA', 2, 1, now)
        ]
        
        all_envs = proeduca_envs + villanueva_envs
        
        cursor.executemany("""
            INSERT OR IGNORE INTO environments 
            (id, organization_id, name, display_name, description, order_priority, active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, all_envs)
        
        print("✅ Datos iniciales insertados")
    
    def modify_existing_tables(self):
        """Modificar tablas existentes para el nuevo esquema."""
        cursor = self.conn.cursor()
        
        print("🔧 Modificando tablas existentes...")
        
        # Verificar si ya existe la columna organization_id en applications
        cursor.execute("PRAGMA table_info(applications)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'organization_id' not in columns:
            # Agregar columna organization_id a applications
            cursor.execute("""
                ALTER TABLE applications 
                ADD COLUMN organization_id TEXT DEFAULT 'proeduca'
            """)
            
            # Establecer organización por defecto para aplicaciones existentes
            cursor.execute("""
                UPDATE applications 
                SET organization_id = 'proeduca' 
                WHERE organization_id IS NULL
            """)
        
        # Verificar si ya existe la columna environment_id en deployments
        cursor.execute("PRAGMA table_info(deployments)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'environment_id' not in columns:
            # Agregar columna environment_id a deployments
            cursor.execute("""
                ALTER TABLE deployments 
                ADD COLUMN environment_id TEXT
            """)
        
        print("✅ Tablas existentes modificadas")
    
    def migrate_deployment_data(self):
        """Migrar datos de deployments del campo environment al nuevo environment_id."""
        cursor = self.conn.cursor()
        
        print("🔄 Migrando datos de deployments...")
        
        # Mapeo de entornos antiguos a nuevos IDs
        # Asumimos que los datos actuales son de PROEDUCA
        env_mapping = {
            'dev': 'proeduca-des',
            'pre': 'proeduca-pre', 
            'test': 'proeduca-test',
            'prod': 'proeduca-pro',
            'pro': 'proeduca-pro'  # Por si había inconsistencias
        }
        
        # Obtener deployments únicos con su entorno
        cursor.execute("SELECT DISTINCT environment FROM deployments WHERE environment IS NOT NULL")
        existing_envs = [row[0] for row in cursor.fetchall()]
        
        print(f"📋 Entornos encontrados en datos actuales: {existing_envs}")
        
        # Migrar cada entorno
        for old_env in existing_envs:
            new_env_id = env_mapping.get(old_env)
            if new_env_id:
                cursor.execute("""
                    UPDATE deployments 
                    SET environment_id = ? 
                    WHERE environment = ? AND environment_id IS NULL
                """, (new_env_id, old_env))
                
                affected = cursor.rowcount
                print(f"  ✅ {old_env} → {new_env_id}: {affected} registros migrados")
            else:
                print(f"  ⚠️ Entorno no mapeado: {old_env}")
        
        # Verificar migración
        cursor.execute("SELECT COUNT(*) FROM deployments WHERE environment_id IS NULL")
        unmigrated = cursor.fetchone()[0]
        
        if unmigrated > 0:
            print(f"⚠️ {unmigrated} deployments sin migrar")
        else:
            print("✅ Todos los deployments migrados correctamente")
    
    def create_sample_urls(self):
        """Crear URLs de ejemplo para algunos componentes."""
        cursor = self.conn.cursor()
        
        print("🌐 Creando URLs de ejemplo...")
        
        # Obtener algunos componentes para crear URLs de ejemplo
        cursor.execute("""
            SELECT ac.id, ac.name, ac.type, a.name as app_name
            FROM application_components ac
            JOIN applications a ON ac.application_id = a.id
            LIMIT 3
        """)
        
        components = cursor.fetchall()
        now = datetime.now().isoformat()
        
        sample_urls = []
        url_counter = 1
        
        for comp_id, comp_name, comp_type, app_name in components:
            # URLs para entornos de PROEDUCA
            proeduca_envs = ['proeduca-des', 'proeduca-pre', 'proeduca-test', 'proeduca-pro']
            env_names = ['des', 'pre', 'test', 'pro']
            
            for env_id, env_name in zip(proeduca_envs, env_names):
                if comp_type == 'frontend':
                    # URL principal de la aplicación
                    sample_urls.append((
                        f"url-{url_counter}", env_id, comp_id, 'main_app',
                        f"https://{app_name.lower().replace(' ', '-')}-{env_name}.proeduca.es",
                        f"Aplicación principal {comp_name}", 1, now
                    ))
                    url_counter += 1
                    
                    # API de versión
                    sample_urls.append((
                        f"url-{url_counter}", env_id, comp_id, 'version_api', 
                        f"https://{app_name.lower().replace(' ', '-')}-{env_name}.proeduca.es/api/version",
                        f"API de versión {comp_name}", 1, now
                    ))
                    url_counter += 1
                
                elif comp_type == 'backend':
                    # Health check
                    sample_urls.append((
                        f"url-{url_counter}", env_id, comp_id, 'health_check',
                        f"https://api-{app_name.lower().replace(' ', '-')}-{env_name}.proeduca.es/health",
                        f"Health check {comp_name}", 1, now
                    ))
                    url_counter += 1
                    
                    # API de versión
                    sample_urls.append((
                        f"url-{url_counter}", env_id, comp_id, 'version_api',
                        f"https://api-{app_name.lower().replace(' ', '-')}-{env_name}.proeduca.es/api/version", 
                        f"API de versión {comp_name}", 1, now
                    ))
                    url_counter += 1
        
        if sample_urls:
            cursor.executemany("""
                INSERT OR IGNORE INTO environment_urls 
                (id, environment_id, component_id, url_type, url, description, active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_urls)
            
            print(f"✅ {len(sample_urls)} URLs de ejemplo creadas")
    
    def verify_migration(self):
        """Verificar que la migración se completó correctamente."""
        cursor = self.conn.cursor()
        
        print("🔍 Verificando migración...")
        
        # Verificar datos en nuevas tablas
        cursor.execute("SELECT COUNT(*) FROM organizations")
        org_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM environments") 
        env_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM environment_urls")
        url_count = cursor.fetchone()[0]
        
        print(f"📊 Organizaciones: {org_count}")
        print(f"📊 Entornos: {env_count}")
        print(f"📊 URLs: {url_count}")
        
        # Verificar integridad referencial
        cursor.execute("PRAGMA foreign_key_check")
        fk_errors = cursor.fetchall()
        
        if fk_errors:
            print(f"❌ Errores de integridad referencial: {fk_errors}")
            return False
        
        # Verificar migración de deployments
        cursor.execute("SELECT COUNT(*) FROM deployments WHERE environment_id IS NOT NULL")
        migrated_deployments = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM deployments")
        total_deployments = cursor.fetchone()[0]
        
        print(f"📊 Deployments migrados: {migrated_deployments}/{total_deployments}")
        
        if migrated_deployments == total_deployments:
            print("✅ Migración completada exitosamente")
            return True
        else:
            print("⚠️ Migración incompleta")
            return False
    
    def generate_migration_report(self):
        """Generar reporte de migración."""
        cursor = self.conn.cursor()
        
        report = {
            "migration_date": datetime.now().isoformat(),
            "backup_file": str(self.backup_path) if self.backup_path else None,
            "organizations": [],
            "environments": [],
            "migration_summary": {}
        }
        
        # Organizaciones
        cursor.execute("SELECT * FROM organizations")
        for row in cursor.fetchall():
            report["organizations"].append({
                "id": row[0], "name": row[1], "display_name": row[2]
            })
        
        # Entornos por organización
        cursor.execute("""
            SELECT o.name, e.name, e.display_name, e.order_priority 
            FROM organizations o 
            JOIN environments e ON o.id = e.organization_id 
            ORDER BY o.name, e.order_priority
        """)
        for row in cursor.fetchall():
            report["environments"].append({
                "organization": row[0], "env_name": row[1], 
                "display_name": row[2], "priority": row[3]
            })
        
        # Resumen de migración
        cursor.execute("SELECT COUNT(*) FROM applications WHERE organization_id IS NOT NULL")
        apps_migrated = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM deployments WHERE environment_id IS NOT NULL")
        deployments_migrated = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM environment_urls")
        urls_created = cursor.fetchone()[0]
        
        report["migration_summary"] = {
            "applications_migrated": apps_migrated,
            "deployments_migrated": deployments_migrated,
            "urls_created": urls_created
        }
        
        # Guardar reporte
        report_path = self.db_path.parent / f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Reporte de migración guardado: {report_path}")
        return report
    
    def run_migration(self):
        """Ejecutar migración completa."""
        try:
            print("🚀 Iniciando migración de base de datos...")
            print("=" * 60)
            
            # 1. Crear backup
            self.create_backup()
            
            # 2. Conectar a BD
            self.connect()
            
            # 3. Verificar esquema actual
            self.verify_current_schema()
            
            # 4. Crear nuevas tablas
            self.create_new_tables()
            
            # 5. Insertar datos iniciales
            self.insert_initial_data()
            
            # 6. Modificar tablas existentes
            self.modify_existing_tables()
            
            # 7. Migrar datos de deployments
            self.migrate_deployment_data()
            
            # 8. Crear URLs de ejemplo
            self.create_sample_urls()
            
            # 9. Commit cambios
            self.conn.commit()
            
            # 10. Verificar migración
            success = self.verify_migration()
            
            # 11. Generar reporte
            self.generate_migration_report()
            
            if success:
                print("🎉 ¡Migración completada exitosamente!")
                print(f"💾 Backup disponible en: {self.backup_path}")
            else:
                print("⚠️ Migración completada con advertencias")
                
        except Exception as e:
            print(f"❌ Error durante la migración: {e}")
            if self.conn:
                self.conn.rollback()
            raise
        finally:
            self.close()

def main():
    """Función principal del script de migración."""
    print("🗄️ MIGRACIÓN DE BASE DE DATOS - Sistema Multi-Organización")
    print("=" * 70)
    print()
    print("Este script migrará tu base de datos para soportar:")
    print("• Múltiples organizaciones (proeduca, villanueva)")
    print("• Entornos flexibles por organización")
    print("• URLs específicas por entorno/componente")
    print()
    
    # Confirmar ejecución
    response = input("¿Continuar con la migración? (s/N): ").lower().strip()
    if response not in ['s', 'sí', 'si', 'yes', 'y']:
        print("❌ Migración cancelada")
        return
    
    try:
        migration = DatabaseMigration()
        migration.run_migration()
        
    except Exception as e:
        print(f"💥 Error fatal: {e}")
        print("🔄 Restaurar desde backup si es necesario")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())