import smtplib
from email.message import EmailMessage
from utils.email_utils import is_test_mode
import os

# Configurazioni SMTP predefinite per provider PEC principali
def get_smtp_config(provider: str):
    configs = {
        "Aruba": {"host": "smtp.pec.aruba.it", "port": 465, "use_ssl": True},
        "PosteCert": {"host": "postecert.poste.it", "port": 465, "use_ssl": True},
        "Legalmail": {"host": "smtps.legalmail.it", "port": 465, "use_ssl": True},
        "Mailtrap": {"host": "sandbox.smtp.mailtrap.io", "port": 587, "use_ssl": False}
    }
    return configs.get(provider)

# Invia PEC con allegato XML
# ritorna (success: bool, message: str)
def legacy_send_via_pec(
    xml_path: str,
    mittente_pec: str,
    mittente_password: str,
    provider: str,
    destinatario: str = "sdi01@pec.fatturapa.it",
    subject: str = "Invio Fattura Elettronica",
    body: str = "In allegato trovi la fattura elettronica in formato XML.",
):
    if is_test_mode():
        os.makedirs("logs", exist_ok=True)
        with open("logs/pec_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[TEST] SDI simulato | file={xml_path}\n")
        return True, "🧪 Modalità test: invio PEC simulato."

    config = get_smtp_config(provider)
    if not config:
        return False, f"Provider PEC '{provider}' non configurato."

    # Prepara il messaggio
    msg = EmailMessage()
    msg["From"] = mittente_pec
    msg["To"] = destinatario
    msg["Subject"] = subject
    msg.set_content(body)

    # Leggi e allega il file XML
    try:
        with open(xml_path, "rb") as f:
            xml_data = f.read()
        filename = xml_path.split("/")[-1]
        msg.add_attachment(
            xml_data,
            maintype="application",
            subtype="xml",
            filename=filename
        )
    except Exception as e:
        return False, f"Errore lettura XML: {e}"

    # Connessione SMTP
    try:
        if config["use_ssl"]:
            server = smtplib.SMTP_SSL(config["host"], config["port"])
        else:
            server = smtplib.SMTP(config["host"], config["port"])
            server.starttls()

        server.login(mittente_pec, mittente_password)
        server.send_message(msg)
        server.quit()
        return True, "Email PEC inviata con successo!"
    except Exception as e:
        return False, f"Errore invio PEC: {e}"


import smtplib
from email.message import EmailMessage
from utils.email_utils import is_test_mode
import os

def get_smtp_config(provider: str):
    return {
        "Aruba":     {"host": "smtp.pec.aruba.it",  "port": 465, "use_ssl": True},
        "PosteCert": {"host": "postecert.poste.it", "port": 465, "use_ssl": True},
        "Legalmail": {"host": "smtps.legalmail.it", "port": 465, "use_ssl": True},
        "Mailtrap":  {"host": "sandbox.smtp.mailtrap.io", "port": 587, "use_ssl": False},
    }.get(provider)

def send_via_pec(xml_path, mittente_pec, mittente_password, provider):
    if is_test_mode():
        os.makedirs("logs", exist_ok=True)
        with open("logs/pec_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[TEST] SDI simulato | file={xml_path} | mittente={mittente_pec}\n")
        return True, "🧪 Modalità test: invio PEC simulato."

    config = get_smtp_config(provider)
    if not config:
        return False, f"Provider PEC non supportato: {provider}"
    if not os.path.exists(xml_path):
        return False, f"File XML non trovato: {xml_path}"

    msg = EmailMessage()
    msg["Subject"] = "Invio FatturaPA"
    msg["From"] = mittente_pec
    msg["To"] = "sdi01@pec.fatturapa.it"  # placeholder
    with open(xml_path, "rb") as fp:
        msg.add_attachment(
            fp.read(),
            maintype="application",
            subtype="xml",
            filename=os.path.basename(xml_path),
        )

    try:
        if config["use_ssl"]:
            server = smtplib.SMTP_SSL(config["host"], config["port"])
        else:
            server = smtplib.SMTP(config["host"], config["port"])
            server.starttls()
        server.login(mittente_pec, mittente_password)
        server.send_message(msg)
        server.quit()
        return True, "Email PEC inviata con successo!"
    except Exception as e:
        return False, f"Errore invio PEC: {e}"
