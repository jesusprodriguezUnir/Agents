import sqlite3
import os

db_path = 'data/deployments.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Listar todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print('Tablas existentes:')
    for table in tables:
        print(f'  - {table[0]}')

    # Verificar si existe la tabla environments
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='environments';")
    if cursor.fetchone():
        print('\nTabla environments existe')
    else:
        print('\nTabla environments NO existe')

    # Verificar si existe la tabla organizations
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='organizations';")
    if cursor.fetchone():
        print('Tabla organizations existe')
    else:
        print('Tabla organizations NO existe')

    # Verificar columnas de deployments
    cursor.execute("PRAGMA table_info(deployments);")
    columns = cursor.fetchall()
    print('\nColumnas de tabla deployments:')
    for col in columns:
        print(f'  - {col[1]} ({col[2]})')

    conn.close()
else:
    print('Base de datos no encontrada')