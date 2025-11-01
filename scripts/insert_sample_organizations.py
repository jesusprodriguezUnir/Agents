import sqlite3
import os

DB_PATH = os.environ.get("DB_PATH", "data/deployments.db")

ORG_DATA = [
    {"name": "proeduca", "display_name": "Proeduca"},
    {"name": "villanueva", "display_name": "Villanueva"},
]

def ensure_organizations():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            display_name TEXT
        )
    """)
    for org in ORG_DATA:
        cur.execute(
            "SELECT id FROM organizations WHERE name = ?", (org["name"],)
        )
        if cur.fetchone() is None:
            cur.execute(
                "INSERT INTO organizations (name, display_name) VALUES (?, ?)",
                (org["name"], org["display_name"])
            )
            print(f"Organización añadida: {org['display_name']} ({org['name']})")
        else:
            print(f"Organización ya existe: {org['display_name']} ({org['name']})")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    ensure_organizations()
    print("Proceso finalizado.")
