import streamlit as st
from utils import db
from utils.fatturapa_generator import generate_fattura_xml
import xml.etree.ElementTree as ET

def test_generate_xml(monkeypatch):
    # Mock session e secrets
    st.session_state["user"] = {"email": "test@example.com"}
    st.secrets = {
        "PEC_USER": "pec@example.com",
        "PEC_PASS": "password",
        "PEC_PROVIDER": "Aruba"
    }
    # Mock settings
    monkeypatch.setattr("utils.db.get_settings", lambda email: {"iva_default": 22.0})

    fattura = {
        "numero_fattura": 1,
        "data": "2025-08-10",
        "cliente": "ACME",
        "descrizione": "Servizio",
        "importo": 100.0,
        "iva": 22.0,
        "totale": 122.0,
        "email": "client@example.com",
        "utente": "tester@example.com"
    }

    path = generate_fattura_xml(fattura)
    assert path.endswith(".xml")

    # Parsing XML con gestione namespace
    tree = ET.parse(path)
    root = tree.getroot()
    tag_name = root.tag.split("}")[-1]  # Rimuove eventuale namespace
    assert tag_name.lower().startswith("fattura"), f"Root XML non è 'Fattura...', ma '{tag_name}'"
