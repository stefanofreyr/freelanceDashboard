import streamlit as st
import pytest
import types
from utils.email_utils import send_invoice_email

@pytest.mark.parametrize("recipient,subject,body", [
    ("destinatario@example.com", "Oggetto di Test", "Corpo email di test")
])
def test_send_invoice_email_mock(temp_db, monkeypatch, recipient, subject, body):
    # Mock secrets come oggetto semplice
    st.secrets = {
        "PEC_USER": "pec@example.com",
        "PEC_PASS": "password",
        "PEC_PROVIDER": "Aruba"
    }

    # Mock invio email → ritorna sempre True
    monkeypatch.setattr("utils.email_utils.send_invoice_email", lambda *a, **kw: True)

    fake_pdf = "fake_invoice.pdf"
    with open(fake_pdf, "wb") as f:
        f.write(b"%PDF-1.4 Fake PDF content")

    result = send_invoice_email(recipient, subject, body, fake_pdf)
    assert result is True
