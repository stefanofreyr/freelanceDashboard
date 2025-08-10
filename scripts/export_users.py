# scripts/export_users.py
import sqlite3
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = str(BASE_DIR / "data" / "fatture.db")
OUT_FILE = Path("utenti.csv")

def export_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, display_name, created_at FROM users")
    rows = cursor.fetchall()
    headers = [d[0] for d in cursor.description]
    conn.close()

    with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    print(f"Esportati {len(rows)} utenti in {OUT_FILE}")

if __name__ == "__main__":
    export_users()
