import streamlit as st
import smtplib
from email.mime.text import MIMEText
import tomllib  # Python 3.11+

# Carica secrets.toml manualmente (senza lanciare tutta l'app Streamlit)
with open(".streamlit/secrets.toml", "rb") as f:
    secrets = tomllib.load(f)

smtp_server = secrets.get("SMTP_SERVER")
smtp_port = int(secrets.get("SMTP_PORT", 587))
smtp_user = secrets.get("SMTP_USER")
smtp_pass = secrets.get("SMTP_PASS")
destinatario = secrets.get("FEEDBACK_RECIPIENT")

# Corpo della mail di test
subject = "Test invio email da FAi"
body = "Se stai leggendo questa mail, l'invio SMTP funziona correttamente."

msg = MIMEText(body, "plain", "utf-8")
msg["From"] = smtp_user
msg["To"] = destinatario
msg["Subject"] = subject

try:
    with smtplib.SMTP(smtp_server, smtp_port, timeout=15) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
    print(f"✅ Email inviata a {destinatario}")
except Exception as e:
    print(f"❌ Errore nell'invio: {e}")
