"""
Rinumerazione sequenziale degli ID nella tabella `users`
e aggiornamento dei riferimenti nelle tabelle collegate.
⚠ FARE BACKUP PRIMA!
"""

import sqlite3
import shutil

DB_PATH = "/data/fatture.db"

# 1. Backup
backup_path = DB_PATH + ".backup_before_reindex"
shutil.copy(DB_PATH, backup_path)
print(f"Backup creato in: {backup_path}")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 2. Disattiva foreign keys temporaneamente
cur.execute("PRAGMA foreign_keys=off;")

# 3. Leggi tutti gli utenti ordinati per id
cur.execute("SELECT id, email FROM users ORDER BY id ASC")
users = cur.fetchall()

# 4. Crea mappa vecchio_id → nuovo_id
id_map = {old_id: new_id for new_id, (old_id, _) in enumerate(users, start=1)}

# 5. Aggiorna tutti i riferimenti nelle altre tabelle
# ⚠ Qui devi mettere le tabelle che hanno una colonna user_id
tables_with_user_id = ["invoices", "payments"]  # <-- Modifica in base al tuo schema

for table in tables_with_user_id:
    cur.execute(f"PRAGMA table_info({table})")
    cols = [c[1] for c in cur.fetchall()]
    if "user_id" in cols:
        for old_id, new_id in id_map.items():
            cur.execute(f"UPDATE {table} SET user_id = ? WHERE user_id = ?", (new_id, old_id))

# 6. Aggiorna la tabella users
#    Creiamo una nuova tabella con id sequenziali e poi sostituiamo
cur.execute("""
CREATE TABLE users_new AS
SELECT NULL as id, email, password_hash, display_name, created_at
FROM users ORDER BY id ASC
""")

# Aggiorna gli ID sequenziali nella nuova tabella
cur.execute("""
CREATE TABLE temp_users AS
SELECT ROW_NUMBER() OVER (ORDER BY email) as id,
       email, password_hash, display_name, created_at
FROM users_new
""")

cur.execute("DROP TABLE users;")
cur.execute("ALTER TABLE temp_users RENAME TO users;")

# 7. Riattiva foreign keys
cur.execute("PRAGMA foreign_keys=on;")

conn.commit()
conn.close()

print("Rinumerazione completata. ID compattati e riferimenti aggiornati.")
