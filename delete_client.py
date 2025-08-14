import sqlite3

def delete_client_and_invoices(db_path, client_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Mostra anteprima dati
    cursor.execute("SELECT email FROM users WHERE id = ?", (client_id,))
    client = cursor.fetchone()
    if not client:
        print(f"❌ Nessun cliente trovato con ID {client_id}")
        conn.close()
        return

    cursor.execute("SELECT id, totale, data FROM invoices WHERE user_id = ?", (client_id,))
    invoices = cursor.fetchall()

    print(f"\nCliente: {client[0]} (ID: {client_id})")
    print("Fatture associate:")
    if invoices:
        for inv in invoices:
            print(f" - ID fattura: {inv[0]}, Importo: {inv[1]}, Data: {inv[2]}")
    else:
        print("   Nessuna fattura associata.")

    # Conferma
    conferma = input("\nSei sicuro di voler ELIMINARE questo cliente e tutte le sue fatture? (s/n): ").lower()
    if conferma != 's':
        print("❌ Operazione annullata.")
        conn.close()
        return

    # Elimina fatture
    cursor.execute("DELETE FROM invoices WHERE user_id = ?", (client_id,))


    conn.commit()
    conn.close()

    print("✅ Fatture eliminate con successo.")

# Esempio di utilizzo
# Cambia 'database.db' con il percorso del tuo database
delete_client_and_invoices(
    r"C:\Users\ste_c\PycharmProjects\freelanceDashboard\data\fatture.db",
    1
)
