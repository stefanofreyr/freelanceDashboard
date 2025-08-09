import streamlit as st
import datetime
import os
import smtplib
from email.mime.text import MIMEText

def show():
    st.title("💬 Feedback")

    st.write("Hai suggerimenti o segnalazioni? Lascia qui il tuo feedback.")

    with st.form("feedback_form"):
        nome = st.text_input("Il tuo nome (facoltativo)")
        email = st.text_input("Email (facoltativa)")
        testo = st.text_area("Il tuo feedback")
        submitted = st.form_submit_button("📩 Invia")

        if submitted:
            if testo.strip():
                # === 1. Salvataggio locale ===
                os.makedirs("feedback", exist_ok=True)
                filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S.txt")
                path = os.path.join("feedback", filename)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(f"Nome: {nome}\nEmail: {email}\n\nTesto:\n{testo}\n")

                # === 2. Invio email ===
                try:
                    send_feedback_email(nome, email, testo)
                    st.success("✅ Grazie! Il tuo feedback è stato salvato e inviato.")
                except Exception as e:
                    st.warning(f"⚠️ Feedback salvato in locale ma invio email fallito: {e}")

            else:
                st.error("❌ Scrivi almeno qualche parola di feedback.")


def send_feedback_email(nome, email, testo):
    """
    Invia il feedback via email usando le credenziali definite in .streamlit/secrets.toml
    """
    smtp_server = st.secrets.get("SMTP_SERVER")
    smtp_port = int(st.secrets.get("SMTP_PORT", 587))
    smtp_user = st.secrets.get("SMTP_USER")
    smtp_pass = st.secrets.get("SMTP_PASS")
    destinatario = st.secrets.get("FEEDBACK_RECIPIENT")  # il tuo indirizzo

    if not all([smtp_server, smtp_user, smtp_pass, destinatario]):
        raise RuntimeError("Config SMTP incompleta nei secrets.")

    subject = "Nuovo feedback dall'app FAi"
    body = f"Nome: {nome}\nEmail: {email}\n\nTesto:\n{testo}"

    msg = MIMEText(body, "plain", "utf-8")
    msg["From"] = smtp_user
    msg["To"] = destinatario
    msg["Subject"] = subject

    with smtplib.SMTP(smtp_server, smtp_port, timeout=15) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
