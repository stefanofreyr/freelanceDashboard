
import sqlite3
import datetime

DB_NAME = "data/fatture.db"


def init_db():
    init_invoice_table()
    init_clienti_table()
    init_eventi_table()


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
            utente TEXT
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
            partita_iva TEXT,
            codice_fiscale TEXT,
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


# === FATTURE ===

def insert_invoice(numero, cliente, descrizione, importo, data, iva, totale, email, utente):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO invoices (numero_fattura, cliente, descrizione, importo, data, iva, totale, email, utente)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (numero, cliente, descrizione, importo, data, iva, totale, email, utente))
    conn.commit()
    conn.close()


def get_all_invoices(utente):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM invoices WHERE utente = ? ORDER BY data DESC', (utente,))
    data = c.fetchall()
    conn.close()
    return data


def get_next_invoice_number():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT MAX(numero_fattura) FROM invoices')
    result = c.fetchone()[0]
    conn.close()
    return (result or 0) + 1


# === CLIENTI ===

def aggiungi_cliente(nome, email, pec, telefono, indirizzo, partita_iva, codice_fiscale, note, utente):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO clienti (nome, email, pec, telefono, indirizzo, partita_iva, codice_fiscale, note, utente)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nome, email, pec, telefono, indirizzo, partita_iva, codice_fiscale, note, utente))
    conn.commit()
    conn.close()


def update_cliente(cliente_id, nome, email, pec, telefono, indirizzo, partita_iva, codice_fiscale, note):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        UPDATE clienti
        SET nome = ?, email = ?, pec = ?, telefono = ?, indirizzo = ?, partita_iva = ?, codice_fiscale = ?, note = ?
        WHERE id = ?
    ''', (nome, email, pec, telefono, indirizzo, partita_iva, codice_fiscale, note, cliente_id))
    conn.commit()
    conn.close()


def lista_clienti(utente=None):
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
        "partita_iva": r[6],
        "codice_fiscale": r[7],
        "note": r[8]
    } for r in rows]


def lista_clienti_raggruppati(utente):
    clienti = lista_clienti(utente)
    from collections import defaultdict
    raggruppati = defaultdict(list)
    for cliente in clienti:
        iniziale = cliente['nome'][0].upper()
        raggruppati[iniziale].append(cliente)
    return dict(raggruppati)


def elimina_cliente(cliente_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM clienti WHERE id = ?", (cliente_id,))
    conn.commit()
    conn.close()


# === EVENTI ===

def aggiungi_evento(titolo, data, ora, cliente, descrizione, utente):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO eventi (titolo, data, ora, cliente, descrizione, utente)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (titolo, data, ora, cliente, descrizione, utente))
    conn.commit()
    conn.close()


def lista_eventi_futuri(utente):
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


def elimina_evento(evento_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM eventi WHERE id = ?", (evento_id,))
    conn.commit()
    conn.close()


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
