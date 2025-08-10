from utils import db
import sqlite3, os

def test_numbering_per_year(tmp_path, monkeypatch):
    # usa un DB temporaneo se hai reso il path configurabile;
    # altrimenti fai attenzione a non rompere il DB reale.
    # Qui ipotizziamo funzioni pure: sostituisci con le tue.
    email = "tester@example.com"
    anno = 2025
    n1 = db.get_next_invoice_number_for_year(email, anno)
    n2 = db.get_next_invoice_number_for_year(email, anno)
    assert n2 == n1 + 1
