import pathlib
import sqlite3
import datetime

DB_NAME = "data/fatture.db"

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
DB_PATH = str(BASE_DIR / "data" / "fatture.db")

def init_db():
    # 1️⃣ Crea le tabelle base
    init_users_table()
    init_invoice_table()
    init_clienti_table()
    init_eventi_table()
    init_settings_table()

    # 2️⃣ Migrazioni schema
    patch_add_user_id()        # Colonna user_id su tutte le tabelle
    backfill_user_id()         # Popola user_id dove possibile

    patch_invoices_add_year()  # Colonna anno + backfill da data

    # 3️⃣ Indici (solo dopo che le colonne esistono)
    patch_add_indexes()

def _conn():
    """Connessione SQLite con FK attive."""
    pathlib.Path("data").mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_users_table():
    """Crea la tabella users se non esiste."""
    with _conn() as c:
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              email TEXT NOT NULL UNIQUE,
              password_hash TEXT NOT NULL,
              display_name TEXT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        c.commit()

def init_invoice_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_fattura INTEGER,
            cliente TEXT,
            descrizione TEXT,
            importo REAL,
            data TEXT,
            iva REAL,
            totale REAL,
            email TEXT,
            utente TEXT,
            anno INTEGER    
        )
    ''')
    conn.commit()
    conn.close()


def init_clienti_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS clienti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT,
            pec TEXT,
            telefono TEXT,
            indirizzo TEXT,
            piva TEXT,
            cf TEXT,
            note TEXT,
            utente TEXT
        )
    ''')
    conn.commit()
    conn.close()


def init_eventi_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS eventi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titolo TEXT,
            data TEXT,
            ora TEXT,
            cliente TEXT,
            descrizione TEXT,
            utente TEXT
        )
    ''')
    conn.commit()
    conn.close()


def get_user_id_by_email(email: str) -> int | None:
    if not email:
        return None
    norm = (email or "").strip().lower()   # aggiungi normalizzazione
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    row = c.execute("SELECT id FROM users WHERE email=?", (norm,)).fetchone()
    conn.close()
    return row[0] if row else None


def get_user_by_email(email: str):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    norm = (email or "").strip().lower()
    row = c.execute("SELECT * FROM users WHERE email=?", (norm,)).fetchone()
    conn.close()
    return dict(row) if row else None



def create_user(email: str, hashed_pw: bytes, display_name: str) -> int | None:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    norm = (email or "").strip().lower()          # ⬅ normalizza
    # salva come testo ASCII, non bytes (bcrypt produce ASCII-safe)
    if isinstance(hashed_pw, bytes):
        hashed_pw = hashed_pw.decode()
    c.execute(
        "INSERT INTO users (email, password_hash, display_name) VALUES (?, ?, ?)",
        (norm, hashed_pw, display_name)
    )
    uid = c.lastrowid
    conn.commit()
    conn.close()
    return uid


# === FATTURE ===

def insert_invoice(numero, cliente, descrizione, importo, data, iva, totale, email, utente=None,
                   user_id=None, anno=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Compat: se non arriva user_id ma arriva l'email in utente, prova a ricavarlo
    if user_id is None and utente:
        user_id = get_user_id_by_email(utente)
    # Anno default da data
    if anno is None and data:
        try:
            anno = int(str(data)[:4])
        except Exception:
            anno = None
    c.execute('''
        INSERT INTO invoices (numero_fattura, cliente, descrizione, importo, data, iva, totale, email, utente, user_id, anno)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (numero, cliente, descrizione, importo, data, iva, totale, email, utente, user_id, anno))
    conn.commit()
    conn.close()


def get_all_invoices(utente):
    """LEGACY: filtra per email (colonna 'utente'). Usa solo durante la transizione."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM invoices WHERE utente = ? ORDER BY data DESC', (utente,))
    data = c.fetchall()
    conn.close()
    return data


def get_all_invoices_by_user_id(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    rows = c.execute(
        'SELECT * FROM invoices WHERE user_id = ? ORDER BY data DESC',
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_invoice_totals_by_user_id(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    row = c.execute(
        'SELECT COUNT(*), COALESCE(SUM(totale),0) FROM invoices WHERE user_id=?',
        (user_id,)
    ).fetchone()
    conn.close()
    return {"count": row[0], "sum": float(row[1] or 0.0)}



def get_next_invoice_number(utente):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT MAX(numero_fattura) FROM invoices WHERE utente = ?', (utente,))
    result = c.fetchone()[0]
    conn.close()
    return (result or 0) + 1


def get_next_invoice_number_for_year_by_user_id(user_id: int, anno: int):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT MAX(numero_fattura) FROM invoices WHERE user_id=? AND anno=?', (user_id, anno))
    result = c.fetchone()[0]
    conn.close()
    return (result or 0) + 1

# === CLIENTI ===

def aggiungi_cliente(nome, email, pec, telefono, indirizzo, piva, cf, note, utente=None, user_id=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if user_id is None and utente:
        user_id = get_user_id_by_email(utente)
    c.execute('''
        INSERT INTO clienti (nome, email, pec, telefono, indirizzo, piva, cf, note, utente, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nome, email, pec, telefono, indirizzo, piva, cf, note, utente, user_id))
    conn.commit()
    conn.close()


def update_cliente(cliente_id, nome, email, pec, telefono, indirizzo, piva, cf, note):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        UPDATE clienti
        SET nome = ?, email = ?, pec = ?, telefono = ?, indirizzo = ?, piva = ?, cf = ?, note = ?
        WHERE id = ?
    ''', (nome, email, pec, telefono, indirizzo, piva, cf, note, cliente_id))
    conn.commit()
    conn.close()


def lista_clienti(utente=None):
    # LEGACY
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if utente:
        c.execute('SELECT * FROM clienti WHERE utente = ? ORDER BY nome', (utente,))
    else:
        c.execute('SELECT * FROM clienti ORDER BY nome')
    rows = c.fetchall()
    conn.close()
    return [{
        "id": r[0],
        "nome": r[1],
        "email": r[2],
        "pec": r[3],
        "telefono": r[4],
        "indirizzo": r[5],
        "piva": r[6],
        "cf": r[7],
        "note": r[8]
    } for r in rows]


def lista_clienti_by_user_id(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM clienti WHERE user_id = ? ORDER BY nome', (user_id,))
    rows = c.fetchall()
    conn.close()
    return [{
        "id": r[0],
        "nome": r[1],
        "email": r[2],
        "pec": r[3],
        "telefono": r[4],
        "indirizzo": r[5],
        "piva": r[6],
        "cf": r[7],
        "note": r[8]
    } for r in rows]


def lista_clienti_raggruppati_by_user_id(user_id: int):
    clienti = lista_clienti_by_user_id(user_id)
    from collections import defaultdict
    raggruppati = defaultdict(list)
    for cliente in clienti:
        iniziale = (cliente['nome'][:1] or "#").upper()
        raggruppati[iniziale].append(cliente)
    return dict(raggruppati)


def elimina_cliente(cliente_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM clienti WHERE id = ?", (cliente_id,))
    conn.commit()
    conn.close()


def fatture_per_cliente(nome_cliente, utente):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT * FROM invoices
        WHERE cliente = ? AND utente = ?
        ORDER BY data DESC
    ''', (nome_cliente, utente))
    rows = c.fetchall()
    conn.close()
    return rows


def get_cliente_by_id(cliente_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM clienti WHERE id = ?", (cliente_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_invoices_by_client_and_user_id(cliente: str, user_id: int):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    rows = c.execute("""
        SELECT * FROM invoices
        WHERE cliente=? AND user_id=?
        ORDER BY data DESC
    """, (cliente, user_id)).fetchall()
    conn.close()
    return rows


# === EVENTI ===

def aggiungi_evento(titolo, data, ora, cliente, descrizione, utente=None, user_id=None):
    # 🔹 Conversione formati compatibili con SQLite
    if hasattr(data, "strftime"):  # datetime.date o datetime.datetime
        data = data.strftime("%Y-%m-%d")
    if hasattr(ora, "strftime"):   # datetime.time
        ora = ora.strftime("%H:%M")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if user_id is None and utente:
        user_id = get_user_id_by_email(utente)

    c.execute('''
        INSERT INTO eventi (titolo, data, ora, cliente, descrizione, utente, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (titolo, data, ora, cliente, descrizione, utente, user_id))

    conn.commit()
    conn.close()



def lista_eventi_futuri(utente):
    """LEGACY: filtra per 'utente' (email)."""
    today = datetime.date.today().isoformat()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT * FROM eventi WHERE data >= ? AND utente = ? ORDER BY data, ora
    ''', (today, utente))
    rows = c.fetchall()
    conn.close()
    return [{
        "id": r[0],
        "titolo": r[1],
        "data": r[2],
        "ora": r[3],
        "cliente": r[4],
        "descrizione": r[5]
    } for r in rows]


def lista_eventi_futuri_by_user_id(user_id: int):
    today = datetime.date.today().isoformat()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT * FROM eventi WHERE data >= ? AND user_id = ? ORDER BY data, ora
    ''', (today, user_id))
    rows = c.fetchall()
    conn.close()
    return [{
        "id": r[0],
        "titolo": r[1],
        "data": r[2],
        "ora": r[3],
        "cliente": r[4],
        "descrizione": r[5]
    } for r in rows]


def eventi_in_scadenza(utente):
    domani = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM eventi WHERE data = ? AND utente = ?", (domani, utente))
    rows = c.fetchall()
    conn.close()
    return [{
        "id": r[0],
        "titolo": r[1],
        "data": r[2],
        "ora": r[3],
        "cliente": r[4],
        "descrizione": r[5]
    } for r in rows]


def update_evento(evento_id, titolo, data, ora, cliente, descrizione):
    if hasattr(data, "strftime"):
        data = data.strftime("%Y-%m-%d")
    if hasattr(ora, "strftime"):
        ora = ora.strftime("%H:%M")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        UPDATE eventi
        SET titolo = ?, data = ?, ora = ?, cliente = ?, descrizione = ?
        WHERE id = ?
    """, (titolo, data, ora, cliente, descrizione, evento_id))
    conn.commit()
    conn.close()


def elimina_evento(evento_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM eventi WHERE id = ?", (evento_id,))
    conn.commit()
    conn.close()


def get_eventi_per_data(utente, data):
    """Ritorna tutti gli eventi di un utente per una specifica data."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT * FROM eventi
        WHERE utente = ?
        AND data = ?
        ORDER BY ora ASC
    """, (utente, data))
    risultati = [dict(row) for row in c.fetchall()]
    conn.close()
    return risultati


def get_eventi_per_intervallo(utente, data_inizio, data_fine):
    """Ritorna tutti gli eventi di un utente in un intervallo di date."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT * FROM eventi
        WHERE utente = ?
        AND data BETWEEN ? AND ?
        ORDER BY data ASC, ora ASC
    """, (utente, data_inizio, data_fine))
    risultati = [dict(row) for row in c.fetchall()]
    conn.close()
    return risultati


# === SETTINGS ===

def init_settings_table():
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS settings (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT NOT NULL UNIQUE,             -- chiave utente (ora usiamo email)
      ragione_sociale TEXT,
      indirizzo TEXT,
      piva TEXT,
      iva_default REAL DEFAULT 22.0,
      pec_provider TEXT,
      pec_user TEXT,
      pec_pass TEXT,
      test_mode INTEGER DEFAULT 1,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit(); conn.close()


def get_settings(email):
    conn = sqlite3.connect(DB_NAME); conn.row_factory = sqlite3.Row
    c = conn.cursor()
    row = c.execute("SELECT * FROM settings WHERE email=?", (email,)).fetchone()
    conn.close()
    return dict(row) if row else None


def upsert_settings(email, **kwargs):
    fields = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [email]
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("INSERT INTO settings (email) VALUES (?) ON CONFLICT(email) DO NOTHING", (email,))
    c.execute(f"UPDATE settings SET {fields}, updated_at=CURRENT_TIMESTAMP WHERE email=?", vals)
    conn.commit(); conn.close()


def patch_invoices_add_year():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("PRAGMA table_info(invoices)")
    cols = [x[1] for x in c.fetchall()]

    if "anno" not in cols:
        print("[DB PATCH] Colonna 'anno' mancante, la creo...")
        c.execute("ALTER TABLE invoices ADD COLUMN anno INTEGER")
        c.execute("""
            UPDATE invoices
            SET anno = CAST(strftime('%Y', data) AS INTEGER)
            WHERE data IS NOT NULL
        """)
        conn.commit()
    else:
        print("[DB PATCH] Colonna 'anno' già presente")

    conn.close()


def get_next_invoice_number_for_year(email, anno):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    row = c.execute("SELECT MAX(numero_fattura) FROM invoices WHERE utente=? AND anno=?", (email, anno)).fetchone()
    conn.close()
    return (row[0] or 0) + 1


def patch_add_user_id():
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    # invoices
    c.execute("PRAGMA table_info(invoices)")
    if "user_id" not in [col[1] for col in c.fetchall()]:
        c.execute("ALTER TABLE invoices ADD COLUMN user_id INTEGER REFERENCES users(id)")
    # clienti
    c.execute("PRAGMA table_info(clienti)")
    if "user_id" not in [col[1] for col in c.fetchall()]:
        c.execute("ALTER TABLE clienti ADD COLUMN user_id INTEGER REFERENCES users(id)")
    # eventi
    c.execute("PRAGMA table_info(eventi)")
    if "user_id" not in [col[1] for col in c.fetchall()]:
        c.execute("ALTER TABLE eventi ADD COLUMN user_id INTEGER REFERENCES users(id)")
    conn.commit(); conn.close()


def backfill_user_id():
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    users_map = {row[1]: row[0] for row in c.execute("SELECT id, email FROM users")}
    for tbl in ("invoices", "clienti", "eventi"):
        for rowid, email in c.execute(f"SELECT id, utente FROM {tbl}"):
            uid = users_map.get(email)
            if uid:
                c.execute(f"UPDATE {tbl} SET user_id=? WHERE id=?", (uid, rowid))
    conn.commit(); conn.close()


def patch_add_indexes():
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("""
      CREATE UNIQUE INDEX IF NOT EXISTS ux_invoices_num_anno_user
      ON invoices (numero_fattura, anno, user_id)
    """)
    c.execute("CREATE INDEX IF NOT EXISTS ix_clienti_user_nome ON clienti (user_id, nome)")
    c.execute("CREATE INDEX IF NOT EXISTS ix_eventi_user_data ON eventi (user_id, data)")
    conn.commit(); conn.close()


"""
def patch_clienti_add_utente_column():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("PRAGMA table_info(clienti)")
    columns = [col[1] for col in c.fetchall()]
    if "utente" not in columns:
        c.execute("ALTER TABLE clienti ADD COLUMN utente TEXT")
        conn.commit()
        print("✅ Colonna 'utente' aggiunta con successo.")
    else:
        print("ℹ️ Colonna 'utente' già esistente.")
    conn.close()

def patch_clienti_add_cf_column():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("PRAGMA table_info(clienti)")
    columns = [col[1] for col in c.fetchall()]
    if "cf" not in columns:
        c.execute("ALTER TABLE clienti ADD COLUMN cf TEXT")
        conn.commit()
        print("✅ Colonna 'cf' aggiunta con successo.")
    else:
        print("ℹ️ Colonna 'cf' già esistente.")
    conn.close()


def patch_invoices_add_utente_column():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("PRAGMA table_info(invoices)")
    columns = [col[1] for col in c.fetchall()]
    if "utente" not in columns:
        c.execute("ALTER TABLE invoices ADD COLUMN utente TEXT")
        conn.commit()
        print("✅ Colonna 'utente' aggiunta a invoices.")
    else:
        print("ℹ️ Colonna 'utente' già esistente in invoices.")
    conn.close()


def patch_eventi_add_utente_column():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("PRAGMA table_info(eventi)")
    columns = [col[1] for col in c.fetchall()]
    if "utente" not in columns:
        c.execute("ALTER TABLE eventi ADD COLUMN utente TEXT")
        conn.commit()
        print("✅ Colonna 'utente' aggiunta a eventi.")
    else:
        print("ℹ️ Colonna 'utente' già esistente in eventi.")
    conn.close()
"""