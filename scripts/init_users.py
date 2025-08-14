"""
scripts/init_users.py

- Controlla la tabella `users` e aggiunge la colonna `name` se manca.
- Crea utenti di test evitando duplicati (INSERT OR IGNORE).
"""

import sqlite3
import os
from utils.db import DB_PATH  # Percorso al tuo DB SQLite

# Lista utenti di test
USERS = [
    ("anna.rossi@fai.test",      "pass1234", "Anna Rossi"),
    ("luca.bianchi@fai.test",    "pass1234", "Luca Bianchi"),
    ("mario.verdi@fai.test",     "pass1234", "Mario Verdi"),
    ("giulia.neri@fai.test",     "pass1234", "Giulia Neri"),
    ("paolo.gallo@fai.test",     "pass1234", "Paolo Gallo"),
    ("chiara.fontana@fai.test",  "pass1234", "Chiara Fontana"),
    ("davide.moretti@fai.test",  "pass1234", "Davide Moretti"),
    ("francesca.greco@fai.test", "pass1234", "Francesca Greco"),
    ("matteo.romano@fai.test",   "pass1234", "Matteo Romano"),
    ("elisa.ferrari@fai.test",   "pass1234", "Elisa Ferrari"),
    ("stefano@fai.test",         "pass1234", "Stefano Castiglione"),
    ("castcla@fai.test",         "pass1234", "Claudio Castiglione"),
    ("cosimo@fai.test",          "pass1234", "Cosimo Dini"),
    ("clelia@fai.test",          "pass1234", "Clelia Dini")
]

def ensure_name_column():
    """Verifica se la colonna `name` esiste, altrimenti la aggiunge."""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cur = conn.cursor()

    # Recupera info colonne
    cur.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cur.fetchall()]

    # Se manca 'name', aggiungila
    if "name" not in columns:
        print("Colonna `name` mancante: aggiungo...")
        cur.execute("ALTER TABLE users ADD COLUMN name TEXT NOT NULL DEFAULT ''")
        conn.commit()
    else:
        print("Colonna `name` già presente.")

    conn.close()

def create_user(email, password, name):
    """Crea un utente, ignorando se già esiste."""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL
        )
    """)
    cur.execute("""
        INSERT OR IGNORE INTO users (email, password_hash, name)
        VALUES (?, ?, ?)
    """, (email, password, name))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    ensure_name_column()

    if not os.environ.get("USERS_INITIALIZED"):
        for email, pwd, name in USERS:
            try:
                create_user(email, pwd, name)
                print(f"Creato utente: {email} ({name})")
            except Exception as e:
                print(f"Errore creazione {email}: {e}")
        os.environ["USERS_INITIALIZED"] = "1"
    else:
        print("Utenti già inizializzati, salto creazione.")
