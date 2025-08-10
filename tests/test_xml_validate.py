from utils.fatturapa_generator import generate_fattura_xml
import os

def test_generate_xml(tmp_path):
    fattura = {
        "numero_fattura": 1, "data": "2025-08-10", "cliente": "ACME",
        "descrizione": "Servizio", "importo": 100.0, "iva": 22.0,
        "totale": 122.0, "email": "client@example.com", "utente": "tester@example.com"
    }
    path = generate_fattura_xml(fattura)
    assert os.path.exists(path)
