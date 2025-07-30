# utils/db.py
import sqlite3

DB_NAME = "data/fatture.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            descrizione TEXT,
            importo REAL,
            data TEXT,
            iva REAL,
            totale REAL
        )
    ''')
    conn.commit()
    conn.close()

def insert_invoice(cliente, descrizione, importo, data, iva, totale):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO invoices (cliente, descrizione, importo, data, iva, totale)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (cliente, descrizione, importo, data, iva, totale))
    conn.commit()
    conn.close()

def get_all_invoices():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM invoices ORDER BY data DESC')
    data = c.fetchall()
    conn.close()
    return data
