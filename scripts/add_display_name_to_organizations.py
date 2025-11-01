import sqlite3

DB_PATH = "data/deployments.db"

ALTER_SQL = """
ALTER TABLE organizations ADD COLUMN display_name TEXT;
"""

UPDATE_SQL = """
UPDATE organizations SET display_name = name WHERE display_name IS NULL OR display_name = '';
"""

def column_exists(conn, table, column):
    cur = conn.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cur.fetchall())

def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        if not column_exists(conn, "organizations", "display_name"):
            print("Agregando columna display_name a organizations...")
            conn.execute(ALTER_SQL)
            conn.commit()
        else:
            print("La columna display_name ya existe.")
        print("Rellenando display_name con name si está vacío...")
        conn.execute(UPDATE_SQL)
        conn.commit()
        print("Listo. Puedes verificar la tabla organizations.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
