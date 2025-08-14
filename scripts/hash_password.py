import sqlite3
import bcrypt

DB_PATH = "/data/fatture.db"

# Funzione per hashare
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Seleziona utenti con password in chiaro (qui riconosciamo quelle uguali a 'pass1234')
cur.execute("SELECT id, password_hash FROM users")
users = cur.fetchall()

for user_id, pwd in users:
    if pwd == "pass1234":  # qui puoi aggiungere altri check se servono
        hashed = hash_password(pwd)
        cur.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hashed, user_id))
        print(f"Hash aggiornata per utente ID {user_id}")

conn.commit()
conn.close()
