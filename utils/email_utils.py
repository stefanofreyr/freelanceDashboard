# utils/email_utils.py

# import yagmail  # Lasciato commentato per uso futuro

def send_invoice_email(destinatario, subject, body, allegato, email_mittente=None, password=None):
    try:
        # Codice reale disattivato per MVP:
        # yag = yagmail.SMTP(user=email_mittente, password=password)
        # yag.send(to=destinatario, subject=subject, contents=body, attachments=allegato)

        print(f"[FAKE EMAIL] A: {destinatario} | Oggetto: {subject}")
        print("Contenuto:", body)
        print("Allegato:", allegato)

        return True
    except Exception as e:
        print(f"[FAKE EMAIL] Errore: {e}")
        return False
