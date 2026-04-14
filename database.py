# database.py
# Manejo de la base de datos SQLite y utilidades: usuarios, palets, ventas, export y sync a Google Sheets

import sqlite3
from passlib.hash import pbkdf2_sha256

DB_FILE = "nico_kiwi.db"

def get_conn():
    conn = sqlite3.connect(DB_FILE, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_conn()
    c = conn.cursor()
    # Usuarios
    c.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'operador'
    )
    ''')
    # Palets (empaquetadora)
    c.execute('''
    CREATE TABLE IF NOT EXISTS palets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        peso REAL NOT NULL,
        calibre TEXT NOT NULL,
        fecha TEXT NOT NULL,
        usuario TEXT NOT NULL
    )
    ''')
    # Ventas
    c.execute('''
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,             -- formato 'YYYY-MM-DD'
        caja_tipo TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        precio_unitario REAL NOT NULL,
        usuario TEXT NOT NULL
    )
    ''')
    # Tabla para llevar el último id sincronizado (Google Sheets)
    c.execute('''
    CREATE TABLE IF NOT EXISTS sync_status (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    ''')
    # Si no hay usuarios, crear admin por defecto
    c.execute("SELECT COUNT(*) AS cnt FROM usuarios")
    row = c.fetchone()
    if row and row["cnt"] == 0:
        pw_hash = pbkdf2_sha256.hash("admin")
        c.execute("INSERT INTO usuarios (username, password_hash, role) VALUES (?, ?, ?)",
                  ("admin", pw_hash, "admin"))
        print("-> Creado usuario por defecto -> usuario: admin / contraseña: admin  (cámbiala después)")
    # Asegurar clave last_sale_id
    c.execute("SELECT value FROM sync_status WHERE key='last_sale_id'")
    if not c.fetchone():
        c.execute("INSERT INTO sync_status (key, value) VALUES (?, ?)", ("last_sale_id", "0"))
    conn.commit()
    conn.close()

# --------------------------
# Usuarios
# --------------------------
def add_user(username, password, role="operador"):
    conn = get_conn()
    c = conn.cursor()
    try:
        pw_hash = pbkdf2_sha256.hash(password)
        c.execute("INSERT INTO usuarios (username, password_hash, role) VALUES (?, ?, ?)",
                  (username, pw_hash, role))
        conn.commit()
        return True, None
    except sqlite3.IntegrityError as e:
        return False, "El usuario ya existe"
    finally:
        conn.close()

def verify_user(username, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT password_hash FROM usuarios WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if not row:
        return False
    return pbkdf2_sha256.verify(password, row["password_hash"])

def list_users():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, username, role FROM usuarios ORDER BY username")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def update_user(user_id, new_username, new_password, new_role):
    conn = get_conn()
    c = conn.cursor()
    pw_hash = pbkdf2_sha256.hash(new_password)
    try:
        c.execute("UPDATE usuarios SET username=?, password_hash=?, role=? WHERE id=?",
                  (new_username, pw_hash, new_role, user_id))
        conn.commit()
        return True, None
    except sqlite3.IntegrityError:
        return False, "El nuevo nombre de usuario ya existe"
    finally:
        conn.close()

def delete_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

# --------------------------
# Palets (empaquetadora)
# --------------------------
def add_pallet(peso, calibre, fecha, usuario):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO palets (peso, calibre, fecha, usuario) VALUES (?, ?, ?, ?)",
              (peso, calibre, fecha, usuario))
    conn.commit()
    last_id = c.lastrowid
    conn.close()
    return last_id

def list_pallets():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, peso, calibre, fecha, usuario FROM palets ORDER BY fecha DESC, id DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_pallet(pallet_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, peso, calibre, fecha, usuario FROM palets WHERE id = ?", (pallet_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def update_pallet(pallet_id, peso, calibre, fecha, usuario):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE palets SET peso=?, calibre=?, fecha=?, usuario=? WHERE id=?",
              (peso, calibre, fecha, usuario, pallet_id))
    conn.commit()
    conn.close()

def delete_pallet(pallet_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM palets WHERE id=?", (pallet_id,))
    conn.commit()
    conn.close()

# --------------------------
# Ventas
# --------------------------
def add_sale(fecha, caja_tipo, cantidad, precio_unitario, usuario):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO ventas (fecha, caja_tipo, cantidad, precio_unitario, usuario) VALUES (?, ?, ?, ?, ?)",
              (fecha, caja_tipo, cantidad, precio_unitario, usuario))
    conn.commit()
    last_id = c.lastrowid
    conn.close()
    return last_id

def list_sales():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, fecha, caja_tipo, cantidad, precio_unitario, usuario FROM ventas ORDER BY fecha DESC, id DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_sale(sale_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, fecha, caja_tipo, cantidad, precio_unitario, usuario FROM ventas WHERE id = ?", (sale_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def update_sale(sale_id, fecha, caja_tipo, cantidad, precio_unitario, usuario):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE ventas SET fecha=?, caja_tipo=?, cantidad=?, precio_unitario=?, usuario=? WHERE id=?",
              (fecha, caja_tipo, cantidad, precio_unitario, usuario, sale_id))
    conn.commit()
    conn.close()

def delete_sale(sale_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM ventas WHERE id=?", (sale_id,))
    conn.commit()
    conn.close()

# --------------------------
# Reportes / agregados
# --------------------------
def sales_aggregate_by_day(start_date, end_date):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
    SELECT fecha, SUM(cantidad * precio_unitario) AS total_revenue, SUM(cantidad) AS total_cajas
    FROM ventas
    WHERE fecha BETWEEN ? AND ?
    GROUP BY fecha
    ORDER BY fecha
    ''', (start_date, end_date))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def sales_aggregate_by_month(start_date, end_date):
    conn = get_conn()
    c = conn.cursor()
    # substr(fecha,1,7) -> 'YYYY-MM'
    c.execute('''
    SELECT substr(fecha,1,7) AS mes, SUM(cantidad * precio_unitario) AS total_revenue, SUM(cantidad) AS total_cajas
    FROM ventas
    WHERE fecha BETWEEN ? AND ?
    GROUP BY mes
    ORDER BY mes
    ''', (start_date, end_date))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def average_daily_revenue(start_date, end_date):
    dias = sales_aggregate_by_day(start_date, end_date)
    if not dias:
        return 0.0
    total = sum(row["total_revenue"] for row in dias)
    return total / len(dias)

# --------------------------
# Export a Excel (pandas)
# --------------------------
def export_sales_to_excel(path):
    try:
        import pandas as pd
    except ImportError:
        raise Exception("Instala pandas y openpyxl: pip install pandas openpyxl")
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM ventas ORDER BY fecha DESC, id DESC", conn)
    df["total"] = df["cantidad"] * df["precio_unitario"]
    df.to_excel(path, index=False)
    conn.close()

def export_pallets_to_excel(path):
    try:
        import pandas as pd
    except ImportError:
        raise Exception("Instala pandas y openpyxl: pip install pandas openpyxl")
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM palets ORDER BY fecha DESC, id DESC", conn)
    df.to_excel(path, index=False)
    conn.close()

# --------------------------
# Google Sheets sync (opcional)
# --------------------------
def get_last_synced_sale_id():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT value FROM sync_status WHERE key='last_sale_id'")
    row = c.fetchone()
    conn.close()
    return int(row["value"]) if row and row["value"] is not None else 0

def set_last_synced_sale_id(last_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO sync_status (key, value) VALUES ('last_sale_id', ?)", (str(last_id),))
    conn.commit()
    conn.close()

def sync_sales_to_google(service_account_file, spreadsheet_id, sheet_name="Ventas"):
    """
    Sincroniza (append) las ventas nuevas (id > last_synced) al sheet dado.
    Requiere credenciales de cuenta de servicio (JSON) y que el sheet exista y esté compartido con la cuenta de servicio.
    """
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
    except ImportError:
        raise Exception("Instala google-api-python-client y google-auth: pip install google-api-python-client google-auth")

    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(service_account_file, scopes=SCOPES)
    service = build("sheets", "v4", credentials=creds)

    last_id = get_last_synced_sale_id()
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, fecha, caja_tipo, cantidad, precio_unitario, usuario FROM ventas WHERE id > ? ORDER BY id", (last_id,))
    rows = c.fetchall()
    if not rows:
        conn.close()
        return 0  # nada nuevo

    # crear header si no existe
    header_range = f"{sheet_name}!A1:F1"
    resp = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=header_range).execute()
    if not resp.get("values"):
        header = [["ID", "Fecha", "CajaTipo", "Cantidad", "PrecioUnitario", "Usuario"]]
        service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=header_range,
                                               valueInputOption="RAW", body={"values": header}).execute()

    values = []
    for r in rows:
        values.append([r["id"], r["fecha"], r["caja_tipo"], r["cantidad"], r["precio_unitario"], r["usuario"]])

    body = {"values": values}
    service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=f"{sheet_name}!A2",
                                           valueInputOption="RAW", insertDataOption="INSERT_ROWS", body=body).execute()

    new_last = rows[-1]["id"]
    set_last_synced_sale_id(new_last)
    conn.close()
    return len(values)