import yagmail
import os

# Usa variabili d'ambiente per sicurezza!
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

def send_invoice_email(to_email, subject, body, attachment_path):
    try:
        yag = yagmail.SMTP(SENDER_EMAIL, SENDER_PASSWORD)
        yag.send(
            to=to_email,
            subject=subject,
            contents=body,
            attachments=attachment_path
        )
        return True
    except Exception as e:
        print("Errore invio email:", e)
        return False
