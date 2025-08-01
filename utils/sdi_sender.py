import smtplib
import os
from email.message import EmailMessage

def send_via_pec(recipient, subject, body, attachment_path):
    try:
        sender_email = os.getenv("PEC_EMAIL")
        sender_password = os.getenv("PEC_PASSWORD")
        smtp_server = "smtp.pec.it"  # Es. Aruba
        smtp_port = 465  # Porta standard per SSL

        msg = EmailMessage()
        msg["From"] = sender_email
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.set_content(body)

        # Aggiungi l'allegato XML
        with open(attachment_path, "rb") as f:
            file_data = f.read()
            file_name = os.path.basename(attachment_path)
        msg.add_attachment(file_data, maintype="application", subtype="xml", filename=file_name)

        # Invio PEC
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)

        return True
    except Exception as e:
        print("Errore PEC:", e)
        return False
