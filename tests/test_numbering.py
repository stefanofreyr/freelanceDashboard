import datetime
from utils import db

def test_invoice_numbering_resets_each_year(temp_db):
    # Crea un utente di test
    email = "numero@example.com"
    hashed_pw = "fakehash"
    uid = db.create_user(email, hashed_pw, "Numero Test")

    # Anni da testare
    anno1, anno2 = 2023, 2024

    # Inserisci due fatture in anni diversi, entrambe numero 1
    db.insert_invoice(
        1, "Cliente A", "Servizio anno 1", 100.0,
        f"{anno1}-01-01", 22.0, 122.0, "cA@example.com",
        utente=email, user_id=uid, anno=anno1
    )
    db.insert_invoice(
        1, "Cliente B", "Servizio anno 2", 200.0,
        f"{anno2}-01-01", 22.0, 244.0, "cB@example.com",
        utente=email, user_id=uid, anno=anno2
    )

    # Verifica che il prossimo numero in ciascun anno sia 2
    next_anno1 = db.get_next_invoice_number_for_year_by_user_id(uid, anno1)
    next_anno2 = db.get_next_invoice_number_for_year_by_user_id(uid, anno2)

    assert next_anno1 == 2, f"Atteso 2 per anno {anno1}, trovato {next_anno1}"
    assert next_anno2 == 2, f"Atteso 2 per anno {anno2}, trovato {next_anno2}"

    # Inserisci una nuova fattura anno2 e verifica incremento
    db.insert_invoice(
        next_anno2, "Cliente C", "Servizio anno 2 bis", 300.0,
        f"{anno2}-06-15", 22.0, 366.0, "cC@example.com",
        utente=email, user_id=uid, anno=anno2
    )
    next_after_insert = db.get_next_invoice_number_for_year_by_user_id(uid, anno2)
    assert next_after_insert == 3, f"Atteso 3 per anno {anno2} dopo inserimento, trovato {next_after_insert}"
