import os
import zipfile
import tempfile
import shutil
import xml.etree.ElementTree as ET
import pytest
import streamlit as st
from utils import db

# Saltiamo il test se mancano le dipendenze principali
pytest.importorskip("streamlit")
pytest.importorskip("reportlab")

from utils.pdf_generator import generate_invoice_pdf
from utils.fatturapa_generator import generate_fattura_xml

@pytest.fixture
def temp_workdir(monkeypatch):
    """Crea una dir temporanea per PDF/XML e la rimuove alla fine."""
    tmpdir = tempfile.mkdtemp()
    cwd = os.getcwd()
    os.chdir(tmpdir)
    try:
        yield tmpdir
    finally:
        os.chdir(cwd)
        shutil.rmtree(tmpdir)

def test_generate_pdf_and_xml(temp_db, temp_workdir, monkeypatch):
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
        "id": 1,
        "numero_fattura": 1,
        "anno": 2024,
        "cliente": "Cliente Test",
        "descrizione": "Servizio test",
        "importo": 100.0,
        "data": "2024-05-01",
        "iva": 22.0,
        "totale": 122.0,
        "email": "c@example.com"
    }

    # Genera PDF
    pdf_path = generate_invoice_pdf(fattura)
    assert os.path.exists(pdf_path)
    assert pdf_path.endswith(".pdf")
    assert os.path.getsize(pdf_path) > 0

    # Genera XML
    xml_path = generate_fattura_xml(fattura)
    assert os.path.exists(xml_path)
    assert xml_path.endswith(".xml")
    assert os.path.getsize(xml_path) > 0

    # Parsing XML con gestione namespace
    tree = ET.parse(xml_path)
    root = tree.getroot()
    tag_name = root.tag.split("}")[-1]  # Rimuove eventuale namespace
    assert tag_name.lower().startswith("fattura"), f"Root XML non è 'Fattura...', ma '{tag_name}'"