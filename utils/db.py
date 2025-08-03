# utils/db.py
import sqlite3
import os
from datetime import date
from collections import defaultdict

DB_NAME = "data/fatture.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # TABELLA FATTURE
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

    # TABELLA CLIENTI
    c.execute('''
            CREATE TABLE IF NOT EXISTS clienti (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                email TEXT,
                piva TEXT,
                indirizzo TEXT,
                pec TEXT,
                telefono TEXT
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


def inserisci_cliente(nome, email, piva, indirizzo, pec, telefono):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO clienti (nome, email, piva, indirizzo, pec, telefono)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nome, email, piva, indirizzo, pec, telefono))
    conn.commit()
    conn.close()


def lista_clienti():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM clienti')
    rows = c.fetchall()
    conn.close()
    return [
        {
            'id': row[0],
            'nome': row[1],
            'email': row[2],
            'piva': row[3],
            'indirizzo': row[4],
            'pec': row[5],
            'telefono': row[6],
        } for row in rows
    ]


def lista_clienti_raggruppati():
    clienti = lista_clienti()
    raggruppati = defaultdict(list)
    for cliente in clienti:
        iniziale = cliente['nome'][0].upper()
        raggruppati[iniziale].append(cliente)
    # Ordina ogni sottolista per nome
    for iniziale in raggruppati:
        raggruppati[iniziale].sort(key=lambda x: x['nome'].lower())
    return dict(raggruppati)



def update_cliente(id_cliente, nome, email, piva, indirizzo, pec, telefono):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        UPDATE clienti SET nome=?, email=?, piva=?, indirizzo=?, pec=?, telefono=? WHERE id=?
    ''', (nome, email, piva, indirizzo, pec, telefono, id_cliente))
    conn.commit()
    conn.close()


def elimina_cliente(id_cliente):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM clienti WHERE id=?', (id_cliente,))
    conn.commit()
    conn.close()

