from utils.fatturapa_generator import generate_fattura_xml
from utils.validator import validate_with_imports

fattura = {
    "numero_fattura": 6,
    "cliente": "Luca Bianchi",
    "descrizione": "Tour Catania",
    "importo": 150.0,
    "iva": 22.0,
    "totale": 183.0,
    "data": "2025-08-03"
}

xml_path = generate_fattura_xml(fattura)

# Validazione dopo generazione
success, msg = validate_with_imports(
    xml_path,
    "../utils/schemas/Schema_VFPA12_V1.2.3.xsd",
    "utils/schemas/xmldsig-core-schema.xsd"
)
print(msg)