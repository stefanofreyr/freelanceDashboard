# utils/email_utils.py
# import yagmail  # Lasciato commentato per uso futuro
import streamlit as st
from utils import db
import os

def is_test_mode() -> bool:
    try:
        user = st.session_state.get("user") or {}
        email = user.get("email")
        s = db.get_settings(email) or {}
        return (s.get("test_mode", 1) == 1)
    except Exception:
        return True  # fallback sicuro


def send_invoice_email(destinatario, subject, body, allegato, email_mittente=None, password=None):
    try:
        if is_test_mode():
            os.makedirs("logs", exist_ok=True)
            with open("logs/email_log.txt", "a", encoding="utf-8") as f:
                f.write(f"[TEST] {destinatario} | {subject} | {allegato}\n")
            return True

        # --- qui il codice reale quando disattivi il test mode ---
        # yag = yagmail.SMTP(user=email_mittente, password=password)
        # yag.send(to=destinatario, subject=subject, contents=body, attachments=allegato)
        return True
    except Exception as e:
        print(e)
        return False