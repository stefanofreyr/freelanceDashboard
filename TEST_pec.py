from utils.fatturapa_generator import generate_fattura_xml
from utils.sdi_sender import send_via_pec

# Genera XML
fattura = {
    "numero_fattura": 7,
    "cliente": "Giulia Verdi",
    "descrizione": "Tour Siracusa",
    "importo": 120.00,
    "iva": 22.0,
    "totale": 146.40,
    "data": "2025-08-04"
}
xml_path = generate_fattura_xml(fattura)

# Invia PEC
success, msg = send_via_pec(
    xml_path=xml_path,
    mittente_pec="f6a9c40b07e433",
    mittente_password="1fea2dfdc9b08e",
    provider="Mailtrap"
)
print(msg)
