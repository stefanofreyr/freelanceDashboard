# utils/db.py
import sqlite3
import os
from datetime import date

DB_NAME = "data/fatture.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_fattura TEXT,
            cliente TEXT,
            descrizione TEXT,
            importo REAL,
            data TEXT,
            iva REAL,
            totale REAL,
            email_cliente TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_next_invoice_number():
    """Genera il prossimo numero progressivo tipo '2025/001'."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM invoices")
    count = c.fetchone()[0]
    conn.close()

    year = date.today().year
    return f"{year}/{count + 1:03d}"

def insert_invoice(numero_fattura, cliente, descrizione, importo, data, iva, totale, email_cliente):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO invoices (numero_fattura, cliente, descrizione, importo, data, iva, totale, email_cliente)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (numero_fattura, cliente, descrizione, importo, data, iva, totale, email_cliente))
    conn.commit()
    conn.close()

def get_all_invoices():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # This makes rows accessible by column name
    c = conn.cursor()
    c.execute('SELECT * FROM invoices ORDER BY data DESC')
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def patch_invoices_with_missing_fields():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE invoices SET totale = importo + (importo * iva / 100) WHERE totale IS NULL OR totale = ''")
    c.execute("UPDATE invoices SET email_cliente = '' WHERE email_cliente IS NULL")
    conn.commit()
    conn.close()
