import sqlite3
from datetime import datetime, timedelta

DB_PATH = "data/deployments.db"

ORG_NAMES = [
    {"name": "proeduca", "display_name": "Proeduca"},
    {"name": "villanueva", "display_name": "Villanueva"},
]

ENV_NAMES = [
    {"name": "dev", "description": "Desarrollo"},
    {"name": "pre", "description": "Preproducción"},
    {"name": "prod", "description": "Producción"},
]

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Obtener organizaciones
    orgs = {}
    for org in ORG_NAMES:
        cur.execute("SELECT id FROM organizations WHERE name = ?", (org["name"],))
        row = cur.fetchone()
        if row:
            orgs[org["name"]] = row[0]
        else:
            print(f"Organización no encontrada: {org['name']}")

    # Crear entornos y despliegues
    for org_name, org_id in orgs.items():
        for env in ENV_NAMES:
            # Crear entorno si no existe
            cur.execute("SELECT id FROM environments WHERE name = ? AND organization_id = ?", (env["name"], org_id))
            env_row = cur.fetchone()
            if env_row:
                env_id = env_row[0]
                print(f"Entorno ya existe: {env['name']} para {org_name}")
            else:
                cur.execute(
                    "INSERT INTO environments (name, description, organization_id) VALUES (?, ?, ?)",
                    (env["name"], env["description"], org_id)
                )
                env_id = cur.lastrowid
                print(f"Entorno creado: {env['name']} para {org_name}")
            # Crear despliegue de ejemplo si no existe
            cur.execute("SELECT id FROM deployments WHERE environment_id = ?", (env_id,))
            if not cur.fetchone():
                deployed_at = (datetime.now() - timedelta(days=env_id)).isoformat()
                cur.execute(
                    "INSERT INTO deployments (environment_id, version, status, deployed_by, deployed_at, notes) VALUES (?, ?, ?, ?, ?, ?)",
                    (env_id, f"1.0.{env_id}", "success", "admin", deployed_at, f"Despliegue inicial en {env['name']}")
                )
                print(f"Despliegue creado en {env['name']} para {org_name}")
            else:
                print(f"Ya existe despliegue en {env['name']} para {org_name}")
    conn.commit()
    conn.close()
    print("Proceso finalizado.")

if __name__ == "__main__":
    main()
