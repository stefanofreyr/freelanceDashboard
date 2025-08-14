"""
Mantiene solo `display_name` nella tabella `users`.
Copia i dati da `name` a `display_name` se quest'ultimo è vuoto,
poi rimuove la colonna `name`.
⚠ Fai un backup prima di eseguire!
"""

import sqlite3
import shutil

DB_PATH = "/data/fatture.db"  # Cambia percorso se necessario

# 1. Backup
backup_path = DB_PATH + ".backup"
shutil.copy(DB_PATH, backup_path)
print(f"Backup creato: {backup_path}")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 2. Copia `name` in `display_name` dove `display_name` è vuoto
cur.execute("""
UPDATE users
SET display_name = name
WHERE (display_name IS NULL OR display_name = '')
AND name IS NOT NULL
""")

# 3. Disattiva foreign keys
cur.execute("PRAGMA foreign_keys=off;")

# 4. Ricrea tabella senza `name`
cur.execute("""
CREATE TABLE users_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    display_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# 5. Copia dati nella nuova tabella
cur.execute("""
INSERT INTO users_new (id, email, password_hash, display_name, created_at)
SELECT id, email, password_hash, display_name, created_at
FROM users
""")

# 6. Sostituzione
cur.execute("DROP TABLE users;")
cur.execute("ALTER TABLE users_new RENAME TO users;")
cur.execute("PRAGMA foreign_keys=on;")

conn.commit()
conn.close()

print("Colonna `name` rimossa, tutti i dati unificati in `display_name`.")
